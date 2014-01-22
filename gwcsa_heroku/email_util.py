import logging
import urllib
import urllib2
import sys
import traceback

from django.conf import settings
from django.template.loader import render_to_string

from gwcsa_heroku.models import *

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
        logging.error("SendGrid email failed with status=%s" % status_code)
        logging.error(result.geturl())
        logging.error(result.info())
    else:
        logging.debug("Successfully sent email '%s' to '%s' through SendGrid." % (to_email, subject))

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
        logging.error(traceback.format_exc())

def send_workshift_confirmation_email(member):
    member_shifts = MemberWorkShift.objects.filter(member=member)
# TODO: need to verify that member_workshifts.count() > 0

    date_times = [(ms.workshift_date_time.date, ms.workshift_date_time.start_time) \
        for ms in member_shifts]

    values = {
        "current_season": CURRENT_SEASON,
        "member": member,
        "shift": member_shifts[0].workshift_date_time.shift,
        "date_times": date_times,
    }

    subject = "Your %s GWCSA Work Shifts" % CURRENT_SEASON
    send_email(member.email, member.name, subject, "email/confirmation.txt", values)

