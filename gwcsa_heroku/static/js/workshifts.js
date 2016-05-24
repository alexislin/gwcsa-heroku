var WED_A_DATES = $.map($(wed_a_dates), function(d) { return getDateFromString(d); });
var WED_B_DATES = $.map($(wed_b_dates), function(d) { return getDateFromString(d); });
var SAT_A_DATES = $.map($(sat_a_dates), function(d) { return getDateFromString(d); });
var SAT_B_DATES = $.map($(sat_b_dates), function(d) { return getDateFromString(d); });

var gAvailableDatesByShiftId = {};

function getMemberId() {
  return $("form input[name='member_id']").first().val();
}

function getShiftIdFromDatePickerId(id) {
  // format of id is <shiftId>-shift-datepicker-<shiftNum>, e.g. 73-shift-datepicker-0
  var shiftId = id.substr(0, id.indexOf("-"));
  return parseInt(shiftId);
}

function shiftHasAvailableDates(jDiv) {
  var id = jDiv.find("input[name^='shift-datepicker-0']").attr("id");
  var shiftId = getShiftIdFromDatePickerId(id);
  var availableDates = gAvailableDatesByShiftId[shiftId];

  // will be undefined until it's first initialized... in this case,
  // treat it as though there are shifts
  return (typeof availableDates == "undefined") || availableDates.length > 0;
}

function getDateFromString(s) {
  var month = parseInt(s.substr(0, 2), 10) - 1;
  var day = parseInt(s.substr(2, 2), 10);
  var year = parseInt(s.substr(4), 10);

  return new Date(year, month, day);
}

function datesAreEqual(d1, d2) {
  return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
}

function isDateInDateArray(date, dates) {
  return $.map($(dates), function(d) { return datesAreEqual(d, date) ? true : null; }).length > 0;
}

function isAWeekDate(date) {
  return isDateInDateArray(date, WED_A_DATES.concat(SAT_A_DATES));
}

function isBWeekDate(date) {
  return isDateInDateArray(date, WED_B_DATES.concat(SAT_B_DATES));
}

function getAvailableDatesForShift(shiftId) {
  var memberId = getMemberId();

  $.ajax({
    url: "/ajax/get_available_dates_for_shift",
    type: "GET",
    data: { "memberId": memberId, "shiftId": shiftId, "t": new Date().getTime() },
    dataType: "json",
    timeout: 30000,
    success: function(data, textStatus, jqXHR) {
      gAvailableDatesByShiftId[shiftId] =
        $.map($(data.available_dates), function(d) { return getDateFromString(d); });
    },
    error: function(jqXHR, textStatus, errorThrown) {
      alert("Error getting dates for shift(id=" + shiftId + "): " + textStatus + ". " + errorThrown);
    }
  });
}

$(function() {
  $("input[name^='shift-datepicker-0']").each(function() {
    var shiftId = getShiftIdFromDatePickerId($(this).attr("id"));
    getAvailableDatesForShift(shiftId);
  });

  $("input[name^='shift-datepicker']").datepicker({
    minDate: new Date(2016, 5, 1), // June 1st
    maxDate: new Date(2016, 10, 30), // November 30th
    beforeShow: function(input, inst) {
      var shiftId = getShiftIdFromDatePickerId($(input).attr("id"));
      getAvailableDatesForShift(shiftId);

      return {
        beforeShowDay: function(date) {
          var validDates = gAvailableDatesByShiftId[shiftId];
          var isValid = $.map($(validDates), function(d) { return datesAreEqual(d, date) ? true : null; }).length > 0;
          if (isValid) {
            var cssClass = isAWeekDate(date) ? "a-week-shift-date" : "b-week-shift-date";
            return [true, cssClass, "Available date for shift."]
          }
          else {
            return [false, "invalid-shift-date", "No available shift on this date."];
          }
        }
      }
    }
  });

  var setAvailabilityOfShiftTimes = function(shiftDatePickerId) {
    var shiftDatePicker = $("#" + shiftDatePickerId);
    var shiftDiv = shiftDatePicker.closest("div.shift-date");
    var shiftTimePicker = shiftDiv.find("[name^='shift-timepicker']");

    // remove all times
    shiftTimePicker.find("option").remove();

    // parameters for ajax request
    var memberId = getMemberId();
    var shiftId = getShiftIdFromDatePickerId(shiftDatePickerId);
    var date = shiftDatePicker.val();

    if (date === "")
      return;

    $.ajax({
      url: "/ajax/get_available_times_for_shift_date",
      type: "GET",
      data: { "memberId": memberId, "shiftId": shiftId, "date": date, "t": new Date().getTime() },
      dataType: "json",
      timeout: 30000,
      context: shiftTimePicker.get(0),
      success: function(data, textStatus, jqXHR) {
        var availableTimes = data["available_times"];

        for (var i in availableTimes) {
          var availableTime = availableTimes[i];

          $(this).append("<option value=\"" + availableTime[0] + "\">" + availableTime[1] + "</option>");
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert("Error getting available times for shift(id=" + shiftId + ") date(" + date + "): " + textStatus + ". " + errorThrown);
      }
    });
  };

  $("input[name^='shift-datepicker']").each(function() {
    setAvailabilityOfShiftTimes($(this).attr("id"));
  });

  $("input[name^='shift-datepicker']").change(function() {
    setAvailabilityOfShiftTimes($(this).attr("id"));
  });

  $(".shift-date-selection").hide();

  $(".shift").click(function() {
    $(".shift").each(function() {
      $(this).removeClass("selected");
      $(this).removeClass("span-20");
      $(this).addClass("span-14");
      $(this).find(".shift-date-selection").hide();
    });
    if (shiftHasAvailableDates($(this))) {
      $(this).removeClass("span-14");
      $(this).addClass("selected");
      $(this).addClass("span-20");
      $(this).find(".shift-date-selection").show();
    }
    else {
      $(this).find(".shift-full").show();
      $(this).addClass("full");
    }
  });

  $(".shift").each(function() {
    if ($(this).hasClass("selected")) {
      $(this).trigger("click");
    }
  });

  $("form[name='shift-form']").submit(function() {
    var datePickers = $(this).find("[name^='shift-datepicker']");
    var timePickers = $(this).find("[name^='shift-timepicker']");

    if (datePickers.length != timePickers.length) {
      alert("Developer error - unequal number of date pickers and time pickers.");
      return false;
    }

    var dates = new Array(datePickers.length);

    datePickers.each(function() {
      var name = $(this).attr("name");
      var index = parseInt(name.substr(name.length - 1));
      dates[index] = $(this).val();
    });

    var times = new Array(timePickers.length);

    timePickers.each(function() {
      var name = $(this).attr("name");
      var index = parseInt(name.substr(name.length - 1));
      times[index] = $(this).val();
    });

    // verify there are no empty dates or times
    for (var i in dates) {
      if (dates[i].length == 0) {
        alert("Please select a date for all of your work shifts.");
        return false;
      }
      else if (!times[i] || /^\s*$/.test(times[i])) {
        alert("Please select a time for all of your work shifts.");
        return false;
      }
      else {
        // append time to the dates
        dates[i] += " " + times[i];
      }
    }

    dates = dates.sort();

    // verify they haven't chosen the same shift twice
    for (var i = 0; i < dates.length - 1; i++) {
      if (dates[i] === dates[i + 1]) {
        alert("Please select different date/times for your workshifts.");
        return false;
      }
    }

    return true;
  });

});
