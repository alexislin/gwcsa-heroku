import json
import logging

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.decorators import *
from gwcsa_heroku.email_util import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *

logger = logging.getLogger(__name__)

@handle_view_exception
def contact(request):
    return render_to_response("contact.html",
        RequestContext(request, {})
    )

# for testing csv_xform bookmarklet, which is unrelated to this site:
# https://github.com/alexislin/csv-xform-bookmarklet
@handle_view_exception
def csv_xform(request):
    return render_to_response("csv_xform.html", RequestContext(request, {}))

@handle_view_exception
def signup_quiz(request):
    return render_to_response("quiz.html",
        RequestContext(request, {})
    )


