from datetime import time
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *

logger = logging.getLogger(__name__)


def get_tplus(t, s):
    return [sum(c) for c in zip(*(t, s))]

def get_tminus(t, s):
    return [x - y for x, y in zip(*(t, s))]

def get_diff(t1, t2):
    return sum([abs(x-y) for x, y in zip(*(t1, t2))])

def assign_distribution_week(members):
    a_week = []
    a_week_totals = [0]*4
    b_week = []
    b_week_totals = [0]*4
    logger.info("start assignment")

    # initial sorting
    for m in members:
        share_count = getattr(m, "biweekly_share_counts")
        a = get_tplus(a_week_totals, share_count)
        b = get_tplus(b_week_totals, share_count)

        workshift_week = m.get_workshift_week()
        if getattr(m, "a_week"):
            a_week.append(m)
            a_week_totals = a
        elif workshift_week == A_WEEK:
            a_week.append(m)
            a_week_totals = a
        elif workshift_week == B_WEEK:
            b_week.append(m)
            b_week_totals = b
        else:
            if get_diff(a, b_week_totals) <= get_diff(b, a_week_totals):
                a_week.append(m)
                a_week_totals = a
            else:
                b_week.append(m)
                b_week_totals = b

    # make some swaps if necessary to balance numbers
    for ma in a_week:
        # don't swap if this member must be A week (i.e. has meat, cheese or P&P)
        if not getattr(ma, "a_week"):
            for mb in b_week:
                a = getattr(ma, "biweekly_share_counts")
                b = getattr(mb, "biweekly_share_counts")

                # get totals if shares were swapped
                ta_delta = get_tplus(get_tminus(a_week_totals, a), b)
                tb_delta = get_tplus(get_tminus(b_week_totals, b), a)

                if get_diff(a_week_totals, b_week_totals) > get_diff(ta_delta, tb_delta):
                    a_week.remove(ma)
                    b_week.append(ma)
                    b_week.remove(mb)
                    a_week.append(mb)

                    a_week_totals = ta_delta
                    b_week_totals = tb_delta
                    break

    for m in a_week:
        m.assigned_week = A_WEEK
        m.save()
    for m in b_week:
        m.assigned_week = B_WEEK
        m.save()

@login_required
@handle_view_exception
def init_assigned_week(request):
    sat_biweekly_members = []
    wed_biweekly_members = []

    for m in Member.objects.filter(season__name=CURRENT_SEASON):
        if not m.has_biweekly:
            m.assigned_week = WEEKLY
            m.save()
        else:
            # only assign A/B weeks to members that have at least one biweekly
            # share (veggies, fruit, eggs or flowers)

            # TODO: DO NOT ASSIGN WEEK IF ALREADY ASSIGNED
            m.add_share_attributes()
            if sum(getattr(m, "biweekly_share_counts")) > 0:
                if m.day == WEDNESDAY:
                    wed_biweekly_members.append(m)
                if m.day == SATURDAY:
                    sat_biweekly_members.append(m)

    assign_distribution_week(sat_biweekly_members)
    assign_distribution_week(wed_biweekly_members)

    return render_to_response("base.html",
        RequestContext(request, {
            "current_season": CURRENT_SEASON,
        })
    )

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

@login_required
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


