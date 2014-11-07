import datetime
import json

from django.http import HttpResponse

from gwcsa_heroku.decorators import *
from gwcsa_heroku.models import *
from gwcsa_heroku.request_util import *

@handle_ajax_exception
def get_available_dates_for_shift(request):
    member = get_member(request, "memberId")
    shift_id = get_required_parameter(request, "shiftId")
    shift = WorkShift.objects.get(id=shift_id)

    dates = []
    for date in shift.get_available_dates_for_member(member):
        # hack to not show the first two weeks of distribution
        if "Distribution" in shift.name and date < datetime.date(2015, 6, 22):
            continue
        dates.append(date.strftime("%m%d%Y"))

    values = { "available_dates" : dates }
    return HttpResponse(json.dumps(values), content_type="application/json")

@handle_ajax_exception
def get_available_times_for_shift_date(request):
    member = get_member(request, "memberId")
    shift_id = get_required_parameter(request, "shiftId")
    shift = WorkShift.objects.get(id=shift_id)
    date = datetime.datetime.strptime(get_required_parameter(request, "date"), "%m/%d/%Y").date()

    member_start_times = [ms.workshift_date_time.start_time for ms in \
        MemberWorkShift.objects.filter(member=member).filter(workshift_date_time__shift=shift)]

    times = []
    for w in WorkShiftDateTime.objects.filter(shift=shift).filter(date=date):
        if not w.is_full() or w.start_time in member_start_times:
            times.append((w.start_time.strftime("%H%M"), w.start_time.strftime("%-I:%M %p")))

    values = { "available_times": times }
    return HttpResponse(json.dumps(values), content_type="application/json")
