from gwcsa_heroku.models import *

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

        if not first_name or not last_name or not email:
            msg = "Missing info: firstname='%s' lastname='%s' email='%s'."
            msg = msg % (first_name, last_name, email)
            msg += " To sign up for workshifts, please use the link "
            msg += "included in your Farmigo sign up confirmation email."
            raise Exception(msg)
        else:
            return Member.get_or_create_member(first_name, last_name, email)

