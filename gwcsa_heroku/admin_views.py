import csv
import logging
import sys

from django.db.models import Count, F
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
            if week in (A_WEEK, B_WEEK):
                member.set_assigned_week(week)
            elif not week or week == "" and member.assigned_week <> None:
                member.set_assigned_week(None)
            else:
                raise Exception("Unknown value for 'week' parameter: '%s'" % week)

    return render_to_response("admin_memberdetail.html",
        RequestContext(request, {
            "member": member,
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
    members = Member.objects.filter(season__name=CURRENT_SEASON).extra(select={
        "weekly_veggie_count": SHARE_COUNT_QUERY % (VEGETABLES, WEEKLY),
        "biweekly_veggie_count": SHARE_COUNT_QUERY % (VEGETABLES, BIWEEKLY),
        "weekly_fruit_count": SHARE_COUNT_QUERY % (FRUIT, WEEKLY),
        "biweekly_fruit_count": SHARE_COUNT_QUERY % (FRUIT, BIWEEKLY),
        "weekly_egg_count": SHARE_COUNT_QUERY % (EGGS, WEEKLY),
        "biweekly_egg_count": SHARE_COUNT_QUERY % (EGGS, BIWEEKLY),
        "weekly_flower_count": SHARE_COUNT_QUERY % (FLOWERS, WEEKLY),
        "biweekly_flower_count": SHARE_COUNT_QUERY % (FLOWERS, BIWEEKLY),
        "veggie_summer_only_count": SHARE_COUNT_QUERY % (VEGETABLES_SUMMER_ONLY, WEEKLY),
        "personal_size_count": SHARE_COUNT_QUERY % (PERSONAL_SIZE, WEEKLY),
        "beer_count": SHARE_COUNT_QUERY % (BEER, NOT_APPLICABLE),
        "cheese_count": SHARE_COUNT_QUERY % (CHEESE, NOT_APPLICABLE),
        "meat_count": SHARE_COUNT_QUERY % (MEAT, NOT_APPLICABLE),
        "bread_count": SHARE_COUNT_QUERY % (BREAD, NOT_APPLICABLE),
        "plant_count": SHARE_COUNT_QUERY % (PLANTS, NOT_APPLICABLE),
    }).order_by("day", "first_name", "last_name")
    return render_to_response("admin_members.html",
        RequestContext(request, {
            "members": members
        })
    )

def __shares_contain(shares, content):
    if len(shares) == 0:
        return False
    return reduce(lambda x, y: x or y,
        [s.content == content and s.quantity > 0 for s in shares])

def __get_export_row(email, first_name, last_name, member):
    m = member
    row = [email, get_ascii(first_name), get_ascii(last_name)]
    row.append(m.day == WEDNESDAY and (m.is_weekly or m.assigned_week == A_WEEK))
    row.append(m.day == WEDNESDAY and (m.is_weekly or m.assigned_week == B_WEEK))
    row.append(m.day == SATURDAY and (m.is_weekly or m.assigned_week == A_WEEK))
    row.append(m.day == SATURDAY and (m.is_weekly or m.assigned_week == B_WEEK))

    shares = list(Share.objects.filter(member=m,quantity__gt=0))
    row.append(__shares_contain(shares, VEGETABLES))
    row.append(__shares_contain(shares, FRUIT))
    row.append(__shares_contain(shares, EGGS))
    row.append(__shares_contain(shares, FLOWERS))
    row.append(__shares_contain(shares, MEAT))
    row.append(__shares_contain(shares, CHEESE))
    row.append(__shares_contain(shares, PICKLES_AND_PRESERVES))
    row.append(__shares_contain(shares, BREAD))
    row.append(__shares_contain(shares, PLANTS))

    row.append(m.id)
    row.append(get_ascii(m.first_name))
    row.append(get_ascii(m.last_name))
    row.append(m.email)
    return row

@handle_view_exception
@login_required
def members_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gwcsa_export.csv"'

    writer = csv.writer(response, dialect=csv.excel)
    writer.writerow(["Email", "Fname", "Lname",
        "Week_A_Wed", "Week_B_Wed", "Week_A_Sat", "Week_B_Sat",
        "Vegetables", "Fruit", "Eggs", "Flowers",
        "Meat", "Cheese", "Pickles_Preserves", "Bread", "Plants",
        "MemberID", "Primary_Fname", "Primary_Lname", "Primary_Email"])

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
            "member_count": Member.objects.filter(season__name=CURRENT_SEASON).count(),
            "secondary_member_count": Member.objects \
                .filter(season__name=CURRENT_SEASON) \
                .exclude(secondary_email__isnull=True) \
                .exclude(secondary_email__exact="") \
                .exclude(secondary_email=F('email')).count(), # at least one member has matching primary and secondary info
        })
    )

@handle_view_exception
@login_required
def share_list(request):
    if request.method == "POST":
        day = get_required_parameter(request, "day")
        week = get_required_parameter(request, "week")
        share_type = get_required_parameter(request, "share_type")

        share_list = get_share_list(share_type, day, week)
        share_list = [(Member.objects.get(id=id), cnt) for id, cnt in share_list]

        return render_to_response("admin_sharelist.html",
            RequestContext(request, {
                "day": [d for c, d in DAYS if day == c][0],
                "week": week,
                "share_type": [d for c, d in SHARES if share_type == c][0],
                "num_shares": sum([x[1] for x in share_list]),
                "share_list": share_list
            })
        )

    return render_to_response("admin_sharelistmaker.html",
        RequestContext(request, {
            "days": DAYS,
            "weeks": WEEK[:-1],
            "share_types": SHARES[:],
        })
    )


