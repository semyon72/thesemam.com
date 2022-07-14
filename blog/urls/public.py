# Project: blog_7myon_com
# Package: 
# Filename: urls_public.py
# Generated: 2021 Mar 01 at 20:53 
# Description of <urls_public>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.urls import path, include
from blog.views.public import author, blog, entry, index

blog_urls = [
    path('<int:pk>/info/', blog.BlogInfoItemView.as_view(), name='blog_info'),
    path('aside/', blog.BlogInfoListView.as_view(), name='blog_aside'),
]

author_urls = [
    path('<int:pk>/info/', author.AuthorInfoItemView.as_view(), name='author_info'),
    path('aside/', author.AuthorInfoListView.as_view(), name='author_aside'),
]

entry_urls = [
    path('', entry.EntryListView.as_view(), name='entry_list'),
    path('<int:id>/detail/', entry.EntryView.as_view(), name='entry_detail'),
]

index_urls = [
    path('', index.IndexView.as_view(), name='index_main'),
    path('search/', index.IndexSearchView.as_view(), name='index_search'),
    path('author/<int:id>/', index.IndexByAuthorView.as_view(), name='index_by_author'),
    path('blog/<int:id>/', index.IndexByBlogView.as_view(), name='index_by_blog'),
    path('entry/<int:id>/', index.IndexEntryView.as_view(), name='index_entry'),
    path('about/', index.IndexAboutView.as_view(), name='index_about'),
    path('contact/', index.IndexContactView.as_view(), name='index_contact'),
    path('contact/success/', index.IndexContactSuccessView.as_view(), name='index_contact_success'),
]

urlpatterns = [
    path('', include(index_urls)),
    path('blog/', include(blog_urls)),
    path('author/', include(author_urls)),
    path('entry/', include(entry_urls)),
]
