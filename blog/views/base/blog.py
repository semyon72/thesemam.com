# Project: blog_7myon_com
# Package: 
# Filename: blog.py
# Generated: 2020 Oct 13 at 15:11 
# Description of <blog>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.db.models import OuterRef, Count
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView
from sm_flexdata.urls import Urls, resolve_attr

from blog.models import Blog, Entry, Author
from blog.forms.base.blog import BlogModelForm, BlogFilterForm

from . import CommonGenericViewsAttributeMixin

from sm_flexdata.views import (
    FilterFormListView, InitialDetailView, RepeatListView,
    MultiViewTemplateView, RepeatListViewMixin
)

pk_url_kwarg = CommonGenericViewsAttributeMixin.pk_url_kwarg


COMMON_BLOG_ACTION_URLS = Urls(
    by_blog_list=('blog:staff:entry_by_blog_list', {
        pk_url_kwarg: resolve_attr('object.pk')
    }),
    list=('blog:staff:blog_list', {}),
    create=('blog:staff:blog_create', {}),
    detail=('blog:staff:blog_detail', {pk_url_kwarg: resolve_attr('object.pk')}),
    update=('blog:staff:blog_update', {pk_url_kwarg: resolve_attr('object.pk')}),
    delete=('blog:staff:blog_delete', {pk_url_kwarg: resolve_attr('object.pk')}),
)


entry_count_sq = Entry.objects.values('blog').filter(blog=OuterRef('pk')).annotate(entry_count=Count('pk', distinct=True)).values('entry_count')
author_count_sq = Entry.objects.values('blog').filter(blog=OuterRef('pk')).annotate(author_count=Count('author', distinct=True)).values('author_count')
COMMON_BLOG_QUERYSET = Blog.objects.annotate(entry_count=entry_count_sq, author_count=author_count_sq).order_by('pk')


class BlogItemView(InitialDetailView):
    pk_url_kwarg = CommonGenericViewsAttributeMixin.pk_url_kwarg
    template_name = 'blog/base/blog/blog_item.html'
    queryset = COMMON_BLOG_QUERYSET
    urls=COMMON_BLOG_ACTION_URLS


class BlogItemListView(RepeatListView):
    paginate_by = 10
    queryset = COMMON_BLOG_QUERYSET
    template_name = 'blog/base/blog/blog_item_list.html'
    repeat_view_class = BlogItemView
    urls = Urls(create=('blog:staff:blog_create', {}))


class BlogFilterListView(BlogItemListView, FilterFormListView):
    template_name = 'blog/base/blog/blog_filter_list.html'
    form_class = BlogFilterForm


class BlogView(MultiViewTemplateView):
    template_name = 'blog/base/blog/list.html'
    view_settings = {
        'content': (BlogFilterListView, {})  # (view_class, {initkwargs})
    }


class BlogCommonAttributeMixin(CommonGenericViewsAttributeMixin):
    # model = Blog
    queryset = COMMON_BLOG_QUERYSET
    form_class = BlogModelForm
    urls = COMMON_BLOG_ACTION_URLS


class BlogCreateView(BlogCommonAttributeMixin, CreateView):
    template_name = 'blog/base/blog/create.html'


class BlogDetailView(BlogCommonAttributeMixin, DetailView):
    template_name = 'blog/base/blog/detail.html'


class BlogUpdateView(BlogCommonAttributeMixin, UpdateView):
    template_name = 'blog/base/blog/edit.html'


class BlogDeleteView(BlogCommonAttributeMixin, DeleteView):
    template_name = 'blog/base/blog/delete.html'
