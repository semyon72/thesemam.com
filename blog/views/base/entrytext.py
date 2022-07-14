# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2020 Oct 17 at 18:31 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from blog.models import EntryText
from blog.forms.base.entry import (EntryTextFilterForm, EntryTextModelForm)

from sm_flexdata.views import (MultiViewTemplateView, )

from . import CommonGenericViewsAttributeMixin
from .entrytext_components import EntryTextFilterListComp, COMMON_ENTRYTEXT_ACTION_URLS, COMMON_ENTRYTEXT_QUERYSET


class EntryTextView(MultiViewTemplateView):
    template_name = 'blog/base/entrytext/list.html'
    default_filter_form = EntryTextFilterForm
    view_settings = {
        'content': (EntryTextFilterListComp, {})  # (view_class, {initkwargs})
    }

    # def modify_queryset(self, queryset, query_data):
    #     # SELECT `blog_entrytext`.`id`, `blog_entrytext`.`entry_id`, `blog_entrytext`.`body_text`,
    #     #  (SELECT COUNT(*) AS `cnt`
    #     #   FROM `blog_entrytext` U0
    #     #   WHERE U0.`entry_id` = `blog_entrytext`.`entry_id`
    #     #   GROUP BY U0.`entry_id` ORDER BY NULL) AS `text_for_entry_count`
    #     # FROM `blog_entrytext`
    #     # implementation of above SQL
    #     # subq = EntryText.objects.values('entry').annotate(cnt=Count('*')).values('cnt').filter(entry=OuterRef('entry'))
    #     # resqs = qs.annotate(text_for_entry_count=Subquery(subq))
    #     return super().modify_queryset(queryset, query_data)


class EntryTextCommonAttributesMixin(CommonGenericViewsAttributeMixin):
    # model = EntryText
    queryset = COMMON_ENTRYTEXT_QUERYSET
    form_class = EntryTextModelForm
    urls = COMMON_ENTRYTEXT_ACTION_URLS


class EntryTextCreateView(EntryTextCommonAttributesMixin, CreateView):
    template_name = 'blog/base/entrytext/create.html'


class EntryTextDetailView(EntryTextCommonAttributesMixin, DetailView):
    template_name = 'blog/base/entrytext/detail.html'


class EntryTextUpdateView(EntryTextCommonAttributesMixin, UpdateView):
    template_name = 'blog/base/entrytext/edit.html'


class EntryTextDeleteView(EntryTextCommonAttributesMixin, DeleteView):
    template_name = 'blog/base/entrytext/delete.html'
