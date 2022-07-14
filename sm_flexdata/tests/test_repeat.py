# Project: blog_7myon_com
# Package: ${PACKAGE_NAME}
# Filename: ${FILE_NAME}
# Generated: 2021 Jun 03 at 12:09 
# Description of <test_repeat>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from html import escape

from django.template import engines
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .viewmixin_mocks import MockModel, MockInitialDetailView
from ..views.generic.deferred import DeferredViewMixin

from ..views.generic.repeat import RepeatListView


class MockRepeatView(RepeatListView):
    template_parts = [
        '<list>\r\n',
        '{% for content in content_list %}{{ content }}{% endfor %}',
        '</list>'
    ]
    template_name = engines['django'].from_string(''.join(template_parts))
    repeat_view_class = MockInitialDetailView

    queryset = MockModel.get_list(17)
    paginate_by = 10


class TestRepeatView(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_common_behaviour(self):

        request = self.factory.get('/some_url/', {})

        # common test
        response = MockRepeatView.as_view()(request)
        response = response.render()
        result = response.content.decode(encoding=response.charset)
        src_list = MockRepeatView.queryset[:MockRepeatView.paginate_by]
        test_str = ''.join((
            MockRepeatView.template_parts[0],
            *(MockRepeatView.repeat_view_class.template_parts[0] +
              escape(str(v)) +
              MockRepeatView.repeat_view_class.template_parts[2]
              for v in src_list),
            MockRepeatView.template_parts[2]
        ))
        self.assertEqual(test_str, result)

        # same as above
        content_list = (MockRepeatView.repeat_view_class.template_name.render({'object': v}) for v in src_list)
        test_str = MockRepeatView.template_name.render({'content_list': content_list})
        self.assertEqual(test_str, result)

        # common actions ( return_results(....) ) for code below
        def return_results(response, paginate_by, page_num):
            response = response.render()
            result = response.content.decode(encoding=response.charset)
            src_list = MockRepeatView.queryset[paginate_by*(page_num-1):paginate_by*page_num]

            content_list = (MockRepeatView.repeat_view_class.template_name.render({'object': v}) for v in src_list)
            test_str = MockRepeatView.template_name.render({'content_list': content_list})
            return test_str, result

        # paginated
        page_num, paginate_by = (2, 5)
        request = self.factory.get('/some_url/', {MockRepeatView.page_kwarg: page_num})
        response = MockRepeatView.as_view(paginate_by=paginate_by)(request)
        self.assertEqual(*return_results(response, paginate_by, page_num))

        # test for DeferredView
        deferred_inittial_detail_view = type(
            'DeferredInittialDetailView',
            (DeferredViewMixin, MockRepeatView.repeat_view_class),
            {}
        )
        page_num, paginate_by = (3, 7)
        request = self.factory.get('/some_url/', {MockRepeatView.page_kwarg: page_num})
        response = MockRepeatView.as_view(
            paginate_by=paginate_by,
            repeat_view_class=deferred_inittial_detail_view
        )(request)
        self.assertEqual(*return_results(response, paginate_by, page_num))
