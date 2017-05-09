from gwcsa_heroku.models import *

import re
import string
import sys
import urllib
import urlparse

def get_required_parameter(request, name):
    if name in request.GET:
        return request.GET[name]
    if name in request.POST:
        return request.POST[name]
    raise Exception("Missing '%s' parameter." % name)

def get_parameter(request, name, default=None):
    if name in request.GET:
        return request.GET[name]
    if name in request.POST:
        return request.POST[name]
    return default

def get_member(request, member_id_param_name):
    member_id = get_parameter(request, member_id_param_name)

    if member_id:
        return Member.objects.get(id=int(member_id))
    else:
        first_name = get_parameter(request, "firstname")
        last_name = get_parameter(request, "lastname")
        email = get_parameter(request, "email")

        # handle emails with + signs
        if re.search("\s+", email):
            qs = string.replace(request.META["QUERY_STRING"], "+", urllib.quote("+"))
            d = urlparse.parse_qs(qs)
            email = d["email"][0]

        if not first_name or not last_name or not email:
            msg = "Missing info: firstname='%s' lastname='%s' email='%s'."
            msg = msg % (first_name, last_name, email)
            raise Exception(msg)
        else:
            return Member.get_or_create_member(first_name, last_name, email)

