import logging
import urllib
import urllib2
import sys

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
    data["text"] = "test" #TODO: self._render(template_path, template_values)
    form_data = urllib.urlencode(data)

    headers = {}
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = urllib2.Request(url, form_data, headers)
    result = urllib2.urlopen(request)

    status_code = result.getcode()
    print >> sys.stderr, "status code: %s" % status_code
    if status_code <> 200:
        logging.error("SendGrid email failed with status=%s" % status_code)
        logging.error(result.geturl())
        logging.error(result.info())
        print >> sys.stderr, result.info()
    else:
        logging.debug("Successfully sent email '%s' to '%s' through SendGrid." % (to_email, subject))

def send_workshift_confirmation_email():
    pass
