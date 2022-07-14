# Project: blog_7myon_com
# Package: 
# Filename: viewmixin_mocks.py
# Generated: 2021 Jun 03 at 23:01 
# Description of <viewmixin_mocks>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from collections import UserList

from django.template import loader, engines
from django.template.backends import django
from django.test import TestCase, RequestFactory
from django.template.base import Template
from django.template.context import Context

from sm_flexdata.views.generic.initial import InitialDetailView


pk_url_kwarg = 'pk'


class MockModel:
    name_value_template = '[%s] %s.name is %r'

    def __init__(self, index, *args, **kwargs):
        self.name = self.name_value_template % (index, type(self).__name__, self)

    @classmethod
    def get_list(cls, length=15):

        def filter(*args, **kwargs):
            result._filter_values = kwargs
            return result

        def get(*args, **kwargs):
            result._filter_values.update(kwargs)
            pk = result._filter_values.get(pk_url_kwarg, 0)
            result._filter_values.clear()
            return result[pk]

        result = UserList([cls(i) for i in range(length)])
        result._filter_values = {}
        result.filter = filter
        result.get = get
        result.objects = result
        result._default_manager = result
        result.all = lambda: result
        result.count = lambda: len(result)

        return result

    def __str__(self) -> str:
        return self.name


class MockInitialDetailView(InitialDetailView):
    template_parts = ['<row>', '{{ object }}', '</row>\r\n']

    # template_name = django.DjangoTemplates({
    #     'OPTIONS': {},
    #     'NAME': {},
    #     'DIRS': {},
    #     'APP_DIRS': []
    # }).from_string('<row>{{ object }}</row>\r\n')
    # template_name = engines.all()[0].from_string('<row>{{ object }}</row>\r\n')
    template_name = engines['django'].from_string(''.join(template_parts))

    queryset = MockModel.get_list()

    def get_template_names(self):
        return self.template_name
