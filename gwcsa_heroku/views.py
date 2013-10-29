from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from decorators import *
from models import *

@handle_view_exception
def index(request):
    if not "foo" in request.GET:
        raise Exception("no foo variable!!")
    return render_to_response("base.html", RequestContext(request, {}))

