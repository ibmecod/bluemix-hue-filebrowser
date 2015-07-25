#!/usr/bin/env python
## -*- coding: utf-8 -*-
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


import logging

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_permission, add_to_group, reformat_json, reformat_xml


from oozie.models2 import Job, Workflow, find_dollar_variables, find_dollar_braced_variables


LOG = logging.getLogger(__name__)


class TestEditor():

  def setUp(self):
    self.wf = Workflow()


  def test_parsing(self):
    assert_equal(['input', 'LIMIT', 'out'], find_dollar_variables("""
data = '$input';
$out = LIMIT data $LIMIT; -- ${nah}
$output = STORE "$out";
    """))

    assert_equal(['max_salary', 'limit'], find_dollar_variables("""
SELECT sample_07.description, sample_07.salary
FROM
  sample_07
WHERE
( sample_07.salary > $max_salary)
ORDER BY sample_07.salary DESC
LIMIT $limit"""))


  def test_hive_script_parsing(self):
    assert_equal(['field', 'tablename', 'LIMIT'], find_dollar_braced_variables("""
    SELECT ${field}
    FROM ${hivevar:tablename}
    LIMIT ${hiveconf:LIMIT}
    """))


  def test_workflow_gen_xml(self):
    assert_equal([
        u'<workflow-app', u'name="My_Workflow"', u'xmlns="uri:oozie:workflow:0.5">', u'<start', u'to="End"/>', u'<kill', u'name="Kill">', u'<message>Action', u'failed,',
        u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>', u'</kill>', u'<end', u'name="End"/>', u'</workflow-app>'],
        self.wf.to_xml({'output': '/path'}).split()
    )

  def test_workflow_map_reduce_gen_xml(self):
    wf = Workflow(data="{\"layout\": [{\"oozieRows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}], \"rows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}], \"oozieEndRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, \"oozieKillRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}, \"enableOozieDropOnAfter\": true, \"oozieStartRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, \"klass\": \"card card-home card-column span12\", \"enableOozieDropOnBefore\": true, \"drops\": [\"temp\"], \"id\": \"0c1908e7-0096-46e7-a16b-b17b1142a730\", \"size\": 12}], \"workflow\": {\"properties\": {\"job_xml\": \"\", \"description\": \"\", \"wf1_id\": null, \"sla_enabled\": false, \"deployment_dir\": \"/user/hue/oozie/workspaces/hue-oozie-1430228904.58\", \"schema_version\": \"uri:oozie:workflow:0.5\", \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}], \"show_arrows\": true, \"parameters\": [{\"name\": \"oozie.use.system.libpath\", \"value\": true}], \"properties\": []}, \"name\": \"My Workflow\", \"versions\": [\"uri:oozie:workflow:0.4\", \"uri:oozie:workflow:0.4.5\", \"uri:oozie:workflow:0.5\"], \"isDirty\": true, \"movedNode\": null, \"linkMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": [\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"], \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": [], \"3f107997-04cc-8733-60a9-a4bb62cebffc\": [\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"17c9c895-5a16-7443-bb81-f34b30b21548\": []}, \"nodeIds\": [\"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"nodes\": [{\"properties\": {}, \"name\": \"Start\", \"children\": [{\"to\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"}], \"actionParametersFetched\": false, \"type\": \"start-widget\", \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"actionParameters\": []}, {\"properties\": {}, \"name\": \"End\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"end-widget\", \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"actionParameters\": []}, {\"properties\": {\"message\": \"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\"}, \"name\": \"Kill\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"kill-widget\", \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"actionParameters\": []}, {\"properties\": {\"retry_max\": [{\"value\": \"5\"}], \"files\": [], \"job_xml\": \"\", \"jar_path\": \"my_jar\", \"job_properties\": [{\"name\": \"prop_1_name\", \"value\": \"prop_1_value\"}], \"archives\": [], \"prepares\": [], \"credentials\": [], \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}]}, \"name\": \"mapreduce-0cf2\", \"children\": [{\"to\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"}, {\"error\": \"17c9c895-5a16-7443-bb81-f34b30b21548\"}], \"actionParametersFetched\": false, \"type\": \"mapreduce-widget\", \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"actionParameters\": []}], \"id\": 50019, \"nodeNamesMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": \"mapreduce-0cf2\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": \"End\", \"3f107997-04cc-8733-60a9-a4bb62cebffc\": \"Start\", \"17c9c895-5a16-7443-bb81-f34b30b21548\": \"Kill\"}, \"uuid\": \"084f4d4c-00f1-62d2-e27e-e153c1f9acfb\"}}")

    assert_equal([
        u'<workflow-app', u'name="My_Workflow"', u'xmlns="uri:oozie:workflow:0.5">',
        u'<start', u'to="mapreduce-0cf2"/>',
        u'<kill', u'name="Kill">', u'<message>Action', u'failed,', u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>', u'</kill>',
        u'<action', u'name="mapreduce-0cf2"', 'retry-max="5">',
        u'<map-reduce>',
        u'<job-tracker>${jobTracker}</job-tracker>',
        u'<name-node>${nameNode}</name-node>',
        u'<configuration>',
        u'<property>',
        u'<name>prop_1_name</name>',
        u'<value>prop_1_value</value>',
        u'</property>',
        u'</configuration>',
        u'</map-reduce>',
        u'<ok', u'to="End"/>',
        u'<error', u'to="Kill"/>',
        u'</action>',
        u'<end', u'name="End"/>',
        u'</workflow-app>'
        ],
        wf.to_xml({'output': '/path'}).split()
    )

  def test_job_validate_xml_name(self):
    job = Workflow()

    job.update_name('a')
    assert_equal('a', job.validated_name)

    job.update_name('aa')
    assert_equal('aa', job.validated_name)

    job.update_name('%a')
    assert_equal('_a', job.validated_name)

    job.update_name('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaz')
    assert_equal(len('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), len(job.validated_name))

    job.update_name('My <...> 1st W$rkflow [With] (Bad) letter$')
    assert_equal('My_______1st_W$rkflow__With___Bad__lette', job.validated_name)


class TestUtils():

  def setUp(self):
    self.wf = Workflow()

  def test_gen_workflow_data_from_xml(self):
    f = open('apps/oozie/src/oozie/test_data/xslt2/test-workflow.xml')
    self.wf.definition = f.read()
    node_list = "[{u'node_type': u'start', u'ok_to': u'fork-68d4', u'name': u''}, {u'node_type': u'kill', u'ok_to': u'', u'name': u'Kill'}, {u'path2': u'shell-0f44', u'node_type': u'fork', u'ok_to': u'', u'name': u'fork-68d4', u'path1': u'subworkflow-a13f'}, {u'node_type': u'join', u'ok_to': u'End', u'name': u'join-775e'}, {u'node_type': u'end', u'ok_to': u'', u'name': u'End'}, {u'node_type': u'sub-workflow', u'ok_to': u'join-775e', u'name': u'subworkflow-a13f', u'job_properties': [{u'name': u'hue-id-w', u'value': u'50001'}], u'error_to': u'Kill'}, {u'shell': {u'command': u'ls'}, u'node_type': u'shell', u'ok_to': u'join-775e', u'name': u'shell-0f44', u'error_to': u'Kill'}, {}]"
    assert_equal(node_list, str(Workflow.gen_workflow_data_from_xml('admin', self.wf)))


#  def test_workflow_name(self):
#    try:
#      workflow_dict = WORKFLOW_DICT.copy()
#      workflow_count = Document.objects.available_docs(Workflow, self.user).count()
#
#      workflow_dict['name'][0] = 'bad workflow name'
#      response = self.c.post(reverse('oozie:create_workflow'), workflow_dict, follow=True)
#      assert_equal(200, response.status_code)
#      assert_equal(workflow_count, Document.objects.available_docs(Workflow, self.user).count(), response)
#
#      workflow_dict['name'][0] = 'good-workflow-name'
#      response = self.c.post(reverse('oozie:create_workflow'), workflow_dict, follow=True)
#      assert_equal(200, response.status_code)
#      assert_equal(workflow_count + 1, Document.objects.available_docs(Workflow, self.user).count(), response)
#    finally:
#      name = 'bad workflow name'
#      if Workflow.objects.filter(name=name).exists():
#        Node.objects.filter(workflow__name=name).delete()
#        Workflow.objects.filter(name=name).delete()
#      name = 'good-workflow-name'
#      if Workflow.objects.filter(name=name).exists():
#        Node.objects.filter(workflow__name=name).delete()
#        Workflow.objects.filter(name=name).delete()
#
#
#  def test_find_parameters(self):
#    data = json.dumps({'sla': [
#        {'key': 'enabled', 'value': True},
#        {'key': 'nominal-time', 'value': '${time}'},]}
#    )
#    jobs = [Job(name="$a"),
#            Job(name="foo ${b} $$"),
#            Job(name="${foo}", description="xxx ${food}", data=data)]
#
#    result = [find_parameters(job, ['name', 'description', 'sla']) for job in jobs]
#    assert_equal(set(["b", "foo", "food", "time"]), reduce(lambda x, y: x | set(y), result, set()))
#
#
#  def test_find_all_parameters(self):
#    self.wf.data = json.dumps({'sla': [
#        {'key': 'enabled', 'value': False},
#        {'key': 'nominal-time', 'value': '${time}'},]}
#    )
#    assert_equal([{'name': u'output', 'value': u''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}],
#                 self.wf.find_all_parameters())
#
#    self.wf.data = json.dumps({'sla': [
#        {'key': 'enabled', 'value': True},
#        {'key': 'nominal-time', 'value': '${time}'},]}
#    )
#    assert_equal([{'name': u'output', 'value': u''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}, {'name': u'time', 'value': u''}],
#                 self.wf.find_all_parameters())
#
#
#  def test_workflow_has_cycle(self):
#    action1 = Node.objects.get(workflow=self.wf, name='action-name-1')
#    action3 = Node.objects.get(workflow=self.wf, name='action-name-3')
#
#    assert_false(self.wf.has_cycle())
#
#    ok = action3.get_link('ok')
#    ok.child = action1
#    ok.save()
#
#    assert_true(self.wf.has_cycle())
#
#
#  def test_workflow_gen_xml(self):
#    assert_equal(
#        '<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">\n'
#        '    <global>\n'
#        '        <job-xml>jobconf.xml</job-xml>\n'
#        '        <configuration>\n'
#        '            <property>\n'
#        '                <name>sleep-all</name>\n'
#        '                <value>${SLEEP}</value>\n'
#        '            </property>\n'
#        '         </configuration>\n'
#        '    </global>\n'
#        '    <start to="action-name-1"/>\n'
#        '    <action name="action-name-1">\n'
#        '        <map-reduce>\n'
#        '           <job-tracker>${jobTracker}</job-tracker>\n'
#        '            <name-node>${nameNode}</name-node>\n'
#        '            <prepare>\n'
#        '                <delete path="${nameNode}${output}"/>\n'
#        '                <mkdir path="${nameNode}/test"/>\n'
#        '            </prepare>\n'
#        '            <configuration>\n'
#        '                <property>\n'
#        '                    <name>sleep</name>\n'
#        '                    <value>${SLEEP}</value>\n'
#        '                </property>\n'
#        '            </configuration>\n'
#        '        </map-reduce>\n'
#        '        <ok to="action-name-2"/>\n'
#        '        <error to="kill"/>\n'
#        '    </action>\n'
#        '    <action name="action-name-2">\n'
#        '        <map-reduce>\n'
#        '            <job-tracker>${jobTracker}</job-tracker>\n'
#        '            <name-node>${nameNode}</name-node>\n'
#        '            <prepare>\n'
#        '                <delete path="${nameNode}${output}"/>\n'
#        '                <mkdir path="${nameNode}/test"/>\n'
#        '            </prepare>\n'
#        '            <configuration>\n'
#        '                <property>\n'
#        '                    <name>sleep</name>\n'
#        '                    <value>${SLEEP}</value>\n'
#        '                </property>\n'
#        '            </configuration>\n'
#        '        </map-reduce>\n'
#        '        <ok to="action-name-3"/>\n'
#        '        <error to="kill"/>\n'
#        '    </action>\n'
#        '    <action name="action-name-3">\n'
#        '        <map-reduce>\n'
#        '            <job-tracker>${jobTracker}</job-tracker>\n'
#        '            <name-node>${nameNode}</name-node>\n'
#        '            <prepare>\n'
#        '                <delete path="${nameNode}${output}"/>\n'
#        '                <mkdir path="${nameNode}/test"/>\n'
#        '            </prepare>\n'
#        '            <configuration>\n'
#        '                <property>\n'
#        '                    <name>sleep</name>\n'
#        '                    <value>${SLEEP}</value>\n'
#        '                </property>\n'
#        '            </configuration>\n'
#        '        </map-reduce>\n'
#        '        <ok to="end"/>\n'
#        '        <error to="kill"/>\n'
#        '    </action>\n'
#        '    <kill name="kill">\n'
#        '        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>\n'
#        '    </kill>\n'
#        '    <end name="end"/>\n'
#        '</workflow-app>'.split(), self.wf.to_xml({'output': '/path'}).split())
#
#
#  def test_workflow_java_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'java', [self.wf.start], {
#        u'name': 'MyTeragen',
#        "description":"Generate N number of records",
#        "main_class":"org.apache.hadoop.examples.terasort.TeraGen",
#        "args":"1000 ${output_dir}/teragen",
#        "files":'["my_file","my_file2"]',
#        "job_xml":"",
#        "java_opts":"-Dexample-property=natty",
#        "jar_path":"/user/hue/oozie/workspaces/lib/hadoop-examples.jar",
#        "prepares":'[{"value":"/test","type":"mkdir"}]',
#        "archives":'[{"dummy":"","name":"my_archive"},{"dummy":"","name":"my_archive2"}]',
#        "capture_output": "on",
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml({'output_dir': '/path'})
#
#    assert_true("""
#    <action name="MyTeragen">
#        <java>
#            <job-tracker>${jobTracker}</job-tracker>
#            <name-node>${nameNode}</name-node>
#            <prepare>
#                  <mkdir path="${nameNode}/test"/>
#            </prepare>
#            <main-class>org.apache.hadoop.examples.terasort.TeraGen</main-class>
#            <java-opts>-Dexample-property=natty</java-opts>
#            <arg>1000</arg>
#            <arg>${output_dir}/teragen</arg>
#            <file>my_file#my_file</file>
#            <file>my_file2#my_file2</file>
#            <archive>my_archive#my_archive</archive>
#            <archive>my_archive2#my_archive2</archive>
#            <capture-output/>
#        </java>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>""" in xml, xml)
#
#
#  def test_workflow_streaming_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'streaming', [self.wf.start], {
#        u'name': 'MyStreaming',
#        "description": "Generate N number of records",
#        "main_class": "org.apache.hadoop.examples.terasort.TeraGen",
#        "mapper": "MyMapper",
#        "reducer": "MyReducer",
#        "files": '["my_file"]',
#        "archives":'[{"dummy":"","name":"my_archive"}]',
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#    <action name="MyStreaming">
#        <map-reduce>
#            <job-tracker>${jobTracker}</job-tracker>
#            <name-node>${nameNode}</name-node>
#            <streaming>
#                <mapper>MyMapper</mapper>
#                <reducer>MyReducer</reducer>
#            </streaming>
#            <file>my_file#my_file</file>
#            <archive>my_archive#my_archive</archive>
#        </map-reduce>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>""" in xml, xml)
#
#
#  def test_workflow_shell_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'shell', [self.wf.start], {
#        u'job_xml': 'my-job.xml',
#        u'files': '["hello.py"]',
#        u'name': 'Shell',
#        u'job_properties': '[]',
#        u'capture_output': 'on',
#        u'command': 'hello.py',
#        u'archives': '[]',
#        u'prepares': '[]',
#        u'params': '[{"value":"World!","type":"argument"}]',
#        u'description': 'Execute a Python script printing its arguments'
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#        <shell xmlns="uri:oozie:shell-action:0.1">
#            <job-tracker>${jobTracker}</job-tracker>
#            <name-node>${nameNode}</name-node>
#              <job-xml>my-job.xml</job-xml>
#            <exec>hello.py</exec>
#              <argument>World!</argument>
#            <file>hello.py#hello.py</file>
#              <capture-output/>
#        </shell>""" in xml, xml)
#
#    action1.capture_output = False
#    action1.save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#        <shell xmlns="uri:oozie:shell-action:0.1">
#            <job-tracker>${jobTracker}</job-tracker>
#            <name-node>${nameNode}</name-node>
#              <job-xml>my-job.xml</job-xml>
#            <exec>hello.py</exec>
#              <argument>World!</argument>
#            <file>hello.py#hello.py</file>
#        </shell>""" in xml, xml)
#
#
#  def test_workflow_fs_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'fs', [self.wf.start], {
#        u'name': 'MyFs',
#        u'description': 'Execute a Fs action that manage files',
#        u'deletes': '[{"name":"/to/delete"},{"name":"to/delete2"}]',
#        u'mkdirs': '[{"name":"/to/mkdir"},{"name":"${mkdir2}"}]',
#        u'moves': '[{"source":"/to/move/source","destination":"/to/move/destination"},{"source":"/to/move/source2","destination":"/to/move/destination2"}]',
#        u'chmods': '[{"path":"/to/chmod","recursive":true,"permissions":"-rwxrw-rw-"},{"path":"/to/chmod2","recursive":false,"permissions":"755"}]',
#        u'touchzs': '[{"name":"/to/touchz"},{"name":"/to/touchz2"}]'
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml({'mkdir2': '/path'})
#
#    assert_true("""
#    <action name="MyFs">
#        <fs>
#              <delete path='${nameNode}/to/delete'/>
#              <delete path='${nameNode}/user/${wf:user()}/to/delete2'/>
#              <mkdir path='${nameNode}/to/mkdir'/>
#              <mkdir path='${nameNode}${mkdir2}'/>
#              <move source='${nameNode}/to/move/source' target='${nameNode}/to/move/destination'/>
#              <move source='${nameNode}/to/move/source2' target='${nameNode}/to/move/destination2'/>
#              <chmod path='${nameNode}/to/chmod' permissions='-rwxrw-rw-' dir-files='true'/>
#              <chmod path='${nameNode}/to/chmod2' permissions='755' dir-files='false'/>
#              <touchz path='${nameNode}/to/touchz'/>
#              <touchz path='${nameNode}/to/touchz2'/>
#        </fs>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>""" in xml, xml)
#
#
#  def test_workflow_email_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'email', [self.wf.start], {
#        u'name': 'MyEmail',
#        u'description': 'Execute an Email action',
#        u'to': 'hue@hue.org,django@python.org',
#        u'cc': '',
#        u'subject': 'My subject',
#        u'body': 'My body'
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#    <action name="MyEmail">
#        <email xmlns="uri:oozie:email-action:0.1">
#            <to>hue@hue.org,django@python.org</to>
#            <subject>My subject</subject>
#            <body>My body</body>
#        </email>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>""" in xml, xml)
#
#    action1.cc = 'lambda@python.org'
#    action1.save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#    <action name="MyEmail">
#        <email xmlns="uri:oozie:email-action:0.1">
#            <to>hue@hue.org,django@python.org</to>
#              <cc>lambda@python.org</cc>
#            <subject>My subject</subject>
#            <body>My body</body>
#        </email>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>""" in xml, xml)
#
#
#  def test_workflow_subworkflow_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    wf_dict = WORKFLOW_DICT.copy()
#    wf_dict['name'] = [u'wf-name-2']
#    wf2 = create_workflow(self.c, self.user, wf_dict)
#
#    action1 = add_node(self.wf, 'action-name-1', 'subworkflow', [self.wf.start], {
#        u'name': 'MySubworkflow',
#        u'description': 'Execute a subworkflow action',
#        u'sub_workflow': wf2,
#        u'propagate_configuration': True,
#        u'job_properties': '[{"value":"World!","name":"argument"}]'
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    assert_true(re.search(
#        '<sub-workflow>\W+'
#            '<app-path>\${nameNode}/user/hue/oozie/workspaces/_test_-oozie-(.+?)</app-path>\W+'
#            '<propagate-configuration/>\W+'
#                '<configuration>\W+'
#                '<property>\W+'
#                    '<name>argument</name>\W+'
#                    '<value>World!</value>\W+'
#                '</property>\W+'
#            '</configuration>\W+'
#        '</sub-workflow>', xml, re.MULTILINE), xml)
#
#    wf2.delete(skip_trash=True)
#
#  def test_workflow_flatten_list(self):
#    assert_equal('[<Start: start>, <Mapreduce: action-name-1>, <Mapreduce: action-name-2>, <Mapreduce: action-name-3>, '
#                 '<Kill: kill>, <End: end>]',
#                 str(self.wf.node_list))
#
#    # 1 2
#    #  3
#    self.setup_forking_workflow()
#
#    assert_equal('[<Start: start>, <Fork: fork-name-1>, <Mapreduce: action-name-1>, <Mapreduce: action-name-2>, '
#                 '<Join: join-name-1>, <Mapreduce: action-name-3>, <Kill: kill>, <End: end>]',
#                 str(self.wf.node_list))
#
#
#  def test_workflow_generic_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'generic', [self.wf.start], {
#        u'name': 'Generic',
#        u'description': 'Execute a Generic email action',
#        u'xml': """
#        <email xmlns="uri:oozie:email-action:0.1">
#            <to>hue@hue.org,django@python.org</to>
#            <subject>My subject</subject>
#            <body>My body</body>
#        </email>""",
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#    <action name="Generic">
#        <email xmlns="uri:oozie:email-action:0.1">
#            <to>hue@hue.org,django@python.org</to>
#            <subject>My subject</subject>
#            <body>My body</body>
#        </email>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>""" in xml, xml)
#
#
#  def test_workflow_hive_gen_xml(self):
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'hive', [self.wf.start], {
#        u'job_xml': 'my-job.xml',
#        u'files': '["hello.py"]',
#        u'name': 'MyHive',
#        u'job_properties': '[]',
#        u'script_path': 'hello.sql',
#        u'archives': '[]',
#        u'prepares': '[]',
#        u'params': '[{"value":"World!","type":"argument"}]',
#        u'description': ''
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    assert_true("""
#<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">
#  <global>
#      <job-xml>jobconf.xml</job-xml>
#            <configuration>
#                <property>
#                    <name>sleep-all</name>
#                    <value>${SLEEP}</value>
#                </property>
#            </configuration>
#  </global>
#    <start to="MyHive"/>
#    <action name="MyHive">
#        <hive xmlns="uri:oozie:hive-action:0.2">
#            <job-tracker>${jobTracker}</job-tracker>
#            <name-node>${nameNode}</name-node>
#              <job-xml>my-job.xml</job-xml>
#            <script>hello.sql</script>
#              <argument>World!</argument>
#            <file>hello.py#hello.py</file>
#        </hive>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>
#    <kill name="kill">
#        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
#    </kill>
#    <end name="end"/>
#</workflow-app>""" in xml, xml)
#
#    import beeswax
#    from beeswax.tests import hive_site_xml
#
#    tmpdir = tempfile.mkdtemp()
#    saved = None
#    try:
#      # We just replace the Beeswax conf variable
#      class Getter(object):
#        def get(self):
#          return tmpdir
#
#      xml = hive_site_xml(is_local=False, use_sasl=True, kerberos_principal='hive/_HOST@test.com')
#      file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(xml)
#
#      beeswax.hive_site.reset()
#      saved = beeswax.conf.HIVE_CONF_DIR
#      beeswax.conf.HIVE_CONF_DIR = Getter()
#
#      action1 = Node.objects.get(workflow=self.wf, name='MyHive')
#      action1.credentials = [{'name': 'hcat', 'value': True}, {'name': 'hbase', 'value': False}, {'name': 'hive2', 'value': True}]
#      action1.save()
#
#      xml = self.wf.to_xml(mapping={
#          'credentials': {
#              'hcat': {
#                  'xml_name': 'hcat',
#                  'properties': [
#                      ('hcat.metastore.uri', 'thrift://hue-koh-chang:9999'),
#                      ('hcat.metastore.principal', 'hive')
#                  ]
#              },
#              'hive2': {
#                  'xml_name': 'hive2',
#                  'properties': [
#                      ('hive2.jdbc.url', 'jdbc:hive2://hue-koh-chang:8888'),
#                      ('hive2.server.principal', 'hive')
#                  ]
#              }
#          }
#        }
#      )
#
#      assert_true("""
#<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">
#  <global>
#      <job-xml>jobconf.xml</job-xml>
#            <configuration>
#                <property>
#                    <name>sleep-all</name>
#                    <value>${SLEEP}</value>
#                </property>
#            </configuration>
#  </global>
#  <credentials>
#    <credential name="hcat" type="hcat">
#      <property>
#        <name>hcat.metastore.uri</name>
#        <value>thrift://hue-koh-chang:9999</value>
#      </property>
#      <property>
#        <name>hcat.metastore.principal</name>
#        <value>hive</value>
#      </property>
#    </credential>
#    <credential name="hive2" type="hive2">
#      <property>
#        <name>hive2.jdbc.url</name>
#        <value>jdbc:hive2://hue-koh-chang:8888</value>
#      </property>
#      <property>
#        <name>hive2.server.principal</name>
#        <value>hive</value>
#      </property>
#    </credential>
#  </credentials>
#    <start to="MyHive"/>
#    <action name="MyHive" cred="hcat,hive2">
#        <hive xmlns="uri:oozie:hive-action:0.2">
#            <job-tracker>${jobTracker}</job-tracker>
#            <name-node>${nameNode}</name-node>
#              <job-xml>my-job.xml</job-xml>
#            <script>hello.sql</script>
#              <argument>World!</argument>
#            <file>hello.py#hello.py</file>
#        </hive>
#        <ok to="end"/>
#        <error to="kill"/>
#    </action>
#    <kill name="kill">
#        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
#    </kill>
#    <end name="end"/>
#</workflow-app>""" in xml, xml)
#
#    finally:
#      beeswax.hive_site.reset()
#      if saved is not None:
#        beeswax.conf.HIVE_CONF_DIR = saved
#      shutil.rmtree(tmpdir)
#
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#
#  def test_workflow_gen_workflow_sla(self):
#    xml = self.wf.to_xml({'output': '/path'})
#    assert_false('<sla' in xml, xml)
#    assert_false('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
#    assert_false('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
#
#    sla = self.wf.sla
#    sla[0]['value'] = True
#    sla[1]['value'] = 'now' # nominal-time
#    sla[3]['value'] = '${ 10 * MINUTES}' # should-end
#    self.wf.sla = sla
#    self.wf.save()
#
#    xml = self.wf.to_xml({'output': '/path'})
#    assert_true('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
#    assert_true('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
#    assert_true("""<end name="end"/>
#          <sla:info>
#            <sla:nominal-time>now</sla:nominal-time>
#            <sla:should-end>${ 10 * MINUTES}</sla:should-end>
#          </sla:info>
#</workflow-app>""" in xml, xml)
#
#
#  def test_workflow_gen_action_sla(self):
#    xml = self.wf.to_xml({'output': '/path'})
#    assert_false('<sla' in xml, xml)
#    assert_false('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
#    assert_false('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
#
#    self.wf.node_set.filter(name='action-name-1').delete()
#
#    action1 = add_node(self.wf, 'action-name-1', 'hive', [self.wf.start], {
#        u'job_xml': 'my-job.xml',
#        u'files': '["hello.py"]',
#        u'name': 'MyHive',
#        u'job_properties': '[]',
#        u'script_path': 'hello.sql',
#        u'archives': '[]',
#        u'prepares': '[]',
#        u'params': '[{"value":"World!","type":"argument"}]',
#        u'description': ''
#    })
#    Link(parent=action1, child=self.wf.end, name="ok").save()
#
#    xml = self.wf.to_xml()
#
#    sla = action1.sla
#    sla[0]['value'] = True
#    sla[1]['value'] = 'now' # nominal-time
#    sla[3]['value'] = '${ 10 * MINUTES}' # should-end
#    action1.sla = sla
#    action1.save()
#
#    xml = self.wf.to_xml({'output': '/path'})
#    assert_true('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
#    assert_true('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
#    assert_true("""<error to="kill"/>
#          <sla:info>
#            <sla:nominal-time>now</sla:nominal-time>
#            <sla:should-end>${ 10 * MINUTES}</sla:should-end>
#          </sla:info>
#    </action>""" in xml, xml)
