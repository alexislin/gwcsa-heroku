import logging
import os
import traceback

from django.shortcuts import render_to_response
from django.template import RequestContext

from functools import wraps


def handle_view_exception(view_func):
    def _decorator(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as error:
            logging.error(traceback.format_exc())
            logging.error("Request Params:")
            args = request.GET if request.method == 'GET' else request.POST
            for arg in args:
                logging.error("    %s: %s" % (arg, args.get(arg)))

            # error page response (much better than throwing an exception)
            return render_to_response("error.html", RequestContext(request, { "error_message" : error }))

    return wraps(view_func)(_decorator)


