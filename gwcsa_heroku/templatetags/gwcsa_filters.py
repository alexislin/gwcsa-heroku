from django.template import Library

register = Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def get_at_index(list, index):
    return list[index]

@register.filter
def get_formatted_time(time):
    return time.strftime("%H%M")




