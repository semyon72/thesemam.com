# Project: blog_7myon_com
# Package: 
# Filename: filtered_list.py
# Generated: 2021 Jan 01 at 10:11 
# Description of <filtered_list>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
import datetime

from django.core.paginator import Paginator
from django.db.models import Model, QuerySet
from django.forms import Form

from django.views.generic import ListView
from django.views.generic.edit import FormMixin


class FilterFormListView(FormMixin, ListView):

    session_key = None

    def get_session_key(self):
        return self.session_key or self.__class__.__name__

    @staticmethod
    def serialize_form(form: Form):
        result = {}
        for field_name, value in form.cleaned_data.items():
            html_field_name = form.add_prefix(field_name)
            serialized_value = form.fields[field_name].prepare_value(value)
            if not isinstance(serialized_value, (str, int, float, list, tuple, dict, type(None))):
                serialized_value = str(serialized_value)
            result[html_field_name] = serialized_value
        return result

    def _form_to_session(self, form: Form):
        if form.is_valid():
            self.request.session[self.get_session_key()] = self.serialize_form(form)
        else:
            raise AssertionError('At this place form "%s" must be valid' % form.__class__.__name__)

    def _session_to_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        ses_key = self.get_session_key()
        sesdata = self.request.session.get(ses_key)

        form_kwargs = {**{'data': sesdata}, **self.get_form_kwargs()}
        form = form_class(**form_kwargs)
        if not form.is_valid():
            # clean session
            self.request.session.pop(ses_key, None)
            # self.request.session.modified = True
            form = None
        return form

    def get_form(self, form_class=None):
        # if method get -> need to restore from session and return
        sess_form = self._session_to_form(form_class)
        if self.request.method in ('GET', ) and sess_form:
            self.set_queryset(sess_form)
            return sess_form
            # need to set queryset into session data

        # Otherwise session data are empty or wrong or POST
        # if method post -> need to persist into session
        form = super().get_form(form_class)
        if self.request.method in ('POST', 'PUT'):
            if form.is_valid():
                self._form_to_session(form)
                # need to set queryset into form data
                self.set_queryset(form)
            else:
                # need to set queryset into session form data
                if sess_form:
                    # we still must limit queryset by session data
                    self.set_queryset(sess_form)
                    pass
                else:
                    # nothing do with queryset
                    self.set_queryset()

        return form

    def set_queryset(self, form=None):
        qs = super().get_queryset()
        if form:
            self.queryset = self.set_filters(qs, form)

    def get_filter_lookup_value(self, field_name, value, form: Form=None):
        # by default value is same as form.cleaned_data[field_name]
        # get appropriate lookup value
        if isinstance(value, (Model, QuerySet,)):
            value = form.fields[field_name].prepare_value(value)
        return value

    def get_filter_kwargs(self, field_name, value, kwargs=None, form=None):
        '''
        If kwargs is None then it will return new dict instance with
        single { filter_lookup: value } pair. Otherwise filer_lookups (dictionary's keys)
        will be collecting (add new and modify exist) and returned value will be passed kwargs
        Value is already prepared by get_filter_lookup_value() that by default
        use form.fields[field_name].prepare_value(value). For example example,
        if value is instance Model then value will contain pk and if QuerySet then [pk, pk, ...]

        :param field_name:
        :param value:
        :param kwargs:
        :param form: Form
        :return:
        '''
        result = kwargs if kwargs is not None else {}
        if not value:
            return
        if isinstance(value, (list, tuple)):
            field_name += '__in'
        elif isinstance(value, (int, float, datetime.date, bool)):
            field_name += '__exact'
        else:
            field_name += '__icontains'
        result[field_name] = value
        return result

    # Example set_filter_xxxx
    # def set_filter_field_name(self, queryset, value, form=None):
    #     # Unlike get_filter_kwargs(self, field_name, value, kwargs=None, form=None),
    #     # value that here is, has not prepared by get_filter_lookup_value(...)
    #     # and it is same as form.cleaned_data[field_name]
    #     kwargs = self.get_filter_kwargs(field_name, value, form=form)
    #     if kwargs:
    #         queryset = queryset.filter(**kwargs)
    #     return queryset
    #

    def set_filters(self, queryset: QuerySet, form: Form):
        '''
        Main queryset modifier that process form.cleaned_data with logic
        by default. If need to modify queryset totally you can redefine it.
        If you need to filter queryset that depends from certain form field
        it can be reached by defining method like
            set_filter_field_name(queryset, value, form)
        that must return modified queryset.
        And at the end If need modify query set on one filter(...) level,
        inside default filter(...) then need to redefine
            get_filter_kwargs(self, field_name, value, kwargs=None, form=None)
        and consequently modify kwargs like in pattern below
            get_filter_kwargs(self, field_name, value, kwargs=None, form: Form = None):
                exclude_fields = ('field_one', 'field_two')
                if field_name not in exclude_fields:
                    # default processing
                    super().get_filter_kwargs(field_name, value, kwargs, form)
                else:
                    # processing lookup manually
                    .......

        :param queryset:
        :param form:
        :return:
        '''
        filter_kwargs = {}
        for field_name, value in form.cleaned_data.items():
            # if exists callback set_filter_field_name then apply for the changes
            filter_setter = getattr(self, 'set_filter_%s' % field_name, None)
            if callable(filter_setter):
                queryset = filter_setter(queryset, value, form)
                if not isinstance(queryset, QuerySet):
                    raise ValueError('filter\'s setter "%s" must return queryset.' % filter_setter)
            else:
                # get appropriate lookup value
                value = self.get_filter_lookup_value(field_name, value, form)
                # collect default filter's lookups
                self.get_filter_kwargs(field_name, value, filter_kwargs, form)

        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)

        return queryset

    def get_context_data(self, **kwargs):
        # skip FormMixin.get_context_data
        # because we initialize kwargs['form'] right before
        # all data will be processed in ListView.get(...)
        grand_parent_get_context_data = super(FormMixin, self).get_context_data
        return grand_parent_get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        # process all data (queryset ...) before ListView.get(...)
        context = {'form': self.get_form()}
        # set extra_context for passing into template
        if self.extra_context:
            self.extra_context.update(context)
        else:
            self.extra_context = context
        return super().get(request, *args, **kwargs)

    post = get  # set post handler same as get
    put = get # set put handler same as get

    def get_success_url(self):
        raise AssertionError('We never must be here')

    def form_valid(self, form):
        raise AssertionError('We never must be here')

    def form_invalid(self, form):
        raise AssertionError('We never must be here')

    #
    # def page_number(self):
    #     # serve session data
    #     page = self.request.GET.get(self.page_kwarg)
    #     if page is None:
    #         sesdata = self.request.session.get(self.get_session_key())
    #         if sesdata is not None:
    #             page = sesdata.get(self.page_kwarg)
    #     else:
    #         self.request.session.setdefault(self.get_session_key(), {})[self.page_kwarg] = page
    #         self.request.session.modified = True
    #
    #     return page

