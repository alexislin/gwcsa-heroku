import csv
import logging
import sys
import zipfile
import StringIO

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
        if "upload-button" in request.POST:
            csv = request.FILES["csv-file"]

            lines = csv.read().split("\n")
            for line in lines[1:]:
                if len(line.strip()) > 0:
                    add_update_member_from_farmigo_csv_entry(line)
        elif "assign-week-button" in request.POST:
            __assign_weeks()

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

def __get_total(members, member=None):
    total = [0]*4
    for m in members:
        total = __get_tplus(getattr(m, "biweekly_share_counts"), total)

    return total if not member else \
    __get_tplus(getattr(member, "biweekly_share_counts"), total)

def __get_tplus(t, s):
    return [sum(c) for c in zip(*(t, s))]

def __get_diff(t1, t2):
    return sum([abs(x-y) for x, y in zip(*(t1, t2))])

def __assign_weeks():
    for location, description in DAYS:
        logger.debug("Assigning A/B Week - %s" % description)

        # find biweekly members for this location
        biweekly_members = []
        for m in Member.objects.filter(season__name=CURRENT_SEASON,day=location):
            if m.is_weekly and not m.has_biweekly:
                m.set_assigned_week(WEEKLY)
            else:
                # only assign A/B weeks to members that have at least one biweekly
                # share (veggies, fruit, eggs or flowers)
                m.add_share_attributes()
                if sum(getattr(m, "biweekly_share_counts")) > 0:
                    biweekly_members.append(m)
                if getattr(m, "a_week") and not m.assigned_week:
                    m.set_assigned_week(A_WEEK)

        # initialize our a and b weeks of members
        a_week = [m for m in biweekly_members if m.get_assigned_week_simplified() == A_WEEK]
        b_week = [m for m in biweekly_members if m.get_assigned_week_simplified() == B_WEEK]

        # assign members without a distribution week
        for m in [m for m in biweekly_members if not m in a_week and not m in b_week]:
            diff_a = __get_diff(
                __get_total(a_week, m),
                __get_total(b_week)
            )
            diff_b = __get_diff(
                __get_total(a_week),
                __get_total(b_week, m)
            )
            if diff_a <= diff_b:
                a_week.append(m)
                m.set_assigned_week(A_WEEK)
            else:
                b_week.append(m)
                m.set_assigned_week(B_WEEK)


@handle_view_exception
@login_required
def members_export(request):
    response = HttpResponse(content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="eve_exports.zip"'

    s = StringIO.StringIO()
    writer = csv.writer(s, dialect=csv.excel)
    writer.writerow(["First Name", "Last Name", "Signup Date", "Email",
        "Phone", "Week", "V(A)", "V(B)", "V(?)", "Fr(A)", "Fr(B)", "Fr(?)",
        "E(A)", "E(B)", "E(?)", "Fl(A)", "Fl(B)", "Fl(?)", "Vso", "PS",
        "Br", "C", "M", "Bd", "Share Description"])
    for m in Member.objects.filter(season__name=CURRENT_SEASON):
        writer.writerow(m.get_export_row())

    zf = zipfile.ZipFile(response, mode="w", compression=zipfile.ZIP_DEFLATED,)
    try:
        zf.writestr("locations/my_export.csv", s.getvalue())
    finally:
        zf.close()

    return response


@handle_view_exception
@login_required
def summaries(request):
    location_ab_counts = []
    location_counts = []
    totals = [0] * 11
    for location, desc in DAYS:
        if location not in (WEDNESDAY, SATURDAY):
            count = get_share_count(location)
            location_counts.append((desc, count))
            totals = [x + y for x, y in zip(count, totals)]

            ab_count = get_ab_count_for_location(location)
            location_ab_counts.append((desc, ab_count))

    location_counts.append(("Total", totals))

    return render_to_response("admin_summaries.html",
        RequestContext(request, {
            "location_counts": location_counts,
            "location_ab_counts": location_ab_counts,
            "member_count": Member.objects.filter(season__name=CURRENT_SEASON).count(),
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


