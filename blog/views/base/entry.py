# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:31 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from blog.models import Entry
from blog.forms.base.entry import (EntryModelForm, )

from sm_flexdata.views import (MultiViewTemplateView, )
from . import CommonGenericViewsAttributeMixin
from .entry_components import (
    EntryFilterListComp, COMMON_ENTRY_ACTION_URLS,
    EntryPreInitializedFilterFormListComp, pk_url_kwarg
)


class EntryView(MultiViewTemplateView):
    template_name = 'blog/base/entry/list.html'
    view_settings = {
        'content': (EntryFilterListComp, {})  # (view_class, {initkwargs})
    }


class BaseEntryFilterByView(MultiViewTemplateView):
    template_name = 'blog/base/entry/list.html'
    view_settings = {
        'content': (EntryPreInitializedFilterFormListComp, {'initial_form_data': {}})  # (view_class, {initkwargs})
    }
    filter_by_field_name = None

    def process_content(self, context_key, view_class, initkwargs, args, kwargs):
        # only need to change initkwargs and return None
        # view_class is EntryPreInitializedFilterFormListView that supports pre-initialization form data

        # for form data wee need to use or boundfield.html_name or form.add_prefix(name)
        dummy_form = view_class.form_class()
        html_field_name = dummy_form[self.filter_by_field_name].html_name
        # connect data from /accounts/staff/author/<int:id>/filter/ to form's html_field_name
        # is narrow place, url must contain value for form.to_field_name
        # in case of ModelChoiceField-s. By default it is primary key field
        initkwargs['initial_form_data'] = {html_field_name: kwargs[pk_url_kwarg]}


class EntryByAuthorView(BaseEntryFilterByView):
    filter_by_field_name = 'author'


class EntryByBlogView(BaseEntryFilterByView):
    filter_by_field_name = 'blog'


class EntryCommonAttributesMixin(CommonGenericViewsAttributeMixin):
    model = Entry
    form_class = EntryModelForm
    urls = COMMON_ENTRY_ACTION_URLS


class EntryCreateView(EntryCommonAttributesMixin, CreateView):
    template_name = 'blog/base/entry/create.html'


class EntryDetailView(EntryCommonAttributesMixin, DetailView):
    template_name = 'blog/base/entry/detail.html'


class EntryUpdateView(EntryCommonAttributesMixin, UpdateView):
    template_name = 'blog/base/entry/edit.html'


class EntryDeleteView(EntryCommonAttributesMixin, DeleteView):
    template_name = 'blog/base/entry/delete.html'


class EntryCommentListView(View):
    pass
