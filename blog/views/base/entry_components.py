# Project: blog_7myon_com
# Package: 
# Filename: entry_parts.py
# Generated: 2021 Jun 17 at 08:37 
# Description of <entry_parts>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.db.models import Prefetch
from django.forms import Form
from django.utils.safestring import mark_safe
from django.views.generic import DetailView

from blog.models import Entry, Author, EntryText
from blog.forms.base.entry import (EntryFilterForm, )
from blog.views.base import PreInitializedFilterFormMixin
from blog.views.base.entrytext_components import EntryTextTabListComp

from sm_flexdata.urls import Urls, resolve_attr
from sm_flexdata.views import (FilterFormListView, InitialDetailView, RepeatListView,)
from sm_flexdata.views.generic.common import response_to_content
from sm_flexdata.views.generic.multi import MultiViewMixin

pk_url_kwarg = 'id'

COMMON_ENTRY_ACTION_URLS = Urls(
    list=('blog:staff:entry_list', {}),
    by_author_list=('blog:staff:entry_by_author_list', {
        pk_url_kwarg: resolve_attr('object.author.pk')
    }),
    by_blog_list=('blog:staff:entry_by_blog_list', {
        pk_url_kwarg: resolve_attr('object.blog.pk')
    }),
    create=('blog:staff:entry_create', {}),
    detail=('blog:staff:entry_detail', {pk_url_kwarg: resolve_attr('object.pk')}),
    update=('blog:staff:entry_update', {pk_url_kwarg: resolve_attr('object.pk')}),
    delete=('blog:staff:entry_delete', {pk_url_kwarg: resolve_attr('object.pk')}),
)


class EntryCoauthorItemComp(InitialDetailView):
    template_name = 'blog/base/entry/entry_coauthor_item.html'
    pk_url_kwarg = pk_url_kwarg
    queryset = Author.objects.all()
    urls = Urls(
        by_author_list=('blog:staff:entry_by_author_list', {
            pk_url_kwarg: resolve_attr('object.pk')
        }),
    )


class EntryCoauthorItemListComp(RepeatListView):
    template_name = 'blog/base/entry/entry_coauthor_item_list.html'
    # By default it will return only those Author-s who pointed in entries as coauthor
    # queryset = Author.objects.filter(
    #     pk__in=Author.objects.filter(entries_as_coauthor_set__isnull=False).values('pk').distinct()
    # )
    queryset = Author.objects.filter(entries_as_coauthor_set__isnull=False).distinct().order_by('pk')
    repeat_view_class = EntryCoauthorItemComp
    # if need to use pagination then uncomment below
    # paginate_by = 10
    # page_kwarg = 'capage'
    # ordering = ('pk',)


class EntryItemComp(InitialDetailView):
    pk_url_kwarg = pk_url_kwarg
    template_name = 'blog/base/entry/entry_item.html'
    queryset = Entry.objects.all()
    urls = COMMON_ENTRY_ACTION_URLS

    def get_coauthors_content(self, coauthors):
        result = ''
        if coauthors:
            response = EntryCoauthorItemListComp.as_view(queryset=coauthors)(self.request, *self.args, **self.kwargs)
            response = response.render()
            result = mark_safe(response.content.decode(encoding=response.charset))
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = context['object']
        # list(entry.coauthors.all()) is fix for removing the extra SQL requests
        # because entry.coauthors.all() at now is still cached by prefetch_related
        # in main queryset for all EntryView in EntryItemListView.queryset
        # but further entry.coauthors.all() will be paginated and it will
        # clear cache
        context['coauthors_content'] = self.get_coauthors_content(list(entry.coauthors.all()))
        return context


class EntryItemListComp(RepeatListView):
    template_name = 'blog/base/entry/entry_item_list.html'
    repeat_view_class = EntryItemComp
    # main queryset for all EntryView
    queryset = Entry.objects.order_by('-mod_date').select_related().prefetch_related(
        'coauthors',
        Prefetch('entrytext_set', EntryText.objects.order_by('pk'))
    )
    paginate_by = 10
    urls = Urls(
        create=('blog:staff:entry_create', {})
    )


class EntryFilterListComp(EntryItemListComp, FilterFormListView):
    template_name = 'blog/base/entry/entry_filter_list.html'
    form_class = EntryFilterForm
    urls = Urls(
        list=('blog:staff:entry_list', {}),
        create=('blog:staff:entry_create', {})
    )

    def set_filter_coauthors(self, queryset, value, form):
        if value:
            entry_author_qs = queryset.model.coauthors.through.objects.filter(author__in=value)
            sub_query = entry_author_qs.distinct().values_list('entry_id', flat=True).query
            queryset = queryset.filter(pk__in=sub_query)
        return queryset

    def get_filter_kwargs(self, field_name, value, kwargs=None, form: Form = None):
        exclude_fields = ('pub_date', 'pub_date_end', 'mod_date', 'mod_date_end', 'coauthors')
        if field_name not in exclude_fields:
            # default processing
            super().get_filter_kwargs(field_name, value, kwargs, form)
        else:

            def add_date_conditions(fname, end_range_fname):
                if query_data[fname] and query_data[end_range_fname]:
                    kwargs[fname+'__range'] = (query_data[fname], query_data[end_range_fname])
                elif query_data[end_range_fname]:
                    kwargs[fname+'__lte'] = query_data[end_range_fname]
                elif query_data[fname]:
                    kwargs[fname+'__gte'] = query_data[fname]

            query_data = form.cleaned_data
            if field_name == 'pub_date':
                add_date_conditions('pub_date', 'pub_date_end')
            if field_name == 'mod_date':
                add_date_conditions('mod_date', 'mod_date_end')


class EntryPreInitializedFilterFormListComp(PreInitializedFilterFormMixin, EntryFilterListComp):
    pass