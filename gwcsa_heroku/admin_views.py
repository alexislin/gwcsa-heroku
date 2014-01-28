import csv
import logging
import sys

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from gwcsa_heroku.decorators import *
from gwcsa_heroku.email_util import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *

logger = logging.getLogger(__name__)

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
            elif week == B_WEEK and not member.assigned_week == B_WEEK:
                member.assigned_week = B_WEEK
                member.save()
            elif not week or week == "" and member.assigned_week <> None:
                member.assigned_week = None
                member.save()
        if action == "send":
            send_ab_week_assignment_email(member)

    shift_date_times = [s.workshift_date_time for s in MemberWorkShift.objects.filter(member=member)]
    shift = None if len(shift_date_times) == 0 else shift_date_times[0].shift
    email_log = EmailLog.objects.filter(member=member).order_by("-created_at")

    return render_to_response("admin_memberdetail.html",
        RequestContext(request, {
            "member": member,
            "shift": shift,
            "shift_date_times": shift_date_times,
            "email_log": email_log,
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

def __get_export_row(email, first_name, last_name, member):
    m = member
    row = [email, get_ascii(first_name), get_ascii(last_name), get_ascii(m.name)]
    row.append(m.day == WEDNESDAY and (m.is_weekly or m.assigned_week == A_WEEK))
    row.append(m.day == WEDNESDAY and (m.is_weekly or m.assigned_week == B_WEEK))
    row.append(m.day == SATURDAY and (m.is_weekly or m.assigned_week == A_WEEK))
    row.append(m.day == SATURDAY and (m.is_weekly or m.assigned_week == B_WEEK))
    row.append(Share.objects.filter(member=m,content=VEGETABLES,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=FRUIT,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=EGGS,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=FLOWERS,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=MEAT,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=CHEESE,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=PICKLES_AND_PRESERVES,quantity__gt=0).exists())
    row.append(Share.objects.filter(member=m,content=PLANTS,quantity__gt=0).exists())

    shifts = MemberWorkShift.objects.filter(member=m)
    [row.append("" if len(shifts) <= i else shifts[i].date.strftime("%-m/%-d/%Y")) \
        for i in range(3)]
    [row.append("" if len(shifts) <= i else shifts[i]) for i in range(3)]

    row.append(m.id)
    return row

@handle_view_exception
@login_required
def members_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gwcsa_export.csv"'

    writer = csv.writer(response, dialect=csv.excel)
    writer.writerow(["Email", "Fname", "Lname", "Primary",
        "Week_A_Wed", "Week_B_Wed", "Week_A_Sat", "Week_B_Sat",
        "Vegetables", "Fruit", "Eggs", "Flowers",
        "Meat", "Cheese", "Pickles_Preserves", "Plants",
        "Workshift_Date_1", "Workshift_Date_2", "Workshift_Date_3",
        "Workshift_Details_1", "Workshift_Details_2", "Workshift_Details_3",
        "MemberID"])

    for m in Member.objects.filter(season__name=CURRENT_SEASON):
        writer.writerow(__get_export_row(m.email, m.first_name, m.last_name, m))
        if m.secondary_email:
            writer.writerow(__get_export_row(m.secondary_email,
                m.secondary_first_name, m.secondary_last_name, m))

    return response


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


