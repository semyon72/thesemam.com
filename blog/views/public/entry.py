# Project: blog_7myon_com
# Package: 
# Filename: entry.py
# Generated: 2021 Mar 03 at 08:37 
# Description of <entry>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import functools

from django.core.paginator import Paginator, Page, PageNotAnInteger, EmptyPage
from django.db.models import Prefetch
from django.utils.safestring import mark_safe

from sm_flexdata.html.contenttools import HTMLTruncator, TextTruncator, StringTruncator
from sm_flexdata.urls import Urls, resolve_attr
from sm_flexdata.views.generic import InitialDetailView, RepeatListView

from ...models import Entry, EntryText, Author
from ...text_tools import strip_tags, highlight_found_text
from ...urls import settings


class CoauthorItemView(InitialDetailView):
    template_name = 'blog/public/entry_detail_author_item.html'
    pk_url_kwarg = 'id'
    model = Author
    urls = Urls(
        index_by_author=(settings.get_view_name('index_by_author'), {pk_url_kwarg: resolve_attr('object.pk')}),
        index_contact=(settings.get_view_name('index_contact'), {})
    )


class CoauthorListView(RepeatListView):
    repeat_view_class = CoauthorItemView


class EntryView(InitialDetailView):
    template_name = 'blog/public/entry_detail.html'

    model = Entry
    queryset = model.objects.filter(inactive=False)

    pk_url_kwarg = 'id'
    page_kwarg = 'text'

    truncate_text_to_length = 0
    truncate_text_to_length_url_kwarg = 'tl'

    search_text_url_kwarg = 'q'
    found_text_prefix = '<span class="found-text">'
    found_text_suffix = '</span>'

    urls = Urls(
        index_by_author=(settings.get_view_name('index_by_author'), {pk_url_kwarg: resolve_attr('object.author.pk')}),
        index_by_blog=(settings.get_view_name('index_by_blog'), {pk_url_kwarg: resolve_attr('object.blog.pk')}),
        entry=(settings.get_view_name('index_entry'), {pk_url_kwarg: resolve_attr('object.pk')}),
        index_contact=(settings.get_view_name('index_contact'), {})
    )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.truncate_text_to_length = self.request.GET.get(
            self.truncate_text_to_length_url_kwarg, 0
        ) or self.truncate_text_to_length

    @functools.cached_property
    def search_text(self):
        return self.request.GET.get(self.search_text_url_kwarg, '').strip()

    def get_entrytext_queryset(self, entry):
        qs = entry.entrytext_set.all()
        return qs

    def _process_body_text(self, entrytext_page: Page):
        if len(entrytext_page) < 1:
            return

        truncator, tl = (HTMLTruncator(), self.truncate_text_to_length)
        truncator.ellipsis.tag = 'span'
        truncator.ellipsis.attrs = {'class': 'truncated-text'}
        truncator.ellipsis.add_data(StringTruncator.ellipsis)

        _ellipsis, search_text = (StringTruncator.ellipsis, self.search_text)
        text_truncator = TextTruncator(needles=search_text.split())
        text_truncator.result_max_length = tl if tl > 0 else -1

        if tl > 0:
            truncator.max_plain_text_length = tl
            StringTruncator.ellipsis = '%s%s%s' % ('<span class="truncated-text">', _ellipsis, '</span>')

        for i, entrytext in enumerate(entrytext_page.object_list):
            if i > 0:
                truncator.reset()

            if search_text:
                text_truncator.haystack = strip_tags(entrytext.fields['body_text']['value'])
                fk = 'body_text_highlighted'
                fv = mark_safe(str(text_truncator))
                entrytext.fields[fk] = entrytext.create_fields_item(None, fk.replace('_', ' ').capitalize(), fv)

            entrytext.fields['body_text']['value'] = str(truncator.feed(entrytext.fields['body_text']['value']))

        # return to back
        if tl:
            StringTruncator.ellipsis = _ellipsis

    def _process_headline(self, entry):
        # headline = strip_tags(entry.fields['headline']['value'])
        headline = entry.fields['headline']['value']
        entry.fields['headline']['value'] = \
            highlight_found_text(headline, self.search_text, self.found_text_prefix, self.found_text_suffix)

    def get_paginated_entrytext(self, entry):
        qs = self.get_entrytext_queryset(entry)
        paginator = Paginator(qs, 1)
        return paginator.get_page(self.request.GET.get(self.page_kwarg, 1))

    def get_coauthors_content(self, coauthors):
        result = ''
        if coauthors.exists():
            response = CoauthorListView.as_view(queryset=coauthors.all())(self.request, *self.args, **self.kwargs)
            response = response.render()
            result = mark_safe(response.content.decode(encoding=response.charset))
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = context['object']
        entrytext_page_obj = self.get_paginated_entrytext(entry)
        context['entrytext_page_obj'] = entrytext_page_obj
        context['coauthors_content'] = self.get_coauthors_content(entry.coauthors)
        self._process_body_text(entrytext_page_obj)
        self._process_headline(entry)

        return context


class EntryListView(RepeatListView):
    template_name = 'blog/public/entry_list.html'
    paginate_by = 10
    model = Entry
    truncate_text_to_length = 256
    repeat_view_class = EntryView
    queryset = model.objects.filter(inactive=False).order_by('-pub_date').select_related()\
        .prefetch_related(
        'coauthors', Prefetch('entrytext_set', queryset=EntryText.objects.order_by('pk'))
    )

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):

        # logic is copied from Paginator.get_page(self, number):
        # for excluding an exception when page_number exceeds the max value
        def _get_page(page_number=1):
            try:
                number = paginator.validate_number(page_number)
            except PageNotAnInteger:
                number = 1
            except EmptyPage:
                number = paginator.num_pages
            return paginator._page(number)

        paginator = super().get_paginator(queryset, per_page, orphans, allow_empty_first_page, **kwargs)
        paginator._page = paginator.page

        paginator.page = _get_page
        return paginator

    def get_content_list_item(self, obj, initkwargs=None):
        initkwargs = {'truncate_text_to_length': self.truncate_text_to_length}
        return super().get_content_list_item(obj, initkwargs)
