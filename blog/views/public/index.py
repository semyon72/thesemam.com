# Project: blog_7myon_com
# Package: 
# Filename: index.py
# Generated: 2021 Mar 10 at 16:03 
# Description of <index>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.utils.translation import gettext as _

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from sm_flexdata.views import DeferredViewMixin
from sm_flexdata.views.generic.multi import MultiViewTemplateView
from .about import AboutView
from .contact import ContactView, ContactSuccessView
from .entry import EntryListView, EntryView
from .author import AuthorInfoListView
from .blog import BlogInfoListView
from .search import SearchEntryListView

from ...models import Entry, Author, Blog, EntryText


default_entry_queryset = Entry.objects.filter(inactive=False).order_by('-pub_date')\
                         .select_related().prefetch_related(
    'coauthors', Prefetch('entrytext_set', queryset=EntryText.objects.order_by('pk'))
)


class IndexBaseView(MultiViewTemplateView):
    template_name = 'blog/public/index.html'
    view_settings = {
        'author_aside_full': AuthorInfoListView,
        'blog_aside_full': BlogInfoListView,
        'body_content': (EntryListView, {
            'queryset': default_entry_queryset
        }),
    }

    active_context_keys = ('body_content', )


class IndexView(IndexBaseView):
    title = _('All entries')


class IndexByAuthorView(IndexBaseView):
    pk_url_kwarg = 'id'
    model = Author
    entry_model_field_name = model._meta.model_name
    title = _('Author')

    def setup_entrylistview(self, initkwargs):
        obj = get_object_or_404(self.model, pk=self.kwargs.get(self.pk_url_kwarg))
        self.title = '{}: "{}"'.format(self.title, str(obj))
        initkwargs['queryset'] = initkwargs['queryset'].filter(**{self.entry_model_field_name: obj})


class IndexByBlogView(IndexByAuthorView):
    model = Blog
    entry_model_field_name = model._meta.model_name
    title = _('Blog')


class IndexEntryView(IndexBaseView):
    pk_url_kwarg = 'id'
    view_settings = {
        'body_content': (
            type('DeferredEntryView', (DeferredViewMixin, EntryView), {'return_response_immediately': False})
        )
    }
    title = _('Entry')

    def process_response(self, view_response, context_key):
        response = super().process_response(view_response, context_key)
        if context_key == 'body_content':
            self.title = '%s: "%s"' % (self.title, view_response.object.headline)
        return response


class IndexSearchView(IndexBaseView):
    view_settings = {
        # if we want to change view for context key that defined in parent class already then
        # we must fill (renew) all initkwargs that consumes this view
        # even if it has same value as in parent class.
        'body_content': (SearchEntryListView, {'queryset': default_entry_queryset})
    }
    title = _('Search')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        self.title = '{}: "{}"'.format(
            self.title,
            self.request.GET.get(self.view_settings['body_content'][0].search_kwarg, "")
        )
        return data


class IndexAboutView(IndexBaseView):
    template_name = 'blog/public/index.html'
    view_settings = {'body_content': (AboutView,)}
    title = _('About')


class IndexContactView(IndexBaseView):
    template_name = 'blog/public/index.html'
    view_settings = {'body_content': ContactView}
    title = _('Contact')


class IndexContactSuccessView(IndexBaseView):
    template_name = 'blog/public/index.html'
    view_settings = {'body_content': ContactSuccessView}
    title = _('Contact')
