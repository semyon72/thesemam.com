# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2021 Jun 03 at 12:17 
# Description of <test_initial>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from difflib import SequenceMatcher

from django.test import TestCase, RequestFactory

from .viewmixin_mocks import pk_url_kwarg, MockInitialDetailView, MockModel


class TestInitialDetailView(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_common_behaviour(self):
        pk = 7
        request = self.factory.get('/<int:%s>/' % pk_url_kwarg, {pk_url_kwarg: pk})

        obj = MockModel('INITIALIZED_OBJECT')
        test_str = MockInitialDetailView.template_name.render({'object': str(obj)})
        response = MockInitialDetailView.as_view(initial_object=obj)(request, pk=pk)
        response = response.render()
        self.assertEqual(test_str, response.content.decode(encoding=response.charset))

        pk = 3
        test_str = MockInitialDetailView.template_name.render({'object': str(MockModel(pk))})
        response = MockInitialDetailView.as_view()(request, pk=pk)
        response = response.render()
        sm = SequenceMatcher(None, test_str, response.content.decode(encoding=response.charset))
        self.assertLess(1-sm.ratio(), .1)
