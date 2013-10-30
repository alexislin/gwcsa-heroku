import json

from django.http import HttpResponse

from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *


def get_available_dates_for_shift(request):
    member = get_member(request, "memberId")
    shift_id = get_required_parameter(request, "shiftId")
    shift = WorkShift.objects.get(id=shift_id)

    dates = [d.strftime("%m%d%Y") \
            for d in shift.get_available_dates_for_member(member)]

    values = { "available_dates" : dates }
    return HttpResponse(json.dumps(values), content_type="application/json")

def get_available_times_for_shift_date(request):
    member = get_member(request, "memberId")
    shift_id = get_required_parameter(request, "shiftId")
    shift = WorkShift.objects.get(id=shift_id)

    date = datetime.datetime.strptime(get_required_parameter("date"), "%m/%d/%Y").date()

    values = {}
    return HttpResponse(json.dumps(values), content_type="application/json")
'''
        member_start_times = [s.time for s in member.shifts if s.get_id() == shift_id]

        available_times = []

        for time in shift.times.order("start"):
            # include if time is available, or if it's currently assigned to this member
            if (not time.is_full(date)) or time.start in member_start_times:
                available_times.append((time.start.strftime("%H%M"), time.start.strftime("%-I:%M %p")))

        data = { "available_times" : available_times }

        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(data))
'''
