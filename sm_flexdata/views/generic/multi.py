# Project: blog_7myon_com
# Package: 
# Filename: multicontext.py
# Generated: 2021 May 23 at 23:02 
# Description of <multicontext>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
import itertools

from django.http.response import HttpResponse
from django.utils.safestring import mark_safe
from django.views import generic


def normalize_settings(settings):
    result = {}
    if settings:
        for context_key, view_opts in settings.items():
            if not view_opts:
                result[context_key] = None
                continue

            opts = [None, {}]
            if isinstance(view_opts, (tuple, list)):
                opts_len = len(view_opts)
                if opts_len > 2 or opts_len < 1:
                    raise ValueError(
                        'context key "%s": if view_settings\' value is list'
                        'or tuple then it must have 2 elements' % context_key
                    )
                if opts_len > 0:
                    opts[0] = view_opts[0]  # view class
                if opts_len > 1:
                    opts[1] = dict(view_opts[1])  # copy view's initkwargs
            else:
                opts[0] = view_opts

            result[context_key] = opts if opts[0] else None

    return result


def _merge_settings(parent, current):
    return dict(filter(lambda kv: kv[1], dict(itertools.chain(parent.items(), current.items())).items()))


def merge_settings_with_parent(cls, current=None, attr_name='view_settings'):
    """

    :param cls: Start point for searching parent that has attr_name attribute
    :param current: current settings that will merge to parent.view_settings
     if current settings is None then will be gotten cls.view_settings
    :param attr_name: attribute name that has view's settings
    :return: Always returns copy of merged parent and current settings that were normalized
    """
    parent = None
    # got first parent who has view_settings
    i = iter(cls.__mro__)
    next(i, None)
    for c in i:
        if attr_name in c.__dict__:
            parent = c.__dict__.get(attr_name)
            break

    if not current:
        current = cls.__dict__.get(attr_name)

    result = _merge_settings(normalize_settings(parent), normalize_settings(current))
    return result


def merge_view_settings(cls):
    """
    Class decorator merge parent view's settings with current
    :param cls:
    :return:
    """
    cls.view_settings = merge_settings_with_parent(cls)
    cls._view_settings_is_merged = True
    return cls


class MultiViewRedirectRequiredError(Exception):

    def __init__(self, *args, response, context_key):
        super().__init__(
            'For context "%s" was returned response %r.' % (context_key, response)
        )
        self.response = response
        self.context_key = context_key


class MultiViewMixin:

    view_settings = {}
    """
        it should be dictionary like
        { 
            'content': PublicAboutView
            'aside_element': (AsideElementView, )
            'aside_element_1': (AsideElement1View, {template_name: 'aside_element_1.html'})
         }
         Where {template_name: 'aside_element_1.html'} is initkwargs and
         It will passed to AsideElement1View.as_view(**initkwargs)
    """

    passive_http_method = 'GET'
    """
        It works together with active_context_keys.
        See active_context_keys notes.
    """

    active_context_keys = ()
    """
        It contains tuple of context's keys from view_settings for indication
        that corresponding view is ready to process a request that has method
        that differ from passive_http_method.
    """

    allow_unimplemented_http_method = True

    def __init__(self, **initkwargs):
        settings_attr_name = 'view_settings'
        initial_view_settings = normalize_settings(initkwargs.pop(settings_attr_name, None))
        super().__init__(**initkwargs)
        if settings_attr_name not in self.__dict__:
            # means, the 'view_settings' was not redefined in the descendants for instance
            # then we will merge them with logic by default
            if not getattr(self, '_view_settings_is_merged', False):
                # decorator merge_view_settings was not applied to class
                merged_class_settings = merge_settings_with_parent(type(self), attr_name=settings_attr_name)
            else:
                # view_settings normalized already
                merged_class_settings = getattr(self, settings_attr_name)

            # redefine instance view's settings with initial values
            setattr(self, settings_attr_name, _merge_settings(merged_class_settings, initial_view_settings))

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self._check_active_context_keys()
        self._patch_unimplemented_http_method()
        self.setup_view_initkwargs()

    def setup_view_initkwargs(self):
        """
        Callbacks setup_view_class_name_in_lower(initkwargs) will be invoked at  setup stage.
        initkwargs is init kwargs that were pointed in view_settings.
        They can be modified at runtime and as result it will affect on value that will be passed
        in certain view_class at runtime stage.
        :return:
        """
        for context_key, (view_class, initkwargs) in self.view_settings.items():
            func = getattr(self, 'setup_%s' % view_class.__name__.lower(), None)
            if callable(func):
                func(initkwargs)

    def _patch_unimplemented_http_method(self):
        method = self.request.method.lower()
        if not hasattr(self, method) and self.allow_unimplemented_http_method and method in self.http_method_names:
            setattr(self, method, self.get)

    def _check_active_context_keys(self):
        context_keys = tuple(self.view_settings)
        if len(self.active_context_keys) == 0:
            len_context_keys = len(context_keys)
            if len_context_keys == 1:
                self.active_context_keys = context_keys[0]
                return
            elif len_context_keys > 1:
                raise ValueError('active_context_keys must contain at least one key from context_view_classes')
        broken_keys = tuple(
            key for key in self.active_context_keys if key not in context_keys
        )
        if len(broken_keys) > 0:
            raise ValueError('active_context_keys must contain only keys from context_view_items')

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except MultiViewRedirectRequiredError as err:
            return err.response

    def process_response(self, view_response, context_key):
        response = view_response
        if hasattr(view_response, 'render'):
            # we suppose that it is TemplateResponse
            response = view_response.render()
            return mark_safe(response.content.decode(encoding=response.charset))
        return response

    def process_default(self, context_key, view, initkwargs, args, kwargs):
        """
        This function and process_xxx (xxx - context_key) must return either string or HttpResponse
        (HttpResponse as example for responses with codes 3xx). Each string's result will be
        included as content regardless whether HttpResponse has code 2xx or 4xx. For HttpResponse with
        code 3xx will thrown redirection. Other responses will be turned to a string.

        Also useful thing is modifying the initkwargs, args and kwargs with further returning None
        from the process_xxx(...) methods. In this case view will be processed
        by concrete process_default(...) method with modified parameters.

        :param view: subclass of View
        :param initkwargs:
        :param context_key:
        :param args: local shallow copy of self.args
        :param kwargs: local shallow copy of self.kwargs
        :return: must return or string or HttpResponse.
        process_xxx(...) method also can return None to delegate real processing
        to process_default method(...)
        """
        method = self.request.method
        try:
            # we need to switch self.request.method into self.passive_http_method
            # each time when view has resolved as not active.
            if context_key not in self.active_context_keys:
                self.request.method = self.passive_http_method.upper()
            response = view.as_view(**initkwargs)(self.request, *args, **kwargs)
        finally:
            self.request.method = method

        return self.process_response(response, context_key)

    def process_view_settings(self, context):
        # to speed up we should make the ordered context's keys
        # in way where self.active_context_keys and rest of the others
        akeys = (self.active_context_keys, ) if isinstance(self.active_context_keys, str) else tuple(self.active_context_keys)
        okeys = akeys + tuple(set(self.view_settings) - set(akeys))

        for context_key in okeys:
            (view, initkwargs) = self.view_settings[context_key]
            process_func = getattr(self, 'process_%s' % context_key, None)
            result, method, args, kwargs = (None, self.request.method, list(self.args), self.kwargs.copy())
            if callable(process_func):
                result = process_func(context_key, view, initkwargs, args, kwargs)
            if result is None:
                result = self.process_default(context_key, view, initkwargs, args, kwargs)
            if result is None:
                # probably some one overloaded process_default
                raise ValueError('%s.%s must return content' % (process_func.__class__.__name__, process_func.__name__))
            # restore self.request.method value if it was changed inside custom callbacks
            self.request.method = method
            # if view from self.view_settings returns something other str,
            # redirect response for example, then we need to return those HTTPResponse-s
            if isinstance(result, HttpResponse):
                if 300 <= result.status_code <= 399:  # status code 3xx is redirect
                    raise MultiViewRedirectRequiredError(response=result, context_key=context_key)
                else:
                    # Need to process this case and return appropriate context
                    # probably, need to logging or maybe raise exception .....
                    result = str(result)

            context[context_key] = result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.process_view_settings(context)
        return context


class MultiViewTemplateView(MultiViewMixin, generic.TemplateView):
    pass


class MultiViewDetailView(MultiViewMixin, generic.DetailView):
    pass


class MultiViewListView(MultiViewMixin, generic.ListView):
    pass
