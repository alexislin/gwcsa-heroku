import json

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *

@handle_view_exception
def index(request):
    foo = get_required_parameter(request, "foo")
    return render_to_response("base.html",
        RequestContext(request, {
            "current_season": CURRENT_SEASON,
        })
    )

@handle_view_exception
def workshift_selection(request):
    if request.method == "POST":
        # TODO!!
        return render_to_response("base.html")
    else:
        member = get_member(request, "member_id")

        shift_id = None
        shift_dates = []
        shift_times = []

        for shift in MemberWorkShift.objects.filter(member=member):
            shift_id = shift.get_id()
            shift_dates.append(shift.date.strftime("%m/%d/%Y"))
            shift_times.append(shift.shift_time.start.strftime("%H%M"))

        shifts = WorkShift.objects.filter(season=Season.objects.get(name=CURRENT_SEASON)).values()
        for shift in shifts:
            shift["times"] = WorkShiftDateTime.objects.filter(shift__id=shift["id"]) \
                .distinct("start_time").values("start_time", "end_time")

        return render_to_response("workshift_selection.html",
            RequestContext(request, {
                "current_season": CURRENT_SEASON,
                "workshifts": shifts,
                "member": member,
                "shift_id": shift_id,
                "shift_dates": shift_dates,
                "shift_times": shift_times,
            })
        )

