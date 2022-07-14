# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2021 Jun 02 at 06:00 
# Description of <test_deferred>
#

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View
from django.views.generic import RedirectView

from ..views.generic.deferred import DeferredViewMixin


class ExampleDeferredView(DeferredViewMixin, View):

    response_content = 'Hello world!'

    def get(self, request, *args, **kwargs):
        response = HttpResponse()
        response.content = self.response_content
        return response


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class TestDeferredView(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_common_behaviour(self):
        request = self.factory.get('/')
        view_obj = ExampleDeferredView.as_view(return_response_immediately=False)(request)
        self.assertTrue(hasattr(view_obj, 'render') and callable(view_obj.render))
        self.assertTrue(str(view_obj) == ExampleDeferredView.response_content)

        contentstr = 'Changed via initkwargs %s' % ExampleDeferredView.response_content
        view_obj = ExampleDeferredView.as_view(return_response_immediately=False, response_content=contentstr)(request)
        self.assertTrue(id(view_obj.response_content) != id(type(view_obj).response_content))
        self.assertListEqual(
            sorted(view_obj._initkwargs_names, key=hash),
            sorted(('return_response_immediately', 'response_content'), key=hash)
        )
        self.assertTrue(str(view_obj) == contentstr)

        # next two lines reset cached_property(response)
        view_obj._response = None
        delattr(view_obj, 'response')
        # test multiple processing
        contentstr = 'Changed via obj.response_content %s'
        for i in range(3):
            resstr = contentstr % id(object())
            view_obj.response_content = resstr
            self.assertTrue(str(view_obj.get_content()) == resstr)
            if i == 0:
                self.assertTrue(str(view_obj) == resstr)
            else:
                self.assertFalse(str(view_obj) == resstr)

        # test further inheritance
        deferred_view = type('Example1DeferredView', (ExampleDeferredView, ), {})
        view_obj = deferred_view.as_view(
            return_response_immediately=False,
            response_content=contentstr
        )(request)
        self.assertTrue(str(view_obj) == contentstr)

        # test contentless View-s and HttpResponse-s
        url = '/tt/rr'
        attrs = {
            'return_response_immediately': False,
            'response_content': '',
            'url': url
        }
        deferred_view = type('RedirectDeferredView', (DeferredViewMixin, RedirectView), attrs)
        view_obj = deferred_view.as_view(response_content=contentstr)(request)
        self.assertTrue(view_obj.content.decode() == '')

        # test using as regular View (behaviour by default) that returns response immediately
        view_obj = ExampleDeferredView.as_view()(request)
        self.assertEqual(bytes(view_obj), b'Content-Type: text/html; charset=utf-8\r\n\r\nHello world!')
        self.assertEqual(view_obj.status_code, 200)

        view_obj = ExampleDeferredView.as_view(return_response_immediately=False)(request)
        response = view_obj.render()
        self.assertEqual(response, view_obj.response)
