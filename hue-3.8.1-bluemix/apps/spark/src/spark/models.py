#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import re
import time

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from beeswax import data_export
from beeswax.design import hql_query
from beeswax import conf as beeswax_conf
from beeswax.models import QUERY_TYPES, HiveServerQueryHandle, QueryHistory, HiveServerQueryHistory
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config, QueryServerException
from beeswax.views import _parse_out_hadoop_jobs

from spark.job_server_api import get_api as get_spark_api
from spark.data_export import download as spark_download


LOG = logging.getLogger(__name__)


# To move to Editor API
class SessionExpired(Exception):
  pass


class QueryExpired(Exception):
  pass


class QueryError(Exception):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return force_unicode(str(self.message))


class Notebook():

  def __init__(self, document=None):
    self.document = None

    if document is not None:
      self.data = document.data
      self.document = document
    else:
      self.data = json.dumps({
          'name': 'My Notebook',
          'description': '',
          'snippets': []
      })

  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)

  def get_data(self):
    _data = json.loads(self.data)

    if self.document is not None:
      _data['id'] = self.document.id

    return _data

  def get_str(self):
    return '\n\n'.join([snippet['statement_raw'] for snippet in self.get_data()['snippets']])


def get_api(user, snippet):
  if snippet['type'] in ('hive', 'impala', 'spark-sql'):
    return HS2Api(user)
  elif snippet['type'] in ('jar', 'py'):
    return SparkBatchApi(user)
  elif snippet['type'] == 'text':
    return TextApi(user)
  else:
    return SparkApi(user)


def _get_snippet_session(notebook, snippet):
  return [session for session in notebook['sessions'] if session['type'] == snippet['type']][0]


class TextApi():

  def __init__(self, user):
    self.user = user

  def create_session(self, lang, properties=None):
    return {
        'type': lang,
        'id': None
    }


# HS2

def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except QueryServerException, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise QueryError(message)
  return decorator


class HS2Api():

  def __init__(self, user):
    self.user = user

  def _get_handle(self, snippet):
    snippet['result']['handle']['secret'], snippet['result']['handle']['guid'] = HiveServerQueryHandle.get_decoded(snippet['result']['handle']['secret'], snippet['result']['handle']['guid'])
    return HiveServerQueryHandle(**snippet['result']['handle'])

  def _get_db(self, snippet):
    if snippet['type'] == 'hive':
      name = 'beeswax'
    elif snippet['type'] == 'impala':
      name = 'impala'
    else:
      name = 'spark-sql'

    return dbms.get(self.user, query_server=get_query_server_config(name=name))

  def create_session(self, lang, properties=None):
    return {
        'type': lang,
        'id': None # Real one at some point
    }

  def execute(self, notebook, snippet):
    db = self._get_db(snippet)
    query = hql_query(snippet['statement'], QUERY_TYPES[0])

    try:
      handle = db.client.query(query)
    except QueryServerException, ex:
      raise QueryError(ex.message)

    # All good
    server_id, server_guid  = handle.get()
    return {
        'secret': server_id,
        'guid': server_guid,
        'operation_type': handle.operation_type,
        'has_result_set': handle.has_result_set,
        'modified_row_count': handle.modified_row_count,
        'log_context': handle.log_context
    }

  @query_error_handler
  def check_status(self, notebook, snippet):
    response = {}
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    operation = db.get_operation_status(handle)
    status = HiveServerQueryHistory.STATE_MAP[operation.operationState]

    if status.index in (QueryHistory.STATE.failed.index, QueryHistory.STATE.expired.index):
      raise QueryError(operation.errorMessage)

    response['status'] = 'running' if status.index in (QueryHistory.STATE.running.index, QueryHistory.STATE.submitted.index) else 'available'

    return response

  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    results = db.fetch(handle, start_over=start_over, rows=rows)

    # No escaping...
    return {
        'has_more': results.has_more,
        'data': list(results.rows()),
        'meta': [{
          'name': column.name,
          'type': column.type,
          'comment': column.comment
        } for column in results.data_table.cols()],
        'type': 'table'
    }

  @query_error_handler
  def fetch_result_metadata(self):
    pass

  @query_error_handler
  def cancel(self, notebook, snippet):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    db.cancel_operation(handle)
    return {'status': 0}

  @query_error_handler
  def get_log(self, snippet, startFrom=None, size=None):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    return db.get_log(handle, start_over=startFrom == 0)

  def download(self, notebook, snippet, format):
    try:
      db = self._get_db(snippet)
      handle = self._get_handle(snippet)
      return data_export.download(handle, format, db)
    except Exception, e:
      LOG.exception('error downloading notebook')

      if not hasattr(e, 'message') or not e.message:
        message = e
      else:
        message = e.message
      raise PopupException(message, detail='')

  def _progress(self, snippet, logs):
    if snippet['type'] == 'hive':
      match = re.search('Total jobs = (\d+)', logs, re.MULTILINE)
      total = (int(match.group(1)) if match else 1) * 2

      started = logs.count('Starting Job')
      ended = logs.count('Ended Job')

      return int((started + ended) * 100 / total)
    elif snippet['type'] == 'impala':
      match = re.search('(\d+)% Complete', logs, re.MULTILINE)
      return int(match.group(1)) if match else 0
    else:
      return 50

  @query_error_handler
  def close(self, snippet):
    if snippet['type'] == 'impala':
      from impala import conf as impala_conf

    if (snippet['type'] == 'hive' and beeswax_conf.CLOSE_QUERIES.get()) or (snippet['type'] == 'impala' and impala_conf.CLOSE_QUERIES.get()):
      db = self._get_db(snippet)

      handle = self._get_handle(snippet)
      db.close_operation(handle)
      return {'status': 0}
    else:
      return {'status': -1}  # skipped

  def _get_jobs(self, log):
    return _parse_out_hadoop_jobs(log)


# Spark


class SparkApi():

  def __init__(self, user):
    self.user = user

  def create_session(self, lang='scala', properties=None):
    if properties is None:
      settings = { 
          'executor_cores': 1, # Some props only in YARN mode
          'executor_count': 1,
          'executor_memory': '1G',
          'driver_cores': 1,
          'driver_memory': '1G'
      }

    api = get_spark_api(self.user)
    print 'TODO: we should use the settings %s for creating the new sessions' % settings
    response = api.create_session(kind=lang)

    status = api.get_session(response['id'])
    count = 0

    while status['state'] == 'starting' and count < 120:
      status = api.get_session(response['id'])
      count += 1
      time.sleep(1)

    if status['state'] != 'idle':
      raise QueryError('\n'.join(status['log']))

    return {
        'type': lang,
        'id': response['id'],
        'properties': settings
    }

  def execute(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)

    try:
      response = api.submit_statement(session['id'], snippet['statement'])
      return {
          'id': response['id'],
          'has_result_set': True,
      }
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message or 'connection refused' in message or 'session is in state busy' in message:
        raise SessionExpired(e)
      else:
        raise e

  def check_status(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
      return {
          'status': response['state'],
      }
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

  def fetch_result(self, notebook, snippet, rows, start_over):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

    content = response['output']

    if content['status'] == 'ok':
      data = content['data']

      try:
        table = data['application/vnd.livy.table.v1+json']
      except KeyError:
        data = [[data['text/plain']]]
        meta = [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}]
        type = 'text'
      else:
        data = table['data']
        headers = table['headers']
        meta = [{'name': h['name'], 'type': h['type'], 'comment': ''} for h in headers]
        type = 'table'

      # Non start_over not supported
      if not start_over:
        data = []

      return {
          'data': data,
          'meta': meta,
          'type': type
      }
    elif content['status'] == 'error':
      tb = content.get('traceback', None)

      if tb is None:
        msg = content.get('ename', 'unknown error')

        evalue = content.get('evalue')
        if evalue is not None:
          msg = '%s: %s' % (msg, evalue)
      else:
        msg = ''.join(tb)

      raise QueryError(msg)

  def download(self, notebook, snippet, format):
    try:
      api = get_spark_api(self.user)
      session = _get_snippet_session(notebook, snippet)
      cell = snippet['result']['handle']['id']

      return spark_download(api, session['id'], cell, format)
    except Exception, e:
      raise PopupException(e)

  def cancel(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    response = api.cancel(session['id'])

    return {'status': 0}

  def get_log(self, snippet, startFrom=0, size=None):
    return 'Not available'

  def _progress(self, snippet, logs):
    return 50

  def close(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)

    if session['id'] is not None:
      api.close(session['id'])
      return {
        'session': session['id'],
        'status': 0
      }
    else:
      return {'status': -1}

  def _get_jobs(self, log):
    return []


class SparkBatchApi():

  def __init__(self, user):
    self.user = user

  def create_session(self, lang, properties=None):
    return {
        'type': lang,
        'id': None
    }

  def execute(self, notebook, snippet):
    api = get_spark_api(self.user)

    properties = {
        'file': snippet['properties'].get('app_jar'),
        'className': snippet['properties'].get('class'),
        'args': [arg['value'] for arg in snippet['properties'].get('arguments')],
        'pyFiles': snippet['properties'].get('py_file'),
        # files
        # driverMemory
        # driverCores
        # executorMemory
        # executorCores
        # archives
    }

    response = api.submit_batch(properties)
    return {
        'id': response['id'],
        'has_result_set': True,
    }

  def check_status(self, notebook, snippet):
    api = get_spark_api(self.user)

    state = api.get_batch_status(snippet['result']['handle']['id'])
    return {
        'status': state,
    }

  def get_log(self, snippet, startFrom=0, size=None):
    api = get_spark_api(self.user)

    return api.get_batch_log(snippet['result']['handle']['id'], startFrom=startFrom, size=size)

  def close(self, snippet):
    api = get_spark_api(self.user)

    session_id = snippet['result']['handle']['id']
    if session_id is not None:
      api.close_batch(session_id)
      return {
        'session': session_id,
        'status': 0
      }
    else:
      return {'status': -1}  # skipped

  def cancel(self, notebook, snippet):
    # Batch jobs do not support interruption, so close session instead.
    return self.close(snippet)

  def _progress(self, snippet, logs):
    return 50

  def _get_jobs(self, log):
    return []
