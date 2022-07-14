# Project: blog_7myon_com
# Package: 
# Filename: author.py
# Generated: 2020 Oct 11 at 20:54 
# Description of <author>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from django.db.models import Count, OuterRef
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from blog.models import Author, Entry
from sm_flexdata.urls import Urls, resolve_attr

from . import CommonGenericViewsAttributeMixin

from blog.forms.base.author import AuthorModelForm, AuthorFilterForm
from sm_flexdata.views import (
    FilterFormListView, InitialDetailView, RepeatListView,
    MultiViewTemplateView, RepeatListViewMixin
)

pk_url_kwarg = CommonGenericViewsAttributeMixin.pk_url_kwarg

COMMON_AUTHOR_ACTION_URLS = Urls(
    by_author_list=('blog:staff:entry_by_author_list', {
        pk_url_kwarg: resolve_attr('object.pk')
    }),
    list=('blog:staff:author_list', {}),
    create=('blog:staff:author_create', {}),
    detail=('blog:staff:author_detail', {pk_url_kwarg: resolve_attr('object.pk')}),
    update=('blog:staff:author_update', {pk_url_kwarg: resolve_attr('object.pk')}),
    delete=('blog:staff:author_delete', {pk_url_kwarg: resolve_attr('object.pk')}),
)

# We need something like
#
# SELECT *, (
#     SELECT COUNT(distinct be.id)
#     FROM blog_entry as be
#     WHERE ba.id = be.author_id
# ) as entry_count,
# (
#     SELECT COUNT(distinct bb.id)
#     FROM blog_entry as be INNER JOIN blog_blog as bb on bb.id = be.blog_id
#     WHERE ba.id = be.author_id
# ) as blog_count
# FROM blog_author as ba

entry_count_sq = Entry.objects.values('author').filter(author=OuterRef('pk')).annotate(entry_count=Count('pk', distinct=True)).values('entry_count')
blog_count_sq = Entry.objects.values('author').filter(author=OuterRef('pk')).annotate(blog_count=Count('blog', distinct=True)).values('blog_count')
COMMON_AUTHOR_QUERYSET = Author.objects.annotate(entry_count=entry_count_sq, blog_count=blog_count_sq).order_by('pk')

# Now we have an equivalent of above
#
# SELECT "blog_author"."id", "blog_author"."user_id",
#        "blog_author"."name", "blog_author"."email",
#        (
#            SELECT COUNT(DISTINCT U0."id") AS "entry_count"
#            FROM "blog_entry" U0
#            WHERE U0."author_id" = "blog_author"."id"
#            GROUP BY U0."author_id"
#        ) AS "entry_count",
#        (
#            SELECT COUNT(DISTINCT U0."blog_id") AS "blog_count"
#            FROM "blog_entry" U0
#            WHERE U0."author_id" = "blog_author"."id"
#            GROUP BY U0."author_id"
#        ) AS "blog_count"
# FROM "blog_author"
# ORDER BY "blog_author"."id" ASC


class AuthorItemView(InitialDetailView):
    pk_url_kwarg = pk_url_kwarg
    template_name = 'blog/base/author/author_item.html'
    queryset = COMMON_AUTHOR_QUERYSET
    urls = COMMON_AUTHOR_ACTION_URLS


class AuthorItemListView(RepeatListView):
    paginate_by = 10
    queryset = COMMON_AUTHOR_QUERYSET
    template_name = 'blog/base/author/author_item_list.html'
    repeat_view_class = AuthorItemView
    urls = Urls(create=('blog:staff:author_create', {}))


class AuthorFilterListView(AuthorItemListView, FilterFormListView):
    template_name = 'blog/base/author/author_filter_list.html'
    form_class = AuthorFilterForm


class AuthorView(MultiViewTemplateView):
    template_name = 'blog/base/author/list.html'
    view_settings = {
        'content': (AuthorFilterListView, {})  # (view_class, {initkwargs})
    }


class AuthorCommonAttributeMixin(CommonGenericViewsAttributeMixin):
    # model = Author
    queryset = COMMON_AUTHOR_QUERYSET
    form_class = AuthorModelForm
    urls = COMMON_AUTHOR_ACTION_URLS


class AuthorCreateView(AuthorCommonAttributeMixin, CreateView):
    template_name = 'blog/base/author/create.html'


class AuthorDetailView(AuthorCommonAttributeMixin, DetailView):
    template_name = 'blog/base/author/detail.html'


class AuthorUpdateView(AuthorCommonAttributeMixin, UpdateView):
    template_name = 'blog/base/author/edit.html'


class AuthorDeleteView(AuthorCommonAttributeMixin, DeleteView):
    template_name = 'blog/base/author/delete.html'
