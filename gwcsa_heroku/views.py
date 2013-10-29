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
    return render_to_response("base.html", RequestContext(request, {}))

@handle_view_exception
def workshift_selection(request):
    if request.method == "POST":
        # TODO!!
        return render_to_response("base.html")
    else:
        member = get_member(request)

        shift_id = None
        shift_dates = []
        shift_times = []

        for shift in MemberWorkShift.objects.filter(member=member):
            shift_id = shift.get_id()
            shift_dates.append(shift.date.strftime("%m/%d/%Y"))
            shift_times.append(shift.shift_time.start.strftime("%H%M"))

        shifts = WorkShift.objects.filter(season=Season.objects.get(name=CURRENT_SEASON))

        available_dates_by_shift_id = {}
        for shift in shifts:
            #dates = [d.strftime("%m%d%Y") \
            #    for d in shift.get_available_dates_for_member(member.key().id())]
            dates = [s.date.strftime("%m%d%Y") for s in WorkShiftDateTime.objects.filter(shift=shift)]
            available_dates_by_shift_id[shift.id] = dates

        member = get_member(request)
        return render_to_response("workshift_selection.html",
            RequestContext(request, {
                "workshifts": shifts,
                "member": member,
                "shift_id": shift_id,
                "shift_dates": shift_dates,
                "shift_times": shift_times,
                "available_dates_by_shift_id": json.dumps(available_dates_by_shift_id),
            })
        )

