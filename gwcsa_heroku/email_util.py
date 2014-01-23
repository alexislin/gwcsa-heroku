import logging
import urllib
import urllib2
import sys
import traceback

from django.conf import settings
from django.template.loader import render_to_string

from gwcsa_heroku.constants import *
from gwcsa_heroku.models import *

logger = logging.getLogger(__name__)

def send_email(to_email, to_name, subject, template_path, template_values):
    url = "https://sendgrid.com/api/mail.send.json"

    data = {}
    data["api_user"] = "williamsburgcsa"
    data["api_key"] = "kohlrabi"
    data["to"] = to_email
    data["toname"] = to_name
    data["from"] = "info@gwcsa.org"
    data["fromname"] = "Greenpoint Williamsburg CSA"
    data["subject"] = subject
    data["text"] = render_to_string(template_path, template_values)

    # send all emails to admin email when developing or debugging
    if settings.DEBUG:
        data["to"] = "admin+testing@gwcsa.org"
        data["toname"] = "GWCSA Admin - Test Emails"

    form_data = urllib.urlencode(data)

    headers = {}
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = urllib2.Request(url, form_data, headers)
    result = urllib2.urlopen(request)

    status_code = result.getcode()
    if status_code <> 200:
        logger.error("SendGrid email failed with status=%s" % status_code)
        logger.error(result.geturl())
        logger.error(result.info())
    else:
        logger.debug("Successfully sent email '%s' to '%s' through SendGrid." % (to_email, subject))

    EmailLog.objects.create(to_email=to_email, to_name=to_name, subject=subject, status_code=status_code)

def send_exception_email(url, args, stack_trace):
    try:
        values = {
            "url": url,
            "args": args,
            "stack_trace": stack_trace,
        }

        subject = "Exception for url: %s" % url
        send_email("admin@gwcsa.org", "GWCSA Admin", subject, "email/exception.txt", values)
    except:
        # don't want to throw an exception when trying to send an exception email...
        # that would only make things worse
        logger.error(traceback.format_exc())

def __add_member_workshift_values(member, values):
    values["member"] = member

    member_shifts = MemberWorkShift.objects.filter(member=member)
    if len(member_shifts) > 0:
        values["shift"] = member_shifts[0].workshift_date_time.shift
        values["date_times"] = [(ms.workshift_date_time.date, ms.workshift_date_time.start_time, ms.week) \
            for ms in member_shifts]
    else:
        values["shift"] = None
        values["date_times"] = []

    return values

def send_workshift_confirmation_email(member):
    values = __add_member_workshift_values(member, { "current_season": CURRENT_SEASON })

    subject = "Your %s GWCSA Work Shifts" % CURRENT_SEASON
    send_email(member.email, member.name, subject, "email/confirmation.txt", values)

def send_ab_week_assignment_email(member):
    if not member.assigned_week:
        logger.error("Can't send an A/B assignment email if the member isn't assigned.")
        return

    if member.day == WEDNESDAY:
        if member.is_weekly or member.assigned_week == A_WEEK:
            first_distribution_date = WED_A_DATES[0]
        elif member.assigned_week == B_WEEK:
            first_distribution_date = WED_B_DATES[0]
    elif member.day == SATURDAY:
        if member.is_weekly or member.assigned_week == A_WEEK:
            first_distribution_date = SAT_A_DATES[0]
        elif member.assigned_week == B_WEEK:
            first_distribution_date = SAT_B_DATES[0]

    values = {
        "first_distribution_date" : first_distribution_date.strftime("%A, %B %-d, %Y")
    }
    values = __add_member_workshift_values(member, values)

    subject = "GWCSA %s Week Distribution Assignment" % member.assigned_week
    send_email(member.email, member.name, subject, "email/ab_week_assignment.txt", values)

