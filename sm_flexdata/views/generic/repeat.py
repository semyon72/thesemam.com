# Project: blog_7myon_com
# Package: 
# Filename: repeat.py
# Generated: 2021 Jun 01 at 20:45 
# Description of <repeat>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.template import engines, Template
from django.utils.safestring import mark_safe
from django.views.generic import ListView, View

from .common import response_to_content
from .deferred import DeferredViewMixin


class RepeatListViewMixin(ListView):
    """
        We will keep result of execution repeat_view_class
        in context key 'content_list' by default but configurable.
        It will have same order as 'object_list'.
        If will be need to get corresponding data in template then
        it is possible using next snippet
        {% for content in content_list %}
            {{ content }}
            {% for object in object_list %}
                {% if forloop.parentloop.counter0 == forloop.counter0 %}
                    {{ object }}
                {% endif %}
            {% endfor %}
        {% empty %}
            Content is empty.
        {% endfor %}
        It is little bit excessive code for template system and
        it is better to create custom filter that returns value by index
        for example something like {{ object_list|list_item:forloop.counter0 }}
        https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-filters
    """

    repeat_view_class = None
    repeat_view_fallback_method = 'GET'
    context_content_list_name = 'content_list'
    template_name = engines.all()[0].from_string(
        '{%% for content in %s %%}{{ content }}\r\n{%% endfor %%}' % context_content_list_name
    )

    def __init__(self, *args, **initkwargs):
        super().__init__(*args, **initkwargs)
        self._check_repeat_view_class()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if type(self.repeat_view_class) is type and issubclass(self.repeat_view_class, DeferredViewMixin):
            self.repeat_view_class = self.repeat_view_class.as_view(
                return_response_immediately=False
            )(request, *self.args, **self.kwargs)

    def _check_repeat_view_class(self):
        if type(self.repeat_view_class) is type:

            if not issubclass(self.repeat_view_class, View) or not hasattr(self.repeat_view_class, 'initial_object'):
                raise ValueError('repeat_view_class must be View class that implements initial_object interface')

        elif not isinstance(self.repeat_view_class, DeferredViewMixin):
            raise ValueError('repeat_view_class neither View class nor instance of DeferredViewMixin')

    def get_content_list_item(self, obj, initkwargs=None, *, return_as_is=False):
        """
        This method evaluate repeat_view_class for each object_list item and returns
        str that is content of execution the repeat_view_class or instance repeat_view_class
        if repeat_view_class is is subclass of DeferredViewMixin and return_as_is == True.
        :param obj: item of object_list
        :param initkwargs: Will be passed into View.as_view(**initkwargs)
        :param return_as_is: It has matter only if repeat_view_class is subclass of
        DeferredViewMixin. In this case instance of repeat_view_class will be returned
        :return: str that is content of repeat_view_class execution or instance repeat_view_class
        if repeat_view_class is is subclass of DeferredViewMixin and return_as_is == True.
        """
        initkwargs = initkwargs if initkwargs is not None else {}
        initkwargs['initial_object'] = obj
        if type(self.repeat_view_class) is type:
            result = response_to_content(
                self.repeat_view_class.as_view(**initkwargs)(self.request, *self.args, **self.kwargs)
            )
        else:
            # now we suppose that self.repeat_view_class is instance that implements DeferredViewMixin interface
            for attr, val in initkwargs.items():
                try:
                    getattr(self.repeat_view_class, attr)
                except:
                    raise
                else:
                    setattr(self.repeat_view_class, attr, val)
            result = self.repeat_view_class
            if not return_as_is:
                result = result.get_content()

        return result

    def get_content_list(self, object_list):
        rq_method = self.request.method
        if not hasattr(self.repeat_view_class, rq_method.lower()):
            fb_method = self.repeat_view_fallback_method
            if hasattr(self.repeat_view_class, fb_method.lower()):
                self.request.method = fb_method.upper()
            else:
                raise NotImplementedError('%s does not support [%s] and fallback [%s] methods' %
                                          (self.repeat_view_class, rq_method, fb_method)
                                          )
        try:
            result = []
            for obj in object_list:
                content_item = self.get_content_list_item(obj)
                if content_item:
                    result.append(mark_safe(str(content_item)))
        finally:
            self.request.method = rq_method

        return result

    def get_context_content_list_name(self):
        return self.context_content_list_name or 'content_list'

    def get_template_names(self):
        # fix for using Template instance directly in template_name
        if self.template_name and type(self.template_name).__name__ == 'Template':
            return self.template_name
        return super().get_template_names()

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs = super().get_context_data(object_list=object_list, **kwargs)
        # now 'object_list' is paginated
        content_list = self.get_content_list(kwargs.get('object_list', []))
        kwargs[self.get_context_content_list_name()] = content_list
        return kwargs


class RepeatListView(RepeatListViewMixin, ListView):
    pass
