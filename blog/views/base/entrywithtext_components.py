# Project: blog_7myon_com
# Package: 
# Filename: entry_entrytext_components.py
# Generated: 2021 Jun 17 at 09:29 
# Description of <entry_entrytext_components>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.safestring import mark_safe

from blog.forms.base.entry import EntryWithTextFilterForm
from blog.models import Entry, EntryText
import blog.views.base.entry_components as entry_comp
from blog.views.base import PreInitializedFilterFormMixin
import blog.views.base.entrytext_components as entrytext_comp
from sm_flexdata.urls import Urls, resolve_attr
from sm_flexdata.views import InitialDetailView, RepeatListView
from sm_flexdata.views.generic.common import response_to_content, AttrTruncateMixin
from sm_flexdata.views.generic.multi import MultiViewMixin

pk_url_kwarg = 'id'
pk_text_url_kwarg = 'text_id'


COMMON_ENTRYWITHTEXT_ACTION_URLS = Urls(
    list=('blog:staff:entrywithtext_list', {}),
    create=('blog:staff:entrywithtext_create', {
        pk_url_kwarg: resolve_attr('object.entry.pk'), # used only in EntryWithTextItemComp where object is Entry
    }),
    detail=('blog:staff:entrywithtext_detail', {
        pk_url_kwarg: resolve_attr('object.entry.pk'),
        pk_text_url_kwarg: resolve_attr('object.pk'),
    }),
    update=('blog:staff:entrywithtext_update', {
        pk_url_kwarg: resolve_attr('object.entry.pk'),
        pk_text_url_kwarg: resolve_attr('object.pk'),
    }),
    delete=('blog:staff:entrywithtext_delete', {
        pk_url_kwarg: resolve_attr('object.entry.pk'),
        pk_text_url_kwarg: resolve_attr('object.pk'),
    }),
)

COMMON_ENTRYWITHTEXT_ENTRY_ACTION_URLS = Urls(
    list=('blog:staff:entrywithtext_list', {}),
    by_author_list=('blog:staff:entrywithtext_by_author_list', {
        pk_url_kwarg: resolve_attr('object.author.pk')
    }),
    by_blog_list=('blog:staff:entrywithtext_by_blog_list', {
        pk_url_kwarg: resolve_attr('object.blog.pk')
    }),
    create=('blog:staff:entry_create', {}),
    detail=('blog:staff:entry_detail', {pk_url_kwarg: resolve_attr('object.pk')}),
    update=('blog:staff:entry_update', {pk_url_kwarg: resolve_attr('object.pk')}),
    delete=('blog:staff:entry_delete', {pk_url_kwarg: resolve_attr('object.pk')}),
)


class EntryCoauthorItemComp(entry_comp.EntryCoauthorItemComp):
    urls = Urls(
        by_author_list=('blog:staff:entrywithtext_by_author_list', {
            pk_url_kwarg: resolve_attr('object.pk')
        }),
    )


class EntryCoauthorItemListComp(entry_comp.EntryCoauthorItemListComp):
    repeat_view_class = EntryCoauthorItemComp


class EntryItemComp(entry_comp.EntryItemComp):
    urls = COMMON_ENTRYWITHTEXT_ENTRY_ACTION_URLS

    def get_coauthors_content(self, coauthors):
        result = ''
        if coauthors:
            response = EntryCoauthorItemListComp.as_view(queryset=coauthors)(self.request, *self.args, **self.kwargs)
            response = response.render()
            result = mark_safe(response.content.decode(encoding=response.charset))
        return result


class EntryTextTabListComp(entrytext_comp.EntryTextTabListComp):
    urls = COMMON_ENTRYWITHTEXT_ACTION_URLS
    pk_text_url_kwarg = pk_text_url_kwarg  # it is used to select appropriate tab in template, only for this purpose


class EntryWithTextItemComp(MultiViewMixin, InitialDetailView):
    template_name = 'blog/base/entrywithtext/entrywithtext_item.html'
    queryset = Entry.objects.all()
    pk_url_kwarg = pk_url_kwarg
    entrytext_tab_list_comp_initkwargs = {
        'template_name': '',
        'truncate_length_default': None
    }

    view_settings = {
        'entry_info': (EntryItemComp, {})
    }

    def process_entry_info(self, context_key, view, initkwargs, args, kwargs):
        initkwargs['initial_object'] = self.object

    def _get_paginator_base_url(self, entry_obj):
        """
        Quite a specific function. Tightly coupled with 3-parts of code
        :param entry_obj:
        :return:
        """
        viewname = EntryTextTabListComp.urls.settings.get('detail')
        if self.initial_object is None or self.request.resolver_match.view_name == viewname[0]:
            # by general approach if initial_object is not initialized it means
            # this instance is using as standalone and we no need to change paginator_base_url at all.
            return ''

        current_app = self.request.resolver_match.namespace  # or EntryTextTabListComp.urls.get_current_app(self)
        return reverse(viewname[0], kwargs={self.pk_url_kwarg: entry_obj.pk}, current_app=current_app)


    def process_entry_object(self, entry_obj):
        result = 'Something went wrong %r, Entry object was not processed properly.' % self

        if entry_obj:
            stub = type('stub', (object,), {'object': type('stub', (object,), {'entry': entry_obj})})
            kwargs = {
                'queryset': list(entry_obj.entrytext_set.all()),
                'paginator_base_url': self._get_paginator_base_url(entry_obj),
                'urls': {
                    'create': EntryTextTabListComp.urls.reverse_for('create', stub, self.request)
                },
            }
            kwargs.update(filter(lambda itm: itm if itm[1] else None, self.entrytext_tab_list_comp_initkwargs.items()))
            resp = EntryTextTabListComp.as_view(**kwargs)(self.request, *self.args, **self.kwargs)
            result = mark_safe(response_to_content(resp))
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entrytext_tab'] = self.process_entry_object(context.get('object'))
        return context


class EntryWithTextItemListComp(RepeatListView):
    template_name = 'blog/base/entrywithtext/entrywithtext_item_list.html'
    queryset = Entry.objects.order_by('-mod_date').select_related().prefetch_related(
        'coauthors',
        Prefetch('entrytext_set', EntryText.objects.order_by('pk'))
    )
    repeat_view_class = EntryWithTextItemComp
    paginate_by = 10
    page_kwarg = 'etpage'

    def get_content_list_item(self, obj, initkwargs=None, *, return_as_is=False):
        initkwargs = initkwargs or {}
        entrytext_tab_list_comp_initkwargs = {
            'template_name': 'blog/base/entrywithtext/entrywithtext_tab_list_as_item_of_list.html',
            'truncate_length_default': 255
        }
        initkwargs['entrytext_tab_list_comp_initkwargs'] = entrytext_tab_list_comp_initkwargs
        return super().get_content_list_item(obj, initkwargs, return_as_is=return_as_is)


class EntryWithTextFilterListComp(EntryWithTextItemListComp, entry_comp.EntryFilterListComp):
    form_class = EntryWithTextFilterForm
    template_name = 'blog/base/entrywithtext/entrywithtext_filter_list.html'
    urls = Urls(
        list=('blog:staff:entrywithtext_list', {})
    )

    def set_filter_body_text(self, queryset, value, form):
        if value:
            queryset = queryset.filter(entrytext__body_text__icontains=value)
        return queryset


class EntryWithTextPreInitializedFilterFormListComp(PreInitializedFilterFormMixin, EntryWithTextFilterListComp):
    pass
