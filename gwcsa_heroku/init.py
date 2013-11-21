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
        if note:
            shift.note = note
            shift.save()

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

    __init_shift(
        day=SATURDAY,
        name="Distribution Shift",
        location="McCarren Park",
        location2="(next to dog run and community garden)",
        num_required_per_member=1,
        timeslots=[(time(8, 15, 0), time(12, 00, 0))],
        num_members_required=[6, 5]
    )

    __init_shift(
        day=SATURDAY,
        name="Garden of Eve Farmstand Shift",
        location="McCarren Park",
        location2="(next to dog run and community garden)",
        num_required_per_member=1,
        timeslots=[(time(7, 30, 0), time(10, 30, 0)), (time(10, 30, 0), time(13, 30, 0))],
        num_members_required=[1, 1]
    )

    __init_shift(
        day=SATURDAY,
        name="Soup Kitchen Driver",
        location="McCarren Park",
        location2="(next to dog run and community garden)",
        num_required_per_member=3,
        timeslots=[(time(11, 45, 0), time(12, 15, 0))],
        num_members_required=[1, 1],
        note="Must have own car. Soup kitchen is on Milton Street in Greenpoint.",
    )

    return render_to_response("base.html",
        RequestContext(request, {
            "current_season": CURRENT_SEASON,
        })
    )


