# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:31 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from collections import deque
from urllib.parse import urlparse, urlunparse, urlsplit, urlunsplit

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import QuerySet, Prefetch
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import resolve, is_valid_path, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.forms.models import ModelForm
from django.views.generic.edit import ModelFormMixin

from blog.models import Entry, EntryText
from blog.forms.base.entry import (
    EntryTextModelForm, EntryWithTextBodytextOnlyModelForm,
)

from sm_flexdata.html.form_elements import FlexFormMixin
from sm_flexdata.views import InitialDetailView
from sm_flexdata.views.generic.multi import MultiViewMixin, MultiViewTemplateView
from . import CommonGenericViewsAttributeMixin
from .entry import BaseEntryFilterByView
from . import entrywithtext_components as comp


class EntryWithTextDetailView(MultiViewMixin, DetailView):
    template_name = 'blog/base/entrywithtext/detail.html'
    queryset = Entry.objects.all()
    pk_url_kwarg = comp.pk_url_kwarg

    view_settings = {
        'content': (comp.EntryWithTextItemComp, {})
    }

    def process_content(self, context_key, view, initkwargs, args, kwargs):
        initkwargs['initial_object'] = self.object


class EntryWithTextView(MultiViewTemplateView):
    template_name = 'blog/base/entrywithtext/list.html'

    view_settings = {
        'content': (comp.EntryWithTextFilterListComp, {})
    }


class BaseEntryWithTextFilterByView(BaseEntryFilterByView):
    template_name = 'blog/base/entrywithtext/list.html'
    view_settings = {
        'content': (comp.EntryWithTextPreInitializedFilterFormListComp, {'initial_form_data': {}})  # (view_class, {initkwargs})
    }


class EntryWithTextByAuthorView(BaseEntryWithTextFilterByView):
    filter_by_field_name = 'author'


class EntryWithTextByBlogView(BaseEntryWithTextFilterByView):
    filter_by_field_name = 'blog'


class EntryWithTextCommonMixin:
    pk_url_kwarg = comp.pk_text_url_kwarg
    pk_entry_url_kwarg = comp.pk_url_kwarg

    queryset = EntryText.objects.select_related()

    urls = comp.COMMON_ENTRYWITHTEXT_ACTION_URLS

    success_url = reverse_lazy(comp.COMMON_ENTRYWITHTEXT_ACTION_URLS.settings.get('list')[0])

    view_settings = {
        'entry_content': (comp.entry_comp.EntryItemComp, )
    }

    def get_queryset(self):
        """
        This is used on Edit and Delete views
        :return: QuerySet
        """
        qs = super().get_queryset().filter(entry=self.kwargs.get(self.pk_entry_url_kwarg))
        return qs

    def process_entry_content(self, context_key, view, initkwargs, args, kwargs):
        initkwargs['initial_object'] = self.entry_object

    def get_context_data(self, **kwargs):
        obj = getattr(self, 'object', None)
        if obj:
            self.entry_object = obj.entry
        context = super().get_context_data(**kwargs)
        context['entry_object'] = self.entry_object
        return context


class EntryWithTextCreateView(EntryWithTextCommonMixin, MultiViewMixin, CreateView):

    template_name = 'blog/base/entrywithtext/create.html'
    form_class = EntryWithTextBodytextOnlyModelForm

    def set_entry(self):
        if self.pk_entry_url_kwarg in self.kwargs:
            self.entry_object = get_object_or_404(Entry, pk=self.kwargs.get(self.pk_entry_url_kwarg))

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.set_entry()

    def form_valid(self, form):
        form.instance.entry = self.entry_object
        return super().form_valid(form)

    def get_success_url(self):
        url = comp.COMMON_ENTRYWITHTEXT_ACTION_URLS.reverse_for('detail', self, none_if_fail=True)
        if url:
            url = url + '?%s=last' % comp.EntryTextTabListComp.page_kwarg
        return url or super().get_success_url()


class EntryWithTextUpdateView(EntryWithTextCommonMixin, MultiViewMixin, UpdateView):
    template_name = 'blog/base/entrywithtext/edit.html'
    form_class = EntryWithTextBodytextOnlyModelForm

    def get_success_url(self):
        url = comp.COMMON_ENTRYWITHTEXT_ACTION_URLS.reverse_for('detail', self, none_if_fail=True)
        if url and self.request.preaction_url.startswith(url):
            url = self.request.preaction_url
        return url or super().get_success_url()


class EntryWithTextDeleteView(EntryWithTextCommonMixin, MultiViewMixin, DeleteView):
    template_name = 'blog/base/entrywithtext/delete.html'

    def get_success_url(self):
        url = comp.COMMON_ENTRYWITHTEXT_ACTION_URLS.reverse_for('detail', self, none_if_fail=True)
        return url or super().get_success_url()
