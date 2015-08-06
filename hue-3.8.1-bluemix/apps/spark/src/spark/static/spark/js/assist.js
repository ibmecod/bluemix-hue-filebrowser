// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var Assist = function (options) {
  var self = this;

  function hasExpired(timestamp) {
    if (!timestamp) {
      return true;
    }
    var TIME_TO_LIVE_IN_MILLIS = 86400000; // 1 day
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  }

  function getTotalStoragePrefix() {
    var _app = "";
    if (typeof options.app != "undefined") {
      _app = options.app;
    }
    if (typeof options.user != "undefined") {
      return _app + "_" + options.user + "_";
    }
    return (_app != "" ? _app + "_" : "");
  }


  function jsonCalls(force) {
    if (typeof options.baseURL == "undefined" || options.baseURL == null) {
      console.error("Assist should always have a baseURL set to work fine.");
      return null;
    }

    var _url = options.baseURL;
    if (options.firstLevel != null) {
      _url += options.firstLevel;
    }
    if (options.secondLevel != null) {
      _url += "/" + options.secondLevel;
    }

    var _cachePath = getTotalStoragePrefix() + _url;
    var _cached = $.totalStorage(_cachePath);
    var _returnCached = false;
    if (_cached != null && !hasExpired(_cached.timestamp) && typeof force == "undefined") {
      options.onDataReceived(_cached.data);
      _returnCached = true;
    }

    if (options.onError) {
      $.ajaxSetup({
        error: function (x, e) {
          if (x.status == 500) {
            self.hasErrors(true);
            options.onError(e);
          }
        }
      });
    }

    if (!_returnCached) {
      $.ajax({
        type: "GET",
        url: _url + "?" + Math.random(),
        success: function (data) {
          if (data.error) {
            if (typeof options.failsSilentlyOn == "undefined" || (data.code != null && options.failsSilentlyOn.indexOf(data.code) == -1)) {
              $.jHueNotify.error(data.error);
            }
          }
          else {
            var _obj = {
              data: data,
              timestamp: (new Date()).getTime()
            }
            $.totalStorage(_cachePath, _obj);
            options.onDataReceived($.totalStorage(_cachePath).data);
          }
        },
        error: function (error) {
          $(document).trigger('error', error);
        }
      });
    }

  }

  self.options = options;

  self.getData = function (path, force) {
    self.path(path);
    self.options.firstLevel = null;
    self.options.secondLevel = null;
    if (path) {
      if (path.indexOf("/") > -1) {
        self.options.firstLevel = path.split("/")[0];
        self.options.secondLevel = path.split("/")[1];
      }
      else {
        self.options.firstLevel = path;
      }
    }
    jsonCalls(force);
  }

  // ko observables
  self.isLoading = ko.observable(true);
  self.hasErrors = ko.observable(false);
  self.path = ko.observable();
  self.selectedMainObject = ko.observable();
  self.mainObjects = ko.observableArray([]);
  self.firstLevelObjects = ko.observable({});

  self.filter = ko.observable("");
  self.filter.extend({ rateLimit: 150 });
  self.filteredFirstLevelObjects = ko.computed(function () {
    return ko.utils.arrayFilter(Object.keys(self.firstLevelObjects()), function (item) {
      return item.toLowerCase().indexOf(self.filter()) > -1;
    });
  });
}