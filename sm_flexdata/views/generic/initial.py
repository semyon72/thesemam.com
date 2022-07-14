# Project: blog_7myon_com
# Package: 
# Filename: initial.py
# Generated: 2021 Jun 01 at 20:45 
# Description of <initial>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.views.generic import DetailView


class InitialObjectMixin:

    initial_object = None

    def __init__(self, *args, **initkwargs) -> None:
        super().__init__(*args, **initkwargs)

        required_attr_name = 'get_object'
        if not hasattr(self, required_attr_name):
            raise AttributeError(
                '%s is not applicable to instance that has no %s attribute.' % (type(self).__name__, required_attr_name)
            )

        self.initial_object = initkwargs.pop('initial_object', None)

    def get_object(self, queryset=None):
        return self.initial_object or super().get_object(queryset)


class InitialDetailView(InitialObjectMixin, DetailView):
    pass

