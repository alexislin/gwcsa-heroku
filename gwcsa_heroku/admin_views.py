from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *

@handle_view_exception
@login_required
def members(request):
    members = Member.objects.annotate(shift_count=Count("memberworkshift"))
    return render_to_response("admin_members.html",
        RequestContext(request, {
            "current_season": CURRENT_SEASON,
            "members": members
        })
    )


