from datetime import time

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *

def __init_shift(day, name, location, location2, num_required_per_member,
    timeslots, num_members_required, note=None):

    season=Season.objects.get(name=CURRENT_SEASON)

    shifts = WorkShift.objects.filter(season=season).filter(name=name).filter(day=day)
    if not shifts.exists():
        shift = WorkShift.objects.create(
            season=season,
            day=day,
            name=name,
            location=location,
            location2=location2,
            num_required_per_member=num_required_per_member
        )

    else:
        shift = shifts[0]

    for date in get_distro_dates(day):
        required = num_members_required[0] \
            if distro_date_is_week(date, A_WEEK) else num_members_required[1]

        shifts = WorkShiftDateTime.objects.filter(shift=shift).filter(date=date)
        for start_time, end_time in timeslots:
            if not shifts.filter(start_time=start_time).exists():
                s = WorkShiftDateTime.objects.create(
                    shift=shift,
                    date=date,
                    num_members_required=required,
                    start_time=start_time,
                    end_time=end_time,
                )

@handle_view_exception
def init_workshift(request):
    __init_shift(
        day=WEDNESDAY,
        name="Distribution Shift",
        location="Lutheran Church of the Messiah",
        location2="129 Russell St, Greenpoint",
        num_required_per_member=2,
        timeslots=[(time(17, 30, 0), time(19, 15, 0)), (time(18, 45, 0), time(20, 20, 0))],
        num_members_required=[5, 4]
    )

    __init_shift(
        day=WEDNESDAY,
        name="Soup Kitchen Driver",
        location="Lutheran Church of the Messiah",
        location2="129 Russell St, Greenpoint",
        num_required_per_member=3,
        timeslots=[(time(19, 45, 0), time(20, 15, 0))],
        num_members_required=[1, 1],
        note="Must have own car. Soup kitchen is on Milton Street in Greenpoint.",
    )


    return render_to_response("base.html",
        RequestContext(request, {
            "current_season": CURRENT_SEASON,
        })
    )


'''
        shift = WorkShift.all()
        shift = shift.filter("season =", CURRENT_SEASON)
        shift = shift.filter("name =", "Distribution Shift")
        shift = shift.filter("day =", SATURDAY)
        if not shift.get():
            shift = WorkShift(
                season=CURRENT_SEASON,
                day=SATURDAY,
                name="Distribution Shift",
                location="McCarren Park",
                location2="(next to dog run and community garden)",
                num_required_per_member=1,
                num_members_required_per_timeslot=5,
                first_day_of_season=SATURDAY_DATES[0],
                last_day_of_season=SATURDAY_DATES[-1],
                dates=SATURDAY_DATES
            )
            shift.put()
            WorkShiftTime(
                start=time(8, 30, 0),
                end=time(12, 15, 0),
                shift=shift
            ).put()

        shift = WorkShift.all()
        shift = shift.filter("season =", CURRENT_SEASON)
        shift = shift.filter("name =", "Garden of Eve Farmstand Shift")
        shift = shift.filter("day =", SATURDAY)
        if not shift.get():
            shift = WorkShift(
                season=CURRENT_SEASON,
                day=SATURDAY,
                name="Garden of Eve Farmstand Shift",
                location="Garden of Eve Stand",
                location2="McCarren Park Farmers Market",
                num_required_per_member=1,
                num_members_required_per_timeslot=1,
                first_day_of_season=SATURDAY_DATES[0],
                last_day_of_season=SATURDAY_DATES[-1],
                dates=SATURDAY_DATES
            )
            shift.put()
            WorkShiftTime(
                start=time(7, 30, 0),
                end=time(9, 30, 0),
                shift=shift
            ).put()
            WorkShiftTime(
                start=time(9, 30, 0),
                end=time(11, 30, 0),
                shift=shift
            ).put()
            WorkShiftTime(
                start=time(11, 30, 0),
                end=time(13, 30, 0),
                shift=shift
            ).put()

        shift = WorkShift.all()
        shift = shift.filter("season =", CURRENT_SEASON)
        shift = shift.filter("name =", "Soup Kitchen Driver")
        shift = shift.filter("day =", SATURDAY)
        if not shift.get():
            shift = WorkShift(
                season=CURRENT_SEASON,
                day=SATURDAY,
                name="Soup Kitchen Driver",
                location="McCarren Park",
                location2="(next to dog run and community garden)",
                note="Must have own car. Soup kitchen is on Milton Street in Greenpoint.",
                num_required_per_member=3,
                num_members_required_per_timeslot=1,
                first_day_of_season=SATURDAY_DATES[0],
                last_day_of_season=SATURDAY_DATES[-1],
                dates=SATURDAY_DATES
            )
            shift.put()
            WorkShiftTime(
                start=time(12, 00, 0),
                shift=shift
            ).put()

'''

