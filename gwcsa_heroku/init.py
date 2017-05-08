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

def assign_distribution_week(members):
    # NOTE: this doesn't take share counts into account
    # until the remainder of the members are assigned. It's only looking at
    # number of members assigned to A vs. B. Probably okay given that almost
    # no one signs up for > 1 veggie share

    # initialize our a and b weeks of members
    a_week = [m for m in members if m.assigned_week == A_WEEK or getattr(m, "a_week")]
    b_week = [m for m in members if m.assigned_week == B_WEEK]
    logger.debug("init => a week: %s, b week: %s" % (get_total(a_week), get_total(b_week)))

    # members still awaiting assignment
    members = [m for m in members \
        if not getattr(m, "a_week") and not m.assigned_week in (A_WEEK, B_WEEK)]

    # split members into three groups
    # TODO: NEED TO REFACTOR!! NO WORKSHIFTS ANYMORE!
    a_week_workshift_members = []
    b_week_workshift_members = []
    no_workshift_members = [m for m in members]

    logger.debug("a ws [%s], b ws [%s], no ws [%s]" % \
        (len(a_week_workshift_members), len(b_week_workshift_members), len(no_workshift_members)))

    # if necessary, extend b_week with b week workshift members
    if len(b_week) < len(a_week):
        i = min(len(b_week_workshift_members), len(a_week) - len(b_week))
        b_week.extend(b_week_workshift_members[:i])
        b_week_workshift_members = b_week_workshift_members[i:]

    # if we didn't have enough b week workshift members to match mandatory
    # a week members, then see if we can make up the difference with no workshift
    # members
    if len(b_week) < len(a_week):
        i = min(len(a_week) - len(b_week), len(no_workshift_members))
        b_week.extend(no_workshift_members[:i])
        no_workshift_members = no_workshift_members[i:]

        logger.debug("after no workshift => a week: %s, b week: %s" % (get_total(a_week), get_total(b_week)))
        logger.debug("a ws [%s], b ws [%s], no ws [%s]" % \
            (len(a_week_workshift_members), len(b_week_workshift_members), len(no_workshift_members)))

    # at this point, one of the following situations is true:
    # 1) len(a_week) == len(b_week) and we might have non-zero lengths for one or more arrays
    # 2) len(a_week) > len(b_week) and we have only a week workshift members left

    if len(b_week) == len(a_week):
        if len(b_week_workshift_members) > 0:
            # shift equivalent numbers of a and b workshift members into a_week and b_week arrays
            # this will empty one of these arrays
            i = min(len(a_week_workshift_members), len(b_week_workshift_members))
            a_week.extend(a_week_workshift_members[:i])
            a_week_workshift_members = a_week_workshift_members[i:]
            b_week.extend(b_week_workshift_members[:i])
            b_week_workshift_members = b_week_workshift_members[i:]

        # now either a_week_workshift_members or b_week_workshift_members will be empty
        if len(no_workshift_members) > 0:
            if len(a_week_workshift_members) > 0 and len(b_week_workshift_members) == 0:
                i = min(len(a_week_workshift_members), len(no_workshift_members))
                a_week.extend(a_week_workshift_members[:i])
                a_week_workshift_members = a_week_workshift_members[i:]
                b_week.extend(no_workshift_members[:i])
                no_workshift_members = no_workshift_members[i:]
            if len(b_week_workshift_members) > 0 and len(a_week_workshift_members) == 0:
                i = min(len(b_week_workshift_members), len(no_workshift_members))
                a_week.extend(no_workshift_members[:i])
                no_workshift_members = no_workshift_members[i:]
                b_week.extend(b_week_workshift_members[:i])
                b_week_workshift_members = b_week_workshift_members[i:]

    logger.debug("before remainder => a week: %s, b week: %s" % (get_total(a_week), get_total(b_week)))
    logger.debug("a ws [%s], b ws [%s], no ws [%s]" % \
        (len(a_week_workshift_members), len(b_week_workshift_members), len(no_workshift_members)))

    # only one or of these arrays should be non-zero length
    members = a_week_workshift_members + b_week_workshift_members + no_workshift_members
    for m in members:
        diff_a = get_diff(get_total(a_week, m), get_total(b_week))
        diff_b = get_diff(get_total(a_week), get_total(b_week, m))
        if diff_a <= diff_b:
            a_week.append(m)
        else:
            b_week.append(m)

    logger.debug("final => a week: %s, b week: %s" % (get_total(a_week), get_total(b_week)))

    for m in a_week:
        if not m.assigned_week == A_WEEK:
            m.assigned_week = A_WEEK
            m.save()
    for m in b_week:
        if not m.assigned_week == B_WEEK:
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
            m.add_share_attributes()
            if sum(getattr(m, "biweekly_share_counts")) > 0:
                if m.day == WEDNESDAY:
                    wed_biweekly_members.append(m)
                if m.day == SATURDAY:
                    sat_biweekly_members.append(m)

    logger.debug("Assigning Saturday A/B Week")
    assign_distribution_week(sat_biweekly_members)
    logger.debug("Assigning Wednesday A/B Week")
    assign_distribution_week(wed_biweekly_members)

    return render_to_response("base.html",
        RequestContext(request, { })
    )

def __send_ab_assignment_email(member):
    if not member.assigned_week in (A_WEEK, B_WEEK):
        return False
    if not EmailLog.objects.filter(member=member)\
        .filter(subject__contains="Week Distribution Assignment").exists():
        return True

    email_timestamp = EmailLog.objects.filter(member=member)\
        .filter(subject__contains="Week Distribution Assignment")\
        .aggregate(Max("created_at"))["created_at__max"]
    week_assignment_timestamp = WeekAssignmentLog.objects.filter(member=member)\
        .aggregate(Max("created_at"))["created_at__max"]
    if not week_assignment_timestamp:
        return False

    return week_assignment_timestamp > email_timestamp

@login_required
@handle_view_exception
def email_assigned_week(request):
    members = Member.objects.filter(season__name=CURRENT_SEASON).filter(Q(assigned_week=A_WEEK) | Q(assigned_week=B_WEEK))
    members = [m for m in members if __send_ab_assignment_email(m)]

    if request.method == "POST":
        [send_ab_week_assignment_email(m) for m in members]
        members = []

    return render_to_response("admin_send_ab_assignment_emails.html",
        RequestContext(request, {
            "members": members,
        })
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



