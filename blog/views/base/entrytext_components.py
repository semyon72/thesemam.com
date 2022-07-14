# Project: blog_7myon_com
# Package: 
# Filename: entrytext_components.py
# Generated: 2021 Jun 17 at 09:00 
# Description of <entrytext_components>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.views.generic import ListView

from blog.forms.base.entry import EntryTextFilterForm
from blog.models import EntryText
from sm_flexdata.urls import Urls, resolve_attr
from sm_flexdata.views import (
    FilterFormListView, RepeatListView, DeferredViewMixin, InitialDetailView
)
from sm_flexdata.views.generic.common import AttrTruncateMixin


pk_url_kwarg = 'id'

COMMON_ENTRYTEXT_ACTION_URLS = Urls(
    list=('blog:staff:entrytext_list', {}),
    by_author_list=('blog:staff:entry_by_author_list', {
        pk_url_kwarg: resolve_attr('object.entry.author.pk')
    }),
    by_blog_list=('blog:staff:entry_by_blog_list', {
        pk_url_kwarg: resolve_attr('object.entry.blog.pk')
    }),
    create=('blog:staff:entrytext_create', {}),
    detail=('blog:staff:entrytext_detail', {pk_url_kwarg: resolve_attr('object.pk')}),
    update=('blog:staff:entrytext_update', {pk_url_kwarg: resolve_attr('object.pk')}),
    delete=('blog:staff:entrytext_delete', {pk_url_kwarg: resolve_attr('object.pk')}),
)


COMMON_ENTRYTEXT_QUERYSET = EntryText.objects.select_related().all().order_by('-pk')


class EntryTextItemComp(AttrTruncateMixin, DeferredViewMixin, InitialDetailView):
    template_name = 'blog/base/entrytext/entrytext_item.html'
    truncate_length_url_kwarg = 'tl'
    truncate_attr_name = 'body_text'
    queryset = COMMON_ENTRYTEXT_QUERYSET
    pk_url_kwarg = pk_url_kwarg
    return_response_immediately = False

    urls = COMMON_ENTRYTEXT_ACTION_URLS

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self.truncate_attr(obj)
        return obj


class EntryTextItemListComp(RepeatListView):
    template_name = 'blog/base/entrytext/entrytext_item_list.html'
    repeat_view_class = EntryTextItemComp
    page_kwarg = 'text'
    paginate_by = 10
    paginator_base_url = ''
    queryset = COMMON_ENTRYTEXT_QUERYSET
    truncate_body_text_length = 256
    urls = Urls(create=('blog:staff:entrytext_create', {}))

    def get_content_list_item(self, obj, initkwargs=None):
        initkwargs = {'truncate_length_default': self.truncate_body_text_length}
        # here uses self.repeat_view_class that is an instance of InitialDetailView
        # what is mixed with DeferredViewMixin.
        # This is why self.repeat_view_class can change its properties.
        result = super().get_content_list_item(obj, initkwargs)
        vars(self.repeat_view_class).pop('urls', None)  # reset urls for new object
        # self.repeat_view_class.__dict__.pop('urls', None)  # Same as line above
        return result


class EntryTextFilterListComp(FilterFormListView, EntryTextItemListComp):
    template_name = 'blog/base/entrytext/entrytext_filter_list.html'
    form_class = EntryTextFilterForm


class EntryTextTabListComp(AttrTruncateMixin, ListView):
    template_name = 'blog/base/entrywithtext/entrywithtext_tab_list.html'

    queryset = COMMON_ENTRYTEXT_QUERYSET
    truncate_attr_name = 'body_text'
    paginate_by = 5
    page_kwarg = 'txtpage'
    urls = COMMON_ENTRYTEXT_ACTION_URLS
    paginator_base_url = ''  #  For fixing base of url if need to go on view but not current

    def truncate_object_list(self, object_list):
        if object_list and self.truncate_length:
            for obj in object_list:
                self.truncate_attr(obj)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        obj_list = context.get('object_list')
        if len(obj_list) > 0:
            # stub for resolve_attr in COMMON_ENTRYTEXT_ACTION_URLS
            stub = type('stub', (), {'object': None})()
            for obj in obj_list:
                stub.object = obj
                obj.urls = type(self).urls.reverse_all(stub, self.request)

        self.truncate_object_list(obj_list)
        return context
