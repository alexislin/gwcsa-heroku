import json
import logging

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from gwcsa_heroku.constants import *
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
def workshift_selection(request):
    if request.method == "POST":
        member = get_member(request, "member_id")
        shift_id = int(get_required_parameter(request, "shift_id"))
        shift = WorkShift.objects.get(id=shift_id)

#TODO: validate that shifts selected are not already full

        # delete all previously selected work shifts, if any
        MemberWorkShift.objects.filter(member=member).delete()

        workshift_date_times = []
        for i in range(shift.num_required_per_member):
            shift_date = get_required_parameter(request, "shift-datepicker-%d" % i)
            shift_time = get_required_parameter(request, "shift-timepicker-%d" % i)

            w = WorkShiftDateTime.objects.get(
                shift=shift,
                date=datetime.strptime(shift_date, "%m/%d/%Y").date(),
                start_time=datetime.strptime(shift_time, "%H%M").time(),
            )
            MemberWorkShift.objects.create(member=member, workshift_date_time=w)
            workshift_date_times.append(w)

        # ensure workshift selection doesn't fail just because the email
        # doesn't send (can happen when SendGrid credits run out)
        try:
            if not settings.DEBUG:
                send_workshift_confirmation_email(member)
        except Exception:
            stack_trace = traceback.format_exc()
            send_exception_email(request.path, request.POST.items(), stack_trace)

        return render_to_response("thankyou.html",
            RequestContext(request, {
                "member" : member,
                "shift" : shift,
                "shift_date_times" : workshift_date_times
            })
        )
    else:
        member = get_member(request, "member_id")

        shift_id = None
        shift_dates = []
        shift_times = []

        for ms in MemberWorkShift.objects.filter(member=member):
            ws = ms.workshift_date_time
            shift_id = ws.shift.id
            shift_dates.append(ws.date.strftime("%m/%d/%Y"))
            shift_times.append(ws.start_time.strftime("%H%M"))

        shifts = WorkShift.objects.filter(season=Season.objects.get(name=CURRENT_SEASON)).values()
        for shift in shifts:
            shift["times"] = WorkShiftDateTime.objects.filter(shift__id=shift["id"]) \
                .distinct("start_time").values("start_time", "end_time")

        return render_to_response("workshift_selection.html",
            RequestContext(request, {
                "workshifts": shifts,
                "member": member,
                "shift_id": shift_id,
                "shift_dates": shift_dates,
                "shift_times": shift_times,
                "wed_a_dates": json.dumps([d.strftime("%m%d%Y") for d in WED_A_DATES]),
                "wed_b_dates": json.dumps([d.strftime("%m%d%Y") for d in WED_B_DATES]),
                "sat_a_dates": json.dumps([d.strftime("%m%d%Y") for d in SAT_A_DATES]),
                "sat_b_dates": json.dumps([d.strftime("%m%d%Y") for d in SAT_B_DATES]),
            })
        )

@handle_view_exception
def signup_quiz(request):
    return render_to_response("quiz.html",
        RequestContext(request, {})
    )


