import logging
import urllib
import urllib2
import sys
import traceback

from django.conf import settings
from django.template.loader import render_to_string

from gwcsa_heroku.models import *
from gwcsa_heroku.str_util import get_ascii

logger = logging.getLogger(__name__)

def send_email_to_member(member, subject, template_path, template_values):
    to_email = member.email if not member.secondary_email else \
        [member.email, member.secondary_email]
    to_name = get_ascii(member.name) if not member.secondary_email else \
        [get_ascii(member.name), get_ascii(member.secondary_name)]
    send_email(to_email, to_name, subject, template_path, template_values, member)

def send_email(to_email, to_name, subject, template_path, template_values, member=None):
    url = "https://sendgrid.com/api/mail.send.json"

    data = {}
    data["api_user"] = settings.SENDGRID_API_USER
    data["api_key"] = settings.SENDGRID_API_KEY
    data["bcc"] = "admin@gwcsa.org" if not settings.DEBUG else "admin+testing@gwcsa.org"
    data["from"] = "info@gwcsa.org"
    data["fromname"] = "Greenpoint Williamsburg CSA"
    data["subject"] = subject
    data["text"] = render_to_string(template_path, template_values)

    # handle multiple recipients
    if isinstance(to_email, list):
        form_data = urllib.urlencode(data)

        for i in range(len(to_email)):
            data = {
                "to[]": to_email[i] if not settings.DEBUG else "admin+testing@gwcsa.org",
                "toname[]": to_name[i] if not settings.DEBUG else "GWCSA Admin - Test Emails [%s]" % i,
            }
            form_data += "&%s" % urllib.urlencode(data)
    else:
        data["to"] = to_email if not settings.DEBUG else "admin+testing@gwcsa.org"
        data["toname"] = to_name if not settings.DEBUG else "GWCSA Admin - Test Emails"
        form_data = urllib.urlencode(data)

    headers = {}
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    status_code = 200
    try:
        request = urllib2.Request(url, form_data, headers)
        result = urllib2.urlopen(request)
        logger.debug("Successfully sent email '%s' to '%s' through SendGrid." % (subject, to_email))
    except urllib2.HTTPError as e:
        status_code = e.code
        logger.error("SendGrid email failed with status=%s" % status_code)
        logger.error(url)
        logger.error(data)
        logger.error(e.read())

    if isinstance(to_email, list):
        for i in range(len(to_email)):
            EmailLog.objects.create(to_email=to_email[i], to_name=to_name[i], subject=subject, status_code=status_code, member=member)
    else:
        EmailLog.objects.create(to_email=to_email, to_name=to_name, subject=subject, status_code=status_code, member=member)


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

def send_ab_week_assignment_email(member):
    if not member.assigned_week:
        logger.error("Can't send an A/B assignment email if the member isn't assigned.")
        return

    logger.warning("A/B assignment email disabled.")


