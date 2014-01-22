import sys

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *


@handle_view_exception
@login_required
def member_detail(request, id):
    member = Member.objects.get(id=id)

    if request.method == "POST":
        action = get_parameter(request, "action")
        if action == "delete":
            member.delete()
            return redirect("gwcsa_heroku.admin_views.members")
        if action == "update":
            week = get_parameter(request, "week")
            if week == A_WEEK and not member.assigned_week == A_WEEK:
                member.assigned_week = A_WEEK
                member.save()
            if week == B_WEEK and not member.assigned_week == B_WEEK:
                member.assigned_week = B_WEEK
                member.save()

    shift_date_times = [s.workshift_date_time for s in MemberWorkShift.objects.filter(member=member)]
    shift = None if len(shift_date_times) == 0 else shift_date_times[0].shift

    return render_to_response("admin_memberdetail.html",
        RequestContext(request, {
            "member": member,
            "shift": shift,
            "shift_date_times": shift_date_times,
        })
    )

SHARE_COUNT_QUERY = """
    SELECT gwcsa_heroku_share.quantity
      FROM gwcsa_heroku_share
     WHERE gwcsa_heroku_share.member_id = gwcsa_heroku_member.id
       AND gwcsa_heroku_share.content = '%s'
       AND gwcsa_heroku_share.frequency = '%s'
"""

@handle_view_exception
@login_required
def members(request):
    if request.method == "POST":
        csv = request.FILES["csv-file"]

        lines = csv.read().split("\n")
        for line in lines[1:]:
            if len(line.strip()) > 0:
                add_update_member_from_farmigo_csv_entry(line)

    # query member data for page
    members = Member.objects.filter(season__name=CURRENT_SEASON).annotate(
        shift_count=Count("memberworkshift")
    ).extra(select={
        "weekly_veggie_count": SHARE_COUNT_QUERY % (VEGETABLES, WEEKLY),
        "biweekly_veggie_count": SHARE_COUNT_QUERY % (VEGETABLES, BIWEEKLY),
        "weekly_fruit_count": SHARE_COUNT_QUERY % (FRUIT, WEEKLY),
        "biweekly_fruit_count": SHARE_COUNT_QUERY % (FRUIT, BIWEEKLY),
        "weekly_egg_count": SHARE_COUNT_QUERY % (EGGS, WEEKLY),
        "biweekly_egg_count": SHARE_COUNT_QUERY % (EGGS, BIWEEKLY),
        "weekly_flower_count": SHARE_COUNT_QUERY % (FLOWERS, WEEKLY),
        "biweekly_flower_count": SHARE_COUNT_QUERY % (FLOWERS, BIWEEKLY),
        "cheese_count": SHARE_COUNT_QUERY % (CHEESE, NOT_APPLICABLE),
        "meat_count": SHARE_COUNT_QUERY % (MEAT, NOT_APPLICABLE),
        "pickles_count": SHARE_COUNT_QUERY % (PICKLES_AND_PRESERVES, NOT_APPLICABLE),
        "plant_count": SHARE_COUNT_QUERY % (PLANTS, NOT_APPLICABLE),
    }).order_by("day", "last_name")
    return render_to_response("admin_members.html",
        RequestContext(request, {
            "members": members
        })
    )

@handle_view_exception
@login_required
def summaries(request):
    return render_to_response("admin_summaries.html",
        RequestContext(request, {
            "wed_counts": get_share_count(WEDNESDAY),
            "sat_counts": get_share_count(SATURDAY),
            "veggie_counts": get_ab_count_for_share(VEGETABLES),
            "fruit_counts": get_ab_count_for_share(FRUIT),
            "egg_counts": get_ab_count_for_share(EGGS),
            "flower_counts": get_ab_count_for_share(FLOWERS),
            "weekly_counts": get_weekly_count_for_shares(),
        })
    )

@handle_view_exception
@login_required
def workshifts(request):
    dates = [o.date for o in WorkShiftDateTime.objects.filter(shift__season__name=CURRENT_SEASON)]
    dates = sorted(list(set(dates)))

    shifts = WorkShift.objects.filter(season__name=CURRENT_SEASON)

    shifts_by_date = []

    for date in dates:
        shifts_by_date.append((date,[]))

        for shift in shifts:
            for wdt in WorkShiftDateTime.objects.filter(date=date,shift=shift).order_by("start_time"):
                members = [ms.member for ms in \
                    MemberWorkShift.objects.filter(workshift_date_time=wdt)]

                shifts_by_date[-1][1].append({
                    "name": shift.name,
                    "time": wdt.start_time,
                    "members": members,
                    "num_members_required": wdt.num_members_required,
                    "full": len(members) >= wdt.num_members_required
                })

    return render_to_response("admin_workshifts.html",
        RequestContext(request, {
            "shifts_by_date": shifts_by_date
        })
    )


