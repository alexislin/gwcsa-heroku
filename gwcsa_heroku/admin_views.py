from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *

@handle_view_exception
@login_required
def members(request):
    if request.method == "POST":
        csv = request.FILES["csv-file"]

#TODO: validate file matches expected layout
#TODO: record last updated date to be displayed on page
        lines = csv.read().split("\n")

        for line in lines[1:]:
            if len(line.strip()) == 0:
                continue

            get_member_from_farmigo_csv_entry(line)
            '''

            # update member with subscription information
            member = Member.get_or_create_member(
                s.first_name, s.last_name, s.email
            )
            if s.is_different(member):
                logging.debug("Updating member: %s %s (%s)" % (
                        member.first_name, member.last_name, member.email
                ))

                # delete all previously specified shares, if any
                [share.delete() for share in member.shares]

                for c, q in s.weekly_shares.items():
                    Share(content=c, quantity=q, frequency=WEEKLY, member=member).put()
                for c, q in s.biweekly_shares.items():
                    Share(content=c, quantity=q, frequency=BIWEEKLY, member=member).put()

                member.phone = s.phone
                member.day = s.pickup_day
                member.farmigo_signup_date = s.signup_date
                member.farmigo_share_description = s.share_description
                member.is_weekly = member.has_shares_with_frequency(WEEKLY)
                member.is_biweekly = member.has_shares_with_frequency(BIWEEKLY)
                member.designated_week = member.infer_designated_week()
                member.put()
'''


    members = Member.objects.annotate(shift_count=Count("memberworkshift")).order_by("day", "last_name")
    return render_to_response("admin_members.html",
        RequestContext(request, {
            "current_season": CURRENT_SEASON,
            "members": members
        })
    )


