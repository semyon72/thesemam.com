# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2021 Jun 05 at 15:44 
# Description of <test_multi>
#
import re

from django.test import TestCase, RequestFactory
from django.views.generic import TemplateView
from django.template import engines

from .test_repeat import MockRepeatView
from .viewmixin_mocks import MockModel, pk_url_kwarg, MockInitialDetailView
from ..views.generic.multi import MultiViewTemplateView
from ..views.generic.repeat import RepeatListView


# @author Semyon Mamonov <semyon.mamonov@gmail.com>
class FixedContentTemplateView(TemplateView):
    template_name = engines.all()[0].from_string('Some fixed content')

    def get_template_names(self):
        return self.template_name


class DetailedContentView(MockInitialDetailView):
    template_name = engines.all()[0].from_string('{{ object }}')


class RepeatContentView(MockRepeatView):
    pass


class MockBaseMultiViewTemplateView(MultiViewTemplateView):

    template_name = engines.all()[0].from_string('''
        <detailed_content>{{ detailed_content }}</detailed_content>
        <repeated_content>{{ repeated_content }}</repeated_content>
        <fixed_content>{{ fixed_content }}</fixed_content>
    ''')

    view_settings = {
        'fixed_content': FixedContentTemplateView,
        'detailed_content': (DetailedContentView, {}),
        'repeated_content': (RepeatContentView, {})
    }
    active_context_keys = ('repeated_content', )

    def get_template_names(self):
        return super().get_template_names()[0]


class MockMultiViewTemplateView(MockBaseMultiViewTemplateView):

    view_settings = {
        'detailed_content': (DetailedContentView, {'initial_object': MockModel.get_list(10)[3]})
    }


class TestMultiViewMixin(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_common_behaviour(self):
        request = self.factory.get('/')
        response = MockMultiViewTemplateView.as_view()(request)
        result = response.render().content.decode(encoding=response.charset)

        data_re = r'\[\d+\][\w&;._\-\s]+0x[0-9A-Fa-f]{8,}(?:&gt;|>)'
        tag_re = r'<%s>%s</%s>'
        tag = 'fixed_content'
        matches = re.findall(tag_re % (tag, 'Some fixed content', tag), result)
        self.assertEqual(len(matches), 1)
        tag = 'detailed_content'
        matches = re.findall(tag_re % (tag, data_re, tag), result)
        self.assertEqual(len(matches), 1)
        tag = 'repeated_content'
        matches = re.findall(tag_re % (tag, r'.+', tag), result, re.S)
        self.assertEqual(len(matches), 1)
        tag = 'row'
        matches = re.findall(tag_re % (r'.*('+tag, data_re, tag+ r')+.*'), matches[0])
        self.assertEqual(len(matches), 10)
