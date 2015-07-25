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

ko.bindingHandlers.slideVisible = {
  init: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).toggle(ko.unwrap(value));
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    ko.unwrap(value) ? $(element).slideDown(100) : $(element).slideUp(100);
  }
};

ko.bindingHandlers.fadeVisible = {
  init: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).toggle(ko.unwrap(value));
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).stop();
    ko.unwrap(value) ? $(element).fadeIn() : $(element).hide();
  }
};


ko.extenders.numeric = function (target, config) {
  var precision = typeof config.precision === 'undefined' ? config : config.precision;
  var roundingMultiplier = Math.pow(10, precision);

  var result = ko.computed({
    read: target,
    write: function (newValue) {
      var current = target(),
          newValueAsNum = isNaN(newValue) ? 0 : parseFloat(+newValue),
          valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;

      if (newValue === '' && config.allowEmpty) {
        valueToWrite = newValue;
      }
      if (valueToWrite !== current) {
        target(valueToWrite);
      } else {
        if (newValue !== current) {
          target.notifySubscribers(valueToWrite);
        }
      }
    }
  }).extend({ notify: 'always' });
  result(target());
  return result;
};

ko.bindingHandlers.numericTextInput = {
  init: function (element, valueAccessor, allBindings) {
    var bindingOptions = ko.unwrap(valueAccessor());
    var numericValue = ko.observable(bindingOptions.value()).extend({ numeric: { precision: bindingOptions.precision, allowEmpty: typeof bindingOptions.allowEmpty !== 'undefined' && bindingOptions.allowEmpty } });
    numericValue.subscribe(function(newValue) { bindingOptions.value(newValue) });
    ko.bindingHandlers.textInput.init(element, function() { return numericValue }, allBindings);
  }
};

ko.bindingHandlers.freshereditor = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var _el = $(element);
    var options = $.extend(valueAccessor(), {});
    _el.html(options.data());
    _el.freshereditor({
      excludes: ['strikethrough', 'removeFormat', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
    });
    _el.freshereditor("edit", true);
    _el.on("mouseup", function () {
      storeSelection();
      updateValues();
    });

    var sourceDelay = -1;
    _el.on("keyup", function () {
      clearTimeout(sourceDelay);
      storeSelection();
      sourceDelay = setTimeout(function () {
        updateValues();
      }, 100);
    });

    $(".chosen-select").chosen({
      disable_search_threshold: 10,
      width: "75%"
    });

    $(document).on("addFieldToVisual", function (e, field) {
      _el.focus();
      pasteHtmlAtCaret("{{" + field.name() + "}}");
    });

    $(document).on("addFunctionToVisual", function (e, fn) {
      _el.focus();
      pasteHtmlAtCaret(fn);
    });

    function updateValues() {
      $("[data-template]")[0].editor.setValue(stripHtmlFromFunctions(_el.html()));
      valueAccessor().data(_el.html());
    }

    function storeSelection() {
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          range = sel.getRangeAt(0);
          _el.data("range", range);
        }
      }
      else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        _el.data("selection", document.selection);
      }
    }

    function pasteHtmlAtCaret(html) {
      var sel, range;
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          if (_el.data("range")) {
            range = _el.data("range");
          }
          else {
            range = sel.getRangeAt(0);
          }
          range.deleteContents();

          // Range.createContextualFragment() would be useful here but is
          // non-standard and not supported in all browsers (IE9, for one)
          var el = document.createElement("div");
          el.innerHTML = html;
          var frag = document.createDocumentFragment(), node, lastNode;
          while ((node = el.firstChild)) {
            lastNode = frag.appendChild(node);
          }
          range.insertNode(frag);

          // Preserve the selection
          if (lastNode) {
            range = range.cloneRange();
            range.setStartAfter(lastNode);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      } else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        if (_el.data("selection")) {
          _el.data("selection").createRange().pasteHTML(html);
        }
        else {
          document.selection.createRange().pasteHTML(html);
        }
      }
    }
  }
};

ko.bindingHandlers.slider = {
  init: function (element, valueAccessor) {
    var _el = $(element);
    var _options = $.extend(valueAccessor(), {});
    _el.slider({
      min: !isNaN(parseFloat(_options.start())) ? parseFloat(_options.start()) : 0,
      max: !isNaN(parseFloat(_options.end())) ? parseFloat(_options.end()) : 10,
      step: !isNaN(parseFloat(_options.gap())) ? parseFloat(_options.gap()) : 1,
      handle: _options.handle ? _options.handle : 'triangle',
      start: parseFloat(_options.min()),
      end: parseFloat(_options.max()),
      tooltip_split: true,
      tooltip: 'always',
      labels: _options.labels
    });
    _el.on("slide", function (e) {
      _options.start(e.min);
      _options.end(e.max);
      _options.min(e.start);
      _options.max(e.end);
      if (_options.min() < _options.start()){
        _options.start(_options.min());
      }
      if (_options.max() > _options.end()){
        _options.end(_options.max());
      }
      _options.gap(e.step);
      if (typeof _options.properties.initial_start == "function"){
        _options.properties.start(_options.properties.initial_start());
        _options.properties.end(_options.properties.initial_end());
        _options.properties.gap(_options.properties.initial_gap());
      }
    });
    _el.on("slideStop", function (e) {
      viewModel.search();
    });
  },
  update: function (element, valueAccessor) {
    var _options = $.extend(valueAccessor(), {});
  }
}

ko.bindingHandlers.daterangepicker = {
  INTERVAL_OPTIONS: [
    {
      value: "+200MILLISECONDS",
      label: "200ms"
    },
    {
      value: "+1SECONDS",
      label: "1s"
    },
    {
      value: "+5SECONDS",
      label: "5s"
    },
    {
      value: "+30SECONDS",
      label: "30s"
    },
    {
      value: "+1MINUTES",
      label: "1m"
    },
    {
      value: "+5MINUTES",
      label: "5m"
    },
    {
      value: "+10MINUTES",
      label: "10m"
    },
    {
      value: "+30MINUTES",
      label: "30m"
    },
    {
      value: "+1HOURS",
      label: "1h"
    },
    {
      value: "+3HOURS",
      label: "3h"
    },
    {
      value: "+6HOURS",
      label: "6h"
    },
    {
      value: "+12HOURS",
      label: "12h"
    },
    {
      value: "+1DAYS",
      label: "1d"
    },
    {
      value: "+7DAYS",
      label: "7d"
    },
    {
      value: "+1MONTHS",
      label: "1M"
    },
    {
      value: "+6MONTHS",
      label: "6M"
    },
    {
      value: "+1YEARS",
      label: "1y"
    },
    {
      value: "+10YEARS",
      label: "10y"
    }
  ],
  EXTRA_INTERVAL_OPTIONS: [],

  init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var DATE_FORMAT = "YYYY-MM-DD";
    var TIME_FORMAT = "HH:mm:ss";
    var DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT;

    var _el = $(element);
    var _options = $.extend(valueAccessor(), {});

    var _intervalOptions = [];
    ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS.forEach(function (interval) {
      _intervalOptions.push('<option value="' + interval.value + '">' + interval.label + '</option>');
    });

    function enableOptions() {
      var _opts = [];
      var _tmp = $("<div>").html(_intervalOptions.join(""))
      $.each(arguments, function (cnt, item) {
        if (_tmp.find("option[value='+" + item + "']").length > 0) {
          _opts.push('<option value="+' + item + '">' + _tmp.find("option[value='+" + item + "']").eq(0).text() + '</option>');
        }
      });
      return _opts;
    }

    function renderOptions(opts) {
      var _html = "";
      for (var i = 0; i < opts.length; i++) {
        _html += opts[i];
      }
      return _html;
    }

    var _tmpl = $('<div class="simpledaterangepicker">' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-small form-control start-date" />' +
            '</div>' +
            '<div class="input-prepend input-group left-margin">' +
            '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
            '<input type="text" class="input-mini form-control start-time" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-small form-control end-date" />' +
            '</div>' +
            '<div class="input-prepend input-group left-margin">' +
            '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
            '<input type="text" class="input-mini form-control end-time" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.INTERVAL + '</div>' +
            '<div class="input-prepend input-group"><span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span></div>&nbsp;' +
            '<select class="input-small interval-select" style="margin-right: 6px">' +
            renderOptions(_intervalOptions) +
            '</select>' +
            '<input class="input interval hide" type="hidden" value="" />' +
            '</div>' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
            '<div class="facet-field-switch"><a href="javascript:void(0)"><i class="fa fa-calendar-o"></i> ' + KO_DATERANGEPICKER_LABELS.CUSTOM_FORMAT + '</a></div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-large form-control start-date-custom" />' +
            '</div>' +
            '<a class="custom-popover" href="javascript:void(0)" data-trigger="focus" data-toggle="popover" data-placement="right" rel="popover" data-html="true"' +
            '       title="' + KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_TITLE + '"' +
            '       data-content="' + KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_CONTENT + '">' +
            '&nbsp;&nbsp;<i class="fa fa-question-circle"></i>' +
            ' </a>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-large form-control end-date-custom" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.INTERVAL + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span>' +
            '<input type="text" class="input-large form-control interval-custom" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
            '<div class="facet-field-switch"><a href="javascript:void(0)"><i class="fa fa-calendar"></i> ' + KO_DATERANGEPICKER_LABELS.DATE_PICKERS + '</a></div>' +
            '</div>' +

            '</div>'
    );

    _tmpl.insertAfter(_el);

    $(".custom-popover").popover();

    var _minMoment = moment(_options.min());
    var _maxMoment = moment(_options.max());

    if (_minMoment.isValid() && _maxMoment.isValid()) {
      _tmpl.find(".facet-field-cnt.custom").hide();
      _tmpl.find(".facet-field-cnt.picker").show();
      _tmpl.find(".start-date").val(_minMoment.utc().format(DATE_FORMAT));
      _tmpl.find(".start-time").val(_minMoment.utc().format(TIME_FORMAT));
      _tmpl.find(".end-date").val(_maxMoment.utc().format(DATE_FORMAT));
      _tmpl.find(".end-time").val(_maxMoment.utc().format(TIME_FORMAT));
      _tmpl.find(".interval").val(_options.gap());
      _tmpl.find(".interval-select").val(_options.gap());
      _tmpl.find(".interval-custom").val(_options.gap());
      if (_tmpl.find(".interval-select").val() == null || ko.bindingHandlers.daterangepicker.EXTRA_INTERVAL_OPTIONS.indexOf(_tmpl.find(".interval-select").val()) > -1) {
        pushIntervalValue(_options.gap());
        _tmpl.find(".facet-field-cnt.custom").show();
        _tmpl.find(".facet-field-cnt.picker").hide();
      }
    }
    else {
      _tmpl.find(".facet-field-cnt.custom").show();
      _tmpl.find(".facet-field-cnt.picker").hide();
      _tmpl.find(".start-date-custom").val(_options.min());
      _tmpl.find(".end-date-custom").val(_options.max());
      _tmpl.find(".interval-custom").val(_options.gap());
      pushIntervalValue(_options.gap());
    }

    if (typeof _options.relatedgap != "undefined"){
      pushIntervalValue(_options.relatedgap());
    }

    _tmpl.find(".start-date").datepicker({
      format: DATE_FORMAT.toLowerCase()
    }).on("changeDate", function () {
      rangeHandler(true);
    });

    _tmpl.find(".start-date").on("change", function () {
      rangeHandler(true);
    });

    _tmpl.find(".start-time").timepicker({
      minuteStep: 1,
      showSeconds: true,
      showMeridian: false,
      defaultTime: false
    });

    _tmpl.find(".end-date").datepicker({
      format: DATE_FORMAT.toLowerCase()
    }).on("changeDate", function () {
      rangeHandler(false);
    });

    _tmpl.find(".end-date").on("change", function () {
      rangeHandler(true);
    });

    _tmpl.find(".end-time").timepicker({
      minuteStep: 1,
      showSeconds: true,
      showMeridian: false,
      defaultTime: false
    });

    _tmpl.find(".start-time").on("change", function () {
      // the timepicker plugin doesn't have a change event handler
      // so we need to wait a bit to handle in with the default field event
      window.setTimeout(function () {
        rangeHandler(true)
      }, 200);
    });

    _tmpl.find(".end-time").on("change", function () {
      window.setTimeout(function () {
        rangeHandler(false)
      }, 200);
    });

    if (_minMoment.isValid() && _maxMoment.isValid()) {
      rangeHandler(true);
    }

    _tmpl.find(".facet-field-cnt.picker .facet-field-switch a").on("click", function () {
      _tmpl.find(".facet-field-cnt.custom").show();
      _tmpl.find(".facet-field-cnt.picker").hide();
    });

    _tmpl.find(".facet-field-cnt.custom .facet-field-switch a").on("click", function () {
      _tmpl.find(".facet-field-cnt.custom").hide();
      _tmpl.find(".facet-field-cnt.picker").show();
    });

    _tmpl.find(".start-date-custom").on("change", function () {
      _options.min(_tmpl.find(".start-date-custom").val());
      _tmpl.find(".start-date").val(moment(_options.min()).utc().format(DATE_FORMAT));
      _tmpl.find(".start-time").val(moment(_options.min()).utc().format(TIME_FORMAT));
      _options.start(_options.min());
    });

    _tmpl.find(".end-date-custom").on("change", function () {
      _options.max(_tmpl.find(".end-date-custom").val());
      _tmpl.find(".end-date").val(moment(_options.max()).utc().format(DATE_FORMAT));
      _tmpl.find(".end-time").val(moment(_options.max()).utc().format(TIME_FORMAT));
      _options.end(_options.max());
    });

    _tmpl.find(".interval-custom").on("change", function () {
      _options.gap(_tmpl.find(".interval-custom").val());
      matchIntervals(true);
      if (typeof _options.relatedgap != "undefined"){
        _options.relatedgap(_options.gap());
      }
    });

    function pushIntervalValue(newValue) {
      var _found = false;
      ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS.forEach(function(interval) {
        if (interval.value == newValue){
          _found = true;
        }
      });
      if (!_found){
        ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS.push({
          value: newValue,
          label: newValue
        });
        ko.bindingHandlers.daterangepicker.EXTRA_INTERVAL_OPTIONS.push(newValue);
        _intervalOptions.push('<option value="' + newValue + '">' + newValue + '</option>');
      }
    }

    function matchIntervals(fromCustom) {
      _tmpl.find(".interval-select").val(_options.gap());
      if (_tmpl.find(".interval-select").val() == null) {
        if (fromCustom){
          pushIntervalValue(_options.gap());
          if (bindingContext.$root.intervalOptions){
            bindingContext.$root.intervalOptions(ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS);
          }
        }
        else {
          _tmpl.find(".interval-select").val(_tmpl.find(".interval-select option:first").val());
          _options.gap(_tmpl.find(".interval-select").val());
          if (typeof _options.relatedgap != "undefined"){
            _options.relatedgap(_options.gap());
          }
          _tmpl.find(".interval-custom").val(_options.gap());
        }
      }
    }

    _tmpl.find(".interval-select").on("change", function () {
      _options.gap(_tmpl.find(".interval-select").val());
      if (typeof _options.relatedgap != "undefined"){
        _options.relatedgap(_options.gap());
      }
      _tmpl.find(".interval").val(_options.gap());
      _tmpl.find(".interval-custom").val(_options.gap());
    });

    function rangeHandler(isStart) {
      var startDate = moment(_tmpl.find(".start-date").val() + " " + _tmpl.find(".start-time").val(), DATETIME_FORMAT);
      var endDate = moment(_tmpl.find(".end-date").val() + " " + _tmpl.find(".end-time").val(), DATETIME_FORMAT);
      if (startDate.valueOf() > endDate.valueOf()) {
        if (isStart) {
          _tmpl.find(".end-date").val(startDate.utc().format(DATE_FORMAT));
          _tmpl.find(".end-date").datepicker('setValue', startDate.utc().format(DATE_FORMAT));
          _tmpl.find(".end-date").data("original-val", _tmpl.find(".end-date").val());
          _tmpl.find(".end-time").val(startDate.utc().format(TIME_FORMAT));
        }
        else {
          if (_tmpl.find(".end-date").val() == _tmpl.find(".start-date").val()) {
            _tmpl.find(".end-time").val(startDate.utc().format(TIME_FORMAT));
            _tmpl.find(".end-time").data("timepicker").setValues(startDate.format(TIME_FORMAT));
          }
          else {
            _tmpl.find(".end-date").val(_tmpl.find(".end-date").data("original-val"));
            _tmpl.find(".end-date").datepicker("setValue", _tmpl.find(".end-date").data("original-val"));
          }
          // non-sticky error notification
          $.jHueNotify.notify({
            level: "ERROR",
            message: "The end cannot be before the starting moment"
          });
        }
      }
      else {
        _tmpl.find(".end-date").data("original-val", _tmpl.find(".end-date").val());
        _tmpl.find(".start-date").datepicker("hide");
        _tmpl.find(".end-date").datepicker("hide");
      }

      var _calculatedStartDate = moment(_tmpl.find(".start-date").val() + " " + _tmpl.find(".start-time").val(), DATETIME_FORMAT);
      var _calculatedEndDate = moment(_tmpl.find(".end-date").val() + " " + _tmpl.find(".end-time").val(), DATETIME_FORMAT);

      _options.min(_calculatedStartDate.format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      _options.start(_options.min());
      _options.max(_calculatedEndDate.format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      _options.end(_options.max());

      _tmpl.find(".start-date-custom").val(_options.min());
      _tmpl.find(".end-date-custom").val(_options.max());

      var _opts = [];
      // hide not useful options from interval
      if (_calculatedEndDate.diff(_calculatedStartDate, 'minutes') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'minutes') <= 60) {
        _opts = enableOptions("200MILLISECONDS", "1SECONDS", "1MINUTES", "5MINUTES", "10MINUTES", "30MINUTES");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'hours') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'hours') <= 12) {
        _opts = enableOptions("5MINUTES", "10MINUTES", "30MINUTES", "1HOURS", "3HOURS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'hours') > 12 && _calculatedEndDate.diff(_calculatedStartDate, 'hours') < 36) {
        _opts = enableOptions("10MINUTES", "30MINUTES", "1HOURS", "3HOURS", "6HOURS", "12HOURS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 7) {
        _opts = enableOptions("30MINUTES", "1HOURS", "3HOURS", "6HOURS", "12HOURS", "1DAYS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 7 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 14) {
        _opts = enableOptions("3HOURS", "6HOURS", "12HOURS", "1DAYS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 14 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 31) {
        _opts = enableOptions("12HOURS", "1DAYS", "7DAYS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') >= 1) {
        _opts = enableOptions("1DAYS", "7DAYS", "1MONTHS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 6) {
        _opts = enableOptions("1DAYS", "7DAYS", "1MONTHS", "6MONTHS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 12) {
        _opts = enableOptions("7DAYS", "1MONTHS", "6MONTHS", "1YEARS", "10YEARS");
      }

      $(".interval-select").html(renderOptions(_opts));

      matchIntervals(true);
    }
  }
}

ko.bindingHandlers.oneClickSelect = {
  init: function (element) {
    $(element).click(function() {
      if (document.selection) {
        var range = document.body.createTextRange();
        range.moveToElementText(element);
        range.select();
      } else if (window.getSelection) {
        var range = document.createRange();
        range.selectNode(element);
        window.getSelection().addRange(range);
      }
    });
  }
};

ko.bindingHandlers.augmenthtml = {
  render: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var _val = ko.unwrap(valueAccessor());
    var _enc = $("<span>").html(_val);
    if (_enc.find("style").length > 0) {
      var parser = new less.Parser();
      $(_enc.find("style")).each(function (cnt, item) {
        var _less = "#result-container {" + $(item).text() + "}";
        try {
          parser.parse(_less, function (err, tree) {
            $(item).text(tree.toCSS());
          });
        }
        catch (e) {
        }
      });
      $(element).html(_enc.html());
    }
    else {
      $(element).html(_val);
    }
  },
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
  }
}

ko.bindingHandlers.clearable = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var _el = $(element);

    function tog(v) {
      return v ? "addClass" : "removeClass";
    }

    _el.addClass("clearable");
    _el
        .on("input", function () {
          _el[tog(this.value)]("x");
        })
        .on("change", function () {
          valueAccessor()(_el.val());
        })
        .on("blur", function () {
          valueAccessor()(_el.val());
        })
        .on("mousemove", function (e) {
          _el[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)]("onX");
        })
        .on("click", function (e) {
          if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
            _el.removeClass("x onX").val("");
            valueAccessor()("");
          }
        });

    if (allBindingsAccessor().valueUpdate != null && allBindingsAccessor().valueUpdate == "afterkeydown") {
      _el.on("keyup", function () {
        valueAccessor()(_el.val());
      });
    }
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    $(element).val(ko.unwrap(valueAccessor()));
  }
}

ko.bindingHandlers.spinedit = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    $(element).spinedit({
      minimum: 0,
      maximum: 10000,
      step: 5,
      value: ko.unwrap(valueAccessor()),
      numberOfDecimals: 0
    });
    $(element).on("valueChanged", function (e) {
      valueAccessor()(e.value);
    });
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    $(element).spinedit("setValue", ko.unwrap(valueAccessor()));
  }
}

ko.bindingHandlers.codemirror = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var options = $.extend(valueAccessor(), {});
    var editor = CodeMirror.fromTextArea(element, options);
    element.editor = editor;
    editor.setValue(options.data());
    editor.refresh();
    var wrapperElement = $(editor.getWrapperElement());

    $(document).on("refreshCodemirror", function () {
      editor.setSize("100%", 300);
      editor.refresh();
    });

    $(document).on("addFieldToSource", function (e, field) {
      if ($(element).data("template")) {
        editor.replaceSelection("{{" + field.name() + "}}");
      }
    });

    $(document).on("addFunctionToSource", function (e, fn) {
      if ($(element).data("template")) {
        editor.replaceSelection(fn);
      }
    });

    $(".chosen-select").chosen({
      disable_search_threshold: 10,
      width: "75%"
    });
    $('.chosen-select').trigger('chosen:updated');

    var sourceDelay = -1;
    editor.on("change", function (cm) {
      clearTimeout(sourceDelay);
      var _cm = cm;
      sourceDelay = setTimeout(function () {
        var _value = _cm.getValue();
        if (options.stripScript){
          _value = _value.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");
        }
        valueAccessor().data(_value);
        if ($(".widget-html-pill").parent().hasClass("active")) {
          $("[contenteditable=true]").html(stripHtmlFromFunctions(valueAccessor().data()));
        }
      }, 100);
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
      wrapperElement.remove();
    });
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    var editor = element.editor;
    editor.refresh();
  }
};

ko.bindingHandlers.chosen = {
    init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
        var $element = $(element);
        var options = ko.unwrap(valueAccessor());
        
        if (typeof options === 'object')
            $element.chosen(options);
        else
            $element.chosen();
                
        ['options', 'selectedOptions', 'value'].forEach(function(propName){
            if (allBindings.has(propName)){
                var prop = allBindings.get(propName);
                if (ko.isObservable(prop)){
                    prop.subscribe(function(){
                        $element.trigger('chosen:updated');
                    });
                }
            }
        });        
    }
}

ko.bindingHandlers.tooltip = {
  init: function (element, valueAccessor) {
    var local = ko.utils.unwrapObservable(valueAccessor()),
        options = {};

    ko.utils.extend(options, local);

    $(element).tooltip(options);

    ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
      $(element).tooltip("destroy");
    });
  },
  update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var options = ko.utils.unwrapObservable(valueAccessor());
    var self = $(element);
    self.tooltip(options);
  }
};

ko.bindingHandlers.typeahead = {
  init: function (element, valueAccessor) {
    var binding = this;
    var elem = $(element);
    var valueAccessor = valueAccessor();

    var _options = {
      source: function () {
        var _source = ko.utils.unwrapObservable(valueAccessor.source);
        if (valueAccessor.extraKeywords) {
          _source = _source.concat(valueAccessor.extraKeywords.split(" "))
        }

        if (valueAccessor.sourceSuffix && _source) {
          var _tmp = [];
          _source.forEach(function(item){
            _tmp.push(item + valueAccessor.sourceSuffix);
          });
          _source = _tmp;
        }
        return _source;
      },
      onselect: function (val) {
        if (typeof valueAccessor.target == "function") {
          valueAccessor.target(val);
        }
        else {
         valueAccessor.target = val;
        }
      }
    }

    function extractor(query, extractorSeparator) {
      var result = /([^ ]+)$/.exec(query);
      if (extractorSeparator){
        result = new RegExp("([^\\" + extractorSeparator + "]+)$").exec(query);
      }
      if (result && result[1])
        return result[1].trim();
      return "";
    }

    if (valueAccessor.multipleValues) {
      var _extractorFound = null;

      function updateExtractors() {
        var _val = elem.val();
        _extractorFound = null;
        var _extractors = (typeof valueAccessor.multipleValuesExtractors == "undefined" || valueAccessor.multipleValuesExtractors == null ? [" "] : valueAccessor.multipleValuesExtractors);
        var _extractorFoundLastIndex = -1;
        _extractors.forEach(function (extractor) {
          if (_val.indexOf(extractor) > -1) {
            if (_val.indexOf(extractor) >= _extractorFoundLastIndex) {
              _extractorFound = extractor;
              _extractorFoundLastIndex = _val.indexOf(extractor);
            }
          }
        });
      }

      _options.updater = function (item) {
        var _val = this.$element.val();
        var _separator = (typeof valueAccessor.multipleValuesSeparator == "undefined" || valueAccessor.multipleValuesSeparator == null ? ":" : valueAccessor.multipleValuesSeparator);
        if (valueAccessor.extraKeywords && valueAccessor.extraKeywords.split(" ").indexOf(item) > -1) {
          _separator = "";
        }
        updateExtractors();
        if (_extractorFound != null) {
          return _val.substring(0, _val.lastIndexOf(_extractorFound)) + _extractorFound + item + _separator;
        }
        else {
          return item + _separator;
        }
      }
      _options.matcher = function (item) {
        updateExtractors();
        var _tquery = extractor(this.query, _extractorFound);
        if (!_tquery) return false;
        return ~item.toLowerCase().indexOf(_tquery.toLowerCase());
      },
          _options.highlighter = function (item) {
            updateExtractors();
            var _query = extractor(this.query, _extractorFound).replace(/[\-\[\]{}()*+?.:\\\^$|#\s]/g, '\\$&');
            return item.replace(new RegExp('(' + _query + ')', 'ig'), function ($1, match) {
              return '<strong>' + match + '</strong>'
            });
          }
    }

    if (valueAccessor.completeSolrRanges) {
      elem.on("keyup", function (e) {
        if (e.keyCode != 8 && e.which != 8 && elem.val() && (elem.val().slice(-1) == "[" || elem.val().slice(-1) == "{")) {
          var _index = elem.val().length;
          elem.val(elem.val() + " TO " + (elem.val().slice(-1) == "[" ? "]" : "}"));

          if (element.createTextRange) {
            var range = element.createTextRange();
            range.move("character", _index);
            range.select();
          } else if (element.selectionStart != null) {
            element.focus();
            element.setSelectionRange(_index, _index);
          }

        }
      });
    }

    if (valueAccessor.triggerOnFocus) {
      _options.minLength = 0;
    }

    element.typeahead = elem.typeahead(_options);

    if (valueAccessor.triggerOnFocus) {
      elem.on('focus', function () {
        elem.trigger("keyup");
      });
    }

    elem.blur(function () {
      if (typeof valueAccessor.target == "function") {
        valueAccessor.target(elem.val());
      }
      else {
       valueAccessor.target = elem.val();
      }
    });
  },
  update: function (element, valueAccessor) {
    var elem = $(element);
    var valueAccessor = valueAccessor();
    if (typeof valueAccessor.target == "function") {
      elem.val(valueAccessor.target());
    }
    else {
      elem.val(valueAccessor.target);
    }
    if (valueAccessor.forceUpdateSource) {
      element.typeahead.data('typeahead').source = function () {
        var _source = ko.utils.unwrapObservable(valueAccessor.source);
        if (valueAccessor.extraKeywords) {
          _source = _source.concat(valueAccessor.extraKeywords.split(" "))
        }

        if (valueAccessor.sourceSuffix && _source) {
          var _tmp = [];
          _source.forEach(function(item){
            _tmp.push(item + valueAccessor.sourceSuffix);
          });
          _source = _tmp;
        }
        return _source;
      }
    }

  }
};


ko.bindingHandlers.select2 = {
  init: function (element, valueAccessor, allBindingsAccessor, vm) {
    var options = ko.toJS(valueAccessor()) || {};

    if (typeof valueAccessor().update != "undefined") {
      if (options.type == "user" && viewModel.selectableHadoopUsers().indexOf(options.update) == -1) {
        viewModel.availableHadoopUsers.push({
          username: options.update
        });
      }
      if (options.type == "group") {
        if (options.update instanceof Array) {
          options.update.forEach(function (opt) {
            if (viewModel.selectableHadoopGroups().indexOf(opt) == -1) {
              viewModel.availableHadoopGroups.push({
                name: opt
              });
            }
          });
        }
        else if (viewModel.selectableHadoopGroups().indexOf(options.update) == -1) {
          viewModel.availableHadoopGroups.push({
            name: options.update
          });
        }
      }
      if (options.type == "action" && viewModel.availableActions().indexOf(options.update) == -1) {
        viewModel.availableActions.push(options.update);
      }
      if (options.type == "scope" && viewModel.availablePrivileges().indexOf(options.update) == -1) {
        viewModel.availablePrivileges.push(options.update);
      }
      if (options.type == "parameter" && options.update != "") {
        var _found = false;
        allBindingsAccessor().options().forEach(function(opt){
          if (opt[allBindingsAccessor().optionsValue]() == options.update){
            _found = true;
          }
        });
        if (!_found){
          allBindingsAccessor().options.push({
            name: ko.observable(options.update),
            value: ko.observable(options.update)
          });
        }
      }
    }
    $(element)
        .select2(options)
        .on("change", function (e) {
          if (typeof e.val != "undefined" && typeof valueAccessor().update != "undefined") {
            valueAccessor().update(e.val);
          }
        })
        .on("select2-focus", function (e) {
          if (typeof options.onFocus != "undefined") {
            options.onFocus();
          }
        })
        .on("select2-blur", function (e) {
          if (typeof options.onBlur != "undefined") {
            options.onBlur();
          }
        })
        .on("select2-open", function () {
          $(".select2-input").off("keyup").data("type", options.type).on("keyup", function (e) {
            if (e.keyCode === 13) {
              var _isArray = options.update instanceof Array;
              var _newVal = $(this).val();
              var _type = $(this).data("type");
              if ($.trim(_newVal) != "") {
                if (_type == "user") {
                  viewModel.availableHadoopUsers.push({
                    username: _newVal
                  });
                }
                if (_type == "group") {
                  viewModel.availableHadoopGroups.push({
                    name: _newVal
                  });
                }
                if (_type == "action") {
                  viewModel.availableActions.push(_newVal);
                }
                if (_type == "scope") {
                  viewModel.availablePrivileges.push(_newVal);
                }
                if (_type == "role") {
                  var _r = new Role(viewModel, { name: _newVal });
                  viewModel.tempRoles.push(_r);
                  viewModel.roles.push(_r);
                }
                if (_type == "parameter") {
                  var _found = false;
                  allBindingsAccessor().options().forEach(function(opt){
                    if (opt[allBindingsAccessor().optionsValue]() == _newVal){
                      _found = true;
                    }
                  });
                  if (!_found){
                    allBindingsAccessor().options.push({
                      name: ko.observable(_newVal),
                      value: ko.observable(_newVal)
                    });
                  }
                }
                if (_isArray) {
                  var _vals = $(element).select2("val");
                  _vals.push(_newVal);
                  $(element).select2("val", _vals, true);
                }
                else {
                  $(element).select2("val", _newVal, true);
                }
                $(element).select2("close");
              }
            }
          });
        })
  },
  update: function (element, valueAccessor, allBindingsAccessor, vm) {
    if (typeof allBindingsAccessor().visible != "undefined"){
      if ((typeof allBindingsAccessor().visible == "boolean" && allBindingsAccessor().visible) || (typeof allBindingsAccessor().visible == "function" && allBindingsAccessor().visible())) {
        $(element).select2("container").show();
      }
      else {
        $(element).select2("container").hide();
      }
    }
    if (typeof valueAccessor().update != "undefined") {
      $(element).select2("val", valueAccessor().update());
    }
    if (typeof valueAccessor().readonly != "undefined") {
      $(element).select2("readonly", valueAccessor().readonly);
      if (typeof valueAccessor().readonlySetTo != "undefined") {
        valueAccessor().readonlySetTo();
      }
    }
  }
};

ko.bindingHandlers.hivechooser = {
  init: function (element, valueAccessor, allBindingsAccessor, vm) {
    var self = $(element);
    self.val(valueAccessor()());

    function setPathFromAutocomplete(path) {
      self.val(path);
      valueAccessor()(path);
      self.blur();
    }

    self.on("blur", function () {
      valueAccessor()(self.val());
    });

    self.jHueHiveAutocomplete({
      skipColumns: true,
      showOnFocus: true,
      home: "/",
      onPathChange: function (path) {
        setPathFromAutocomplete(path);
      },
      onEnter: function (el) {
        setPathFromAutocomplete(el.val());
      },
      onBlur: function () {
        if (self.val().lastIndexOf(".") == self.val().length - 1) {
          self.val(self.val().substr(0, self.val().length - 1));
        }
        valueAccessor()(self.val());
      }
    });
  }
}

ko.bindingHandlers.hdfsAutocomplete = {
  init: function (element, valueAccessor, allBindingsAccessor, vm) {
    var stripHashes = function (str) {
      return str.replace(/#/gi, encodeURIComponent("#"));
    };

    var self = $(element);
    self.attr("autocomplete", "off");
    self.jHueHdfsAutocomplete({
      skipKeydownEvents: true,
      skipScrollEvent: true,
      zIndex: 990
    });
  }
};

ko.bindingHandlers.filechooser = {
  init: function (element, valueAccessor, allBindingsAccessor, vm) {
    var self = $(element);
    self.attr("autocomplete", "off");
    if (typeof valueAccessor() == "function" || typeof valueAccessor().value == "function") {
      self.val(valueAccessor().value ? valueAccessor().value(): valueAccessor()());
      self.data("fullPath", self.val());
      self.attr("data-original-title", self.val());
      if (valueAccessor().displayJustLastBit){
        var _val = self.val();
        self.val(_val.split("/")[_val.split("/").length - 1]);
      }
      self.on("blur", function () {
        if (valueAccessor().value){
          if (valueAccessor().displayJustLastBit){
            var _val = self.data("fullPath");
            valueAccessor().value(_val.substr(0, _val.lastIndexOf("/")) + "/" + self.val());
          }
          else {
            valueAccessor().value(self.val());
          }
          self.data("fullPath", valueAccessor().value());
        }
        else {
          valueAccessor()(self.val());
          self.data("fullPath", valueAccessor()());
        }
        self.attr("data-original-title", self.data("fullPath"));
      });
    }
    else {
      self.val(valueAccessor());
      self.on("blur", function () {
        valueAccessor(self.val());
      });
    }

    self.after(getFileBrowseButton(self, true, valueAccessor, true, allBindingsAccessor));
  }
};


function getFileBrowseButton(inputElement, selectFolder, valueAccessor, stripHdfsPrefix, allBindingsAccessor) {
  var _btn = $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
    e.preventDefault();
    $("html").addClass("modal-open");
    // check if it's a relative path
    callFileChooser();

    function callFileChooser() {
      var _initialPath = $.trim(inputElement.val()) != "" ? inputElement.val() : "/";
      if ((allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.skipInitialPathIfEmpty && inputElement.val() == "") || (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator)){
        _initialPath = "";
      }
      if (inputElement.data("fullPath")){
        _initialPath = inputElement.data("fullPath");
      }
      if (_initialPath.indexOf("hdfs://") > -1) {
        _initialPath = _initialPath.substring(7);
      }
      $("#filechooser").jHueFileChooser({
        suppressErrors: true,
        selectFolder: (selectFolder) ? true : false,
        onFolderChoose: function (filePath) {
          handleChoice(filePath, stripHdfsPrefix);
          if (selectFolder) {
            $("#chooseFile").modal("hide");
            $(".modal-backdrop").remove();
          }
        },
        onFileChoose: function (filePath) {
          handleChoice(filePath, stripHdfsPrefix);
          $("#chooseFile").modal("hide");
          $(".modal-backdrop").remove();
        },
        createFolder: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.createFolder,
        uploadFile: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.uploadFile,
        initialPath: _initialPath,
        errorRedirectPath: "",
        forceRefresh: true,
        showExtraHome: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.showExtraHome,
        extraHomeProperties: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.extraHomeProperties ? allBindingsAccessor().filechooserOptions.extraHomeProperties : {},
        filterExtensions: allBindingsAccessor && allBindingsAccessor().filechooserFilter ? allBindingsAccessor().filechooserFilter : ""
      });
      $("#chooseFile").modal("show");
      $("#chooseFile").on("hidden", function(){
        $("html").removeClass("modal-open");
        $(".modal-backdrop").remove();
      });
    }

    function handleChoice(filePath, stripHdfsPrefix) {
      if (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator){
        filePath = inputElement.val().split(allBindingsAccessor().filechooserPrefixSeparator)[0] + '=' + filePath;
      }
      if (allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.deploymentDir){
        inputElement.data("fullPath", filePath);
        inputElement.attr("data-original-title", filePath);
        if (filePath.indexOf(allBindingsAccessor().filechooserOptions.deploymentDir) == 0){
          filePath = filePath.substr(allBindingsAccessor().filechooserOptions.deploymentDir.length + 1);
        }
      }
      if (stripHdfsPrefix){
        inputElement.val(filePath);
      }
      else {
        inputElement.val("hdfs://" + filePath);
      }
      inputElement.change();
      if (valueAccessor){
        if (typeof valueAccessor() == "function" || typeof valueAccessor().value == "function") {
          if (valueAccessor().value){
            valueAccessor().value(inputElement.val());
            if (valueAccessor().displayJustLastBit){
              inputElement.data("fullPath", inputElement.val());
              inputElement.attr("data-original-title", inputElement.val());
              var _val = inputElement.val();
              inputElement.val(_val.split("/")[_val.split("/").length - 1])
            }
          }
          else {
            valueAccessor()(inputElement.val());
          }
        }
        else {
          valueAccessor(inputElement.val());
        }
      }
    }
  });
  if (allBindingsAccessor && allBindingsAccessor().filechooserDisabled){
    _btn.addClass("disabled").attr("disabled", "disabled");
  }
  return _btn;
}

ko.bindingHandlers.datepicker = {
  init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
    var _el = $(element);
    var _options = ko.unwrap(valueAccessor());
    _el.datepicker({
      format: "yyyy-mm-dd"
    }).on("show", function (e) {
      if (_options.momentFormat) {
        _el.datepicker("setValue", moment(_el.val()).utc().format("YYYY-MM-DD"));
      }
    }).on("changeDate", function (e) {
      setDate(e.date);
    }).on("hide", function (e) {
      setDate(e.date);
    });

    function setDate(d) {
      if (_options.momentFormat) {
        _el.val(moment(d).utc().format(_options.momentFormat));
      }
      allBindings().value(_el.val());
    }
  }
}


ko.bindingHandlers.timepicker = {
  init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
    var _el = $(element);
    _el.timepicker({
      minuteStep: 1,
      showSeconds: false,
      showMeridian: false,
      defaultTime: false
    });
    _el.on("change", function () {
      if (_el.val().substr(-1) != "Z") {
        _el.val(_el.val() + "Z");
        _el.trigger("change");
      }
    });
  }
}


ko.bindingHandlers.textSqueezer = {
  init: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).text(ko.unwrap(value));
    $(element).textSqueezer({
      decimalPrecision: 2
    });
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).text(ko.unwrap(value));
    $(element).trigger("redraw");
  }
};


ko.toJSONObject = function (koObj) {
  return JSON.parse(ko.toJSON(koObj));
}

ko.bindingHandlers.aceEditor = {
    init: function (element, valueAccessor) {
      var _el = $(element);
      var _options = ko.unwrap(valueAccessor());
      var _onBlur = _options.onBlur || function () {};
      var _onChange = _options.onChange || function () {};
      _el.text(_options.value());
      ace.require("ace/ext/language_tools");
      var editor = ace.edit(element);
      editor.session.setMode(_options.mode());
      editor.setTheme($.totalStorage("hue.ace.theme") || "ace/theme/clouds");
      editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        showGutter: false
      });
      editor.on("blur", function () {
        _options.value(editor.getValue());
        _onBlur(editor);
      });
      editor.on("change", function () {
        _onChange(editor);
      });
      editor.$blockScrolling = Infinity
      element.editor = editor;
      element.editor.originalCompleters = editor.completers;
    },
    update: function (element, valueAccessor) {
      var _options = ko.unwrap(valueAccessor());
      if (element.editor) {
        element.editor.completers = element.editor.originalCompleters.slice();
        _options.extraCompleters().forEach(function (complete) {
          element.editor.completers.push(complete);
        });
      }
    }
  }