# Project: blog_7myon_com
# Package: 
# Filename: blog.py
# Generated: 2021 Mar 01 at 20:41 
# Description of <blog>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from blog.models import Author

from sm_flexdata.urls import Urls, resolve_attr
from sm_flexdata.views.generic.initial import InitialDetailView
from sm_flexdata.views.generic.repeat import RepeatListView

from .common import PopularViewMixin
from ...urls import settings


class AuthorInfoItemView(PopularViewMixin, InitialDetailView):
    template_name = 'blog/public/author_aside_item.html'
    model = Author
    urls = Urls(
        index_by=(settings.get_view_name('index_by_author'), {'id': resolve_attr('object.pk')})
    )

    def get_queryset(self):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return super().get_queryset().filter(pk=pk)


class AuthorInfoListView(PopularViewMixin, RepeatListView):
    template_name = 'blog/public/author_aside.html'
    repeat_view_class = AuthorInfoItemView
    model = Author
    page_kwarg = 'aap'

    def get_queryset(self):
        return super().get_queryset().select_related('user')
