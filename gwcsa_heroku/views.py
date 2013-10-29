from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *

@handle_view_exception
def index(request):
    foo = get_required_parameter(request, "foo")
    return render_to_response("base.html", RequestContext(request, {}))

@handle_view_exception
def workshift_selection(request):
    if request.method == "POST":
        # TODO!!
        return render_to_response("base.html")
    else:
        member = get_member(request)
        return render_to_response("workshift_selection.html",
            RequestContext(request, {
                "member" : member,
            })
        )

