import logging
import os
import traceback

from django.shortcuts import render_to_response
from django.template import RequestContext

from functools import wraps

from gwcsa_heroku.email_util import *

def __log_error(args, stack_trace):
    logging.error(stack_trace)
    logging.error("Request Params:")
    for name, value in args:
        logging.error("    %s: %s" % (name, value))

def handle_view_exception(view_func):
    def _decorator(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as error:
            args = request.GET if request.method == 'GET' else request.POST
            args = args.items()
            stack_trace = traceback.format_exc()

            __log_error(args, stack_trace)
            send_exception_email(request.path, args, stack_trace)

            # error page response (much better than throwing an exception)
            return render_to_response("error.html", RequestContext(request, { "error_message" : error }))

    return wraps(view_func)(_decorator)

def handle_ajax_exception(ajax_func):
    def _decorator(request, *args, **kwargs):
        try:
            return ajax_func(request, *args, **kwargs)
        except Exception as error:
            args = request.GET if request.method == 'GET' else request.POST
            args = args.items()
            stack_trace = traceback.format_exc()

            __log_error(args, stack_trace)
            send_exception_email(request.path, args, stack_trace)
            raise

    return wraps(ajax_func)(_decorator)


