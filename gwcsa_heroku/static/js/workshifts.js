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

function setAvailableDatesForShift(shiftId, availableDates) {
  dates = []
  for (var i in availableDates) {
    var d = availableDates[i];

    var month = parseInt(d.substr(0, 2), 10) - 1;
    var day = parseInt(d.substr(2, 2), 10);
    var year = parseInt(d.substr(4), 10);

    dates.push(new Date(year, month, day));
  }
  gAvailableDatesByShiftId[shiftId] = dates;
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
      setAvailableDatesForShift(shiftId, data.available_dates);
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
    minDate: new Date(2014, 5, 1), // June 1st
    maxDate: new Date(2014, 10, 30), // November 30th
    beforeShow: function(input, inst) {
      var shiftId = getShiftIdFromDatePickerId($(input).attr("id"));
      getAvailableDatesForShift(shiftId);

      return {
        beforeShowDay: function(date) {
          var validDates = gAvailableDatesByShiftId[shiftId];

          for (var i in validDates) {
            var equal =
                date.getFullYear() === validDates[i].getFullYear() &&
                date.getMonth() === validDates[i].getMonth() &&
                date.getDate() === validDates[i].getDate();

            if (equal)
              return [true, "", "Available date for shift."]
          }
          return [false, "invalid-shift-date", "No available shift on this date."];
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
