# Project: blog_7myon_com
# Package: 
# Filename: middleware.py
# Generated: 2021 Jan 23 at 16:54 
# Description of <middleware>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import abc
from functools import cached_property
from typing import Union

from django.http.request import HttpRequest

from django.contrib.auth.views import redirect_to_login
from django.urls import reverse, path, include
from django.http import HttpResponse

from .urls import settings
from . import urls


class AbstractRightsChecker(metaclass=abc.ABCMeta):

    def __init__(self, request: HttpRequest ) -> None:
        self._request = request
        super().__init__()

    @abc.abstractmethod
    def is_matched(self) -> bool:
        return False

    @abc.abstractmethod
    def is_access_allow(self) -> bool:
        return True

    @abc.abstractmethod
    def access_granted(self) -> Union[HttpResponse, None]:
        return None

    @abc.abstractmethod
    def access_denied(self) -> Union[HttpResponse, None]:
        return None

    @abc.abstractmethod
    def get_response_or_raise_exception(self):
        if self.is_matched():
            if self.is_access_allow():
                return self.access_granted()
            else:
                return self.access_denied()


class BaseAccessor(AbstractRightsChecker):

    namespace_separator = ':'

    def get_tracked_namespaces(self):
        return getattr(self, 'tracked_namespaces', ())

    @cached_property
    def matched_ns(self) -> Union[list, None]:
        trckd_ns = self.get_tracked_namespaces()
        for tns in trckd_ns:
            _tns = tns.split(self.namespace_separator)
            rns = self._request.resolver_match.namespace.split(self.namespace_separator)[:len(_tns)]
            if _tns == rns:
                return _tns

    def is_matched(self) -> bool:
        return self.matched_ns is not None

    def is_access_allow(self) -> bool:
        return self._request.user.is_authenticated

    def access_granted(self) -> HttpResponse:
        return super().access_granted()

    def access_denied(self) -> HttpResponse:
        return HttpResponse('You have not access to this area.')

    def get_response_or_raise_exception(self):
        return super().get_response_or_raise_exception()


class AccessorRedirectToLoginMixin:

    def get_login_url(self):
        return None

    def access_denied(self) -> HttpResponse:
        requested_path = self._request.get_full_path()
        return redirect_to_login(requested_path, login_url=self.get_login_url())


class BlogBaseAccessor(AccessorRedirectToLoginMixin, BaseAccessor):

    tracked_namespaces = (
        settings.get_app_name(settings.STAFF_NAME),
        settings.get_app_name(settings.AUTHOR_NAME)
    )

    def get_login_url(self):
        return reverse(settings.get_view_name('login', settings.AUTH_NAME))

    def is_access_allow(self) -> bool:
        if super().is_access_allow():  # only tests for authentication
            mns = self.matched_ns
            # cause settings.get_app_name_for_user(self._request.user)
            # create ns that depends from is_staff user or not then
            # it enough for the tracked sections at this moment
            user_ns = settings.get_app_name_for_user(self._request.user).split(self.namespace_separator)
            return mns == user_ns[:len(mns)]
        return False

    def access_granted(self) -> HttpResponse:
        # Probably, Now need add appropriate queryset (limited by user) as class attribute
        # and use its in View directly
        # view_class = self._request.resolver_match.view_class
        # view_class.queryset =

        return super().access_granted()


class AuthorAccessor(BlogBaseAccessor):
    """
        parent is_access_allow() implements all of we need. See comment above
    """
    pass


class StaffAccessor(BlogBaseAccessor):
    """
        parent is_access_allow() implements all of we need. See comment above
    """
    pass


# it could be inherited from django.utils.deprecation.MiddlewareMixin
class BlogLoginRequiredMiddleware:

    def __init__(self, get_request) -> None:
        # it happens at load middleware stage
        self.get_request = get_request

    def __call__(self, request):
        # it happens at execution of middleware stage
        # right before the next middleware will be executed
        result = self.get_request(request)
        # now we have response that is response
        return result

    @staticmethod
    def _get_accessors():
        accessors = [
            # StaffAccessor(),
            # AuthorAccessor()
            BlogBaseAccessor
        ]
        return accessors

    def process_view(self, request, view_func, view_args, view_kwargs):
        # it happens right before view will be executed
        # check request path from settings and users.is_staff ....
        for Accessor in self._get_accessors():
            if not issubclass(Accessor, AbstractRightsChecker):
                raise TypeError('Accessor must implement AbstractRightsChecker type')
            response = Accessor(request).get_response_or_raise_exception()
            if response is not None:  # then main flow should be interrupted - redirect to login
                return response
        # if returns None then main flow will not interrupted


class BlogUrlSectionSwitcherMiddleware:

    def __init__(self, get_request) -> None:
        # it happens at load middleware stage
        self.get_request = get_request

    def __call__(self, request):
        # it happens at execution of middleware stage
        # right before the next middleware will be executed

        # section = settings.match_sections(request.path)
        # TODO: Need refactor cause settings.match_sections() is removed
        section = ''
        if section:
            request.urlconf = (path('', include((urls.urlpatterns_for[section], settings.APP_NAME))),)

        result = self.get_request(request)
        # now, we have response that will be sent back as result of the current request
        return result
