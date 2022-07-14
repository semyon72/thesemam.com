# Project: blog_7myon_com
# Package: 
# Filename: deferred.py
# Generated: 2021 Jun 01 at 20:44 
# Description of <deferred>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from functools import cached_property

from django.views.generic import DetailView

from .common import response_to_content

"""
Main code flow of View

ViewClass.as_view(initilkwargs only for existent class attributes) -> returns view_func(request, *args, **kwargs)
  view_func(....) is invoked by django.core.handlers.base.BaseHandler._get_response(...) as part
  common HTTP request's process. As parameters there are passed Request object and *args, **kwargs
  that was parsed from requested url if url defined as parametrized 
view_func(request, *args, **kwargs) -> Response object
  Response object is content that will be returned
  It must be object of HttpRequest but if object (response) has 'render' attribute and it
  callable then will be returned result of object.render() ( response.render() )

Attention:
  view_func.view_initkwargs - is not safe

Like conclusion:
  1. Instance of ViewClass does not reachable from outside but this is useful
  if need to invoke ViewClass manually few times
  2. we can not manipulate dynamically any attributes from moment
  where view function is created up to response will be formed and instance will be lost.
  
view_func(request, *args, **kwargs)
  self = cls(**initkwargs)  # initkwargs - copy of initkwargs passed into View.as_view(...)
  self.setup(request, *args, **kwargs)
  ....
  return self.dispatch(request, *args, **kwargs)
  
By default dispatch invokes attribute (method) that has name that same as request.method
something like 'get', 'post' ... For example self.get(request, *args, **kwargs)
 
"""


class DeferredViewMixin:

    return_response_immediately = True

    def __init__(self, **initkwargs):
        super().__init__(**initkwargs)
        self._response = None
        # store initialised kwargs' names
        self._initkwargs_names = tuple(initkwargs)
        # store parent dispatch that bound with current instance
        self.__dispatch = super(DeferredViewMixin, self).dispatch

    def dispatch(self, *args, **kwargs):
        if self.return_response_immediately:
            return self.get_response()
        return self

    def get_response(self):
        return self.__dispatch(self.request, *self.args, **self.kwargs)

    def get_content(self, response=None):
        return response_to_content(response or self.get_response())

    # ######
    # methods below useful (have matter) only if initkwargs - return_response_immediately = False
    # for example view_class.as_view(return_response_immediately = False)(request, *args, **kwargs)
    # It will return instance of view_class without start code's flow
    #

    @cached_property
    def response(self):
        """
            It returns same response each time
        :return:
        """
        if not self._response:
            self._response = self.get_response()
        return self._response

    def render(self):
        """
        Cause django.core.handlers.base.BaseHandler._get_response(request)
        supports deferred rendering we use this behaviour to return the real response

        But, cause response.render() will be invoked only after applying to template
        response middleware process_template_response(request, response)
        https://docs.djangoproject.com/en/3.2/topics/http/middleware/#process-template-response
        then inside middleware it still does not be processed

        :return: HttpResponse
        """
        renderer = getattr(self.response, 'render', None)
        if callable(renderer):
            return renderer()
        return self.response

    @property
    def content(self):
        return self.response.content

    def __str__(self):
        return response_to_content(self.response)


class DeferredDetailView(DeferredViewMixin, DetailView):
    pass
