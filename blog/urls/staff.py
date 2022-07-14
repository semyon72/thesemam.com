# Project: blog_7myon_com
# Package: 
# Filename: staff_urls.py
# Generated: 2021 Jan 25 at 15:48 
# Description of <staff_urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.urls import path, include
from blog.views.base import (
    author, blog,
    entry, entrytext, entrywithtext,
    entry_components as entry_comp,
    entrytext_components as entrytext_comp,
    entrywithtext_components as entry_text_comp,
    profile
)


author_urls = [
    path('test/item/<int:id>/', author.AuthorItemView.as_view(), name='author_test_item'),
    path('test/list/', author.AuthorItemListView.as_view(), name='author_test_list'),
    path('test/filter/list/', author.AuthorFilterListView.as_view(), name='author_test_filter_list'),
    path('test/index/', author.AuthorView.as_view(), name='author_test_index'),

    path('', author.AuthorView.as_view(), name='author_list'),
    path('create/', author.AuthorCreateView.as_view(), name='author_create'),
    path('<int:id>/', author.AuthorDetailView.as_view(), name='author_detail'),
    path('<int:id>/update/', author.AuthorUpdateView.as_view(), name='author_update'),
    path('<int:id>/delete/', author.AuthorDeleteView.as_view(), name='author_delete'),
]

blog_urls = [
    path('test/item/<int:id>/', blog.BlogItemView.as_view(), name='blog_test_item'),
    path('test/list/', blog.BlogItemListView.as_view(), name='blog_test_list'),
    path('test/filter/list/', blog.BlogFilterListView.as_view(), name='blog_test_filter_list'),
    path('test/index/', blog.BlogView.as_view(), name='blog_test_index'),

    path('', blog.BlogView.as_view(), name='blog_list'),
    path('create/', blog.BlogCreateView.as_view(), name='blog_create'),
    path('<int:id>/', blog.BlogDetailView.as_view(), name='blog_detail'),
    path('<int:id>/update/', blog.BlogUpdateView.as_view(), name='blog_update'),
    path('<int:id>/delete/', blog.BlogDeleteView.as_view(), name='blog_delete'),
]

entry_urls = [

    path('comp/coauthor/<int:id>/', entry_comp.EntryCoauthorItemComp.as_view(), name='entry_comp_coauthor_item'),
    path('comp/coauthor/', entry_comp.EntryCoauthorItemListComp.as_view(), name='entry_comp_coauthor_list'),
    path('comp/<int:id>/', entry_comp.EntryItemComp.as_view(), name='entry_comp_item'),
    path('comp/', entry_comp.EntryItemListComp.as_view(), name='entry_comp_list'),
    path('comp/filter/', entry_comp.EntryFilterListComp.as_view(), name='entry_comp_filter_list'),

    path('filter/author/<int:id>/', entry.EntryByAuthorView.as_view(), name='entry_by_author_list'),
    path('filter/blog/<int:id>/', entry.EntryByBlogView.as_view(), name='entry_by_blog_list'),
    path('', entry.EntryView.as_view(), name='entry_list'),
    path('create/', entry.EntryCreateView.as_view(), name='entry_create'),
    path('<int:id>/', entry.EntryDetailView.as_view(), name='entry_detail'),
    path('<int:id>/update/', entry.EntryUpdateView.as_view(), name='entry_update'),
    path('<int:id>/delete/', entry.EntryDeleteView.as_view(), name='entry_delete'),

    path('comp/<int:id>/text/', entry_text_comp.EntryWithTextItemComp.as_view(), name='entry_comp_with_text_item'),
    path('comp/text/', entry_text_comp.EntryWithTextItemListComp.as_view(), name='entry_comp_with_text_list'),
    path('comp/text/filter/', entry_text_comp.EntryWithTextFilterListComp.as_view(), name='entry_comp_with_text_filter_list'),

    path('text/', entrywithtext.EntryWithTextView.as_view(), name='entrywithtext_list'),
    path('text/filter/author/<int:id>/', entrywithtext.EntryWithTextByAuthorView.as_view(), name='entrywithtext_by_author_list'),
    path('text/filter/blog/<int:id>/', entrywithtext.EntryWithTextByBlogView.as_view(), name='entrywithtext_by_blog_list'),
    path('<int:id>/text/', entrywithtext.EntryWithTextDetailView.as_view(), name='entrywithtext_detail'),
    path('<int:id>/text/<int:text_id>/', entrywithtext.EntryWithTextDetailView.as_view(), name='entrywithtext_detail'),

    path('<int:id>/text/create/', entrywithtext.EntryWithTextCreateView.as_view(), name='entrywithtext_create'),
    path('<int:id>/text/<int:text_id>/update/', entrywithtext.EntryWithTextUpdateView.as_view(), name='entrywithtext_update'),
    path('<int:id>/text/<int:text_id>/delete/', entrywithtext.EntryWithTextDeleteView.as_view(), name='entrywithtext_delete'),

    #    path('<int:id>/comment/', entry.EntryCommentListView.as_view(), name='entry_comment_list'),
]

entrytext_urls = [

    path('comp/<int:id>/', entrytext_comp.EntryTextItemComp.as_view(), name='entrytext_comp_item'),
    path('comp/', entrytext_comp.EntryTextItemListComp.as_view(), name='entrytext_comp_list'),
    path('comp/filter/', entrytext_comp.EntryTextFilterListComp.as_view(), name='entrytext_comp_filter_list'),
    path('comp/tab/', entrytext_comp.EntryTextTabListComp.as_view(), name='entrytext_comp_tab_list'),

    path('', entrytext.EntryTextView.as_view(), name='entrytext_list'),
    path('create/', entrytext.EntryTextCreateView.as_view(), name='entrytext_create'),
    path('<int:id>/', entrytext.EntryTextDetailView.as_view(), name='entrytext_detail'),
    path('<int:id>/update/', entrytext.EntryTextUpdateView.as_view(), name='entrytext_update'),
    path('<int:id>/delete/', entrytext.EntryTextDeleteView.as_view(), name='entrytext_delete'),

]

profile_urls = [
    path('', profile.ProfileUpdateView.as_view(), name='profile_update')
]

urlpatterns = [
    path('', include(profile_urls)),
    path('author/', include(author_urls)),
    path('blog/', include(blog_urls)),
    path('entry/', include(entry_urls)),
    path('entrytext/', include(entrytext_urls)),
]
