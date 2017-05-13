from datetime import time
import logging

from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.decorators import *
from gwcsa_heroku.email_util import send_ab_week_assignment_email
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *
from gwcsa_heroku.util import *

logger = logging.getLogger(__name__)

def get_total(members, member=None):
    total = [0]*4
    for m in members:
        total = get_tplus(getattr(m, "biweekly_share_counts"), total)

    return total if not member else \
        get_tplus(getattr(member, "biweekly_share_counts"), total)

def get_tplus(t, s):
    return [sum(c) for c in zip(*(t, s))]

def get_tminus(t, s):
    return [x - y for x, y in zip(*(t, s))]

def get_diff(t1, t2):
    return sum([abs(x-y) for x, y in zip(*(t1, t2))])

# assign A/B week, location by location
@login_required
@handle_view_exception
def init_assigned_week(request):
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

        # initialize our a and b weeks of members
        a_week = [m for m in biweekly_members \
            if m.get_assigned_week_simplified() == A_WEEK or getattr(m, "a_week")]
        b_week = [m for m in biweekly_members \
            if m.get_assigned_week_simplified() == B_WEEK]
        logger.debug("init => a week: %s, b week: %s" % (get_total(a_week), get_total(b_week)))

        # assign members without a distribution week
        for m in [m for m in biweekly_members if not m in a_week and not m in b_week]:
            diff_a = get_diff(get_total(a_week, m), get_total(b_week))
            diff_b = get_diff(get_total(a_week), get_total(b_week, m))
            if diff_a <= diff_b:
                a_week.append(m)
                m.set_assigned_week(A_WEEK)
            else:
                b_week.append(m)
                m.set_assigned_week(B_WEEK)

        logger.debug("final => a week: %s, b week: %s" % (get_total(a_week), get_total(b_week)))

    return render_to_response("base.html",
        RequestContext(request, { })
    )

@login_required
@handle_view_exception
def set_is_weekly(request):
    members = Member.objects.filter(season__name=CURRENT_SEASON)
    for member in members:
        member.is_weekly = Share.objects.filter(member=member,frequency=WEEKLY).count() > 0
        member.has_biweekly = Share.objects.filter(member=member,frequency=BIWEEKLY).count() > 0
        member.save()

    return render_to_response("base.html",
        RequestContext(request, { })
    )



