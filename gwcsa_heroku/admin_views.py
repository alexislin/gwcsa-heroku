from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *


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
    members = Member.objects.annotate(
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
            "current_season": CURRENT_SEASON,
            "members": members
        })
    )


