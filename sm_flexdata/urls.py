# Project: blog_7myon_com
# Package: 
# Filename: urls.py
# Generated: 2021 May 29 at 18:39 
# Description of <urls>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from functools import wraps

from django.urls import NoReverseMatch, reverse
from django.views import View


def get_value_for(obj, attr_path):
    """
    :param obj: is start object to resolve the value for start_obj.attr_name.attr_name1.attr_name2
    :param attr_path: str Like attr_name.attr_name1.attr_name2
    :return: object that represents value of attr_name.attr_name1.attr_name2 or
     error message if one of attribute or sub-attribute has not exist
    """
    attr_list = attr_path.split('.')
    cobj = obj
    for attr in attr_list:
        try:
            tobj = getattr(cobj, attr)
        except AttributeError as err:
            return str(err)
        else:
            cobj = tobj

    return None if cobj is obj else cobj


def resolve_attr(path: str = ''):
    """
    :param path: str Like attr_name.attr_name1.attr_name2
    :return: string that represents value of attr_name.attr_name1.attr_name2 or
     error message if one of attribute or sub-attribute has not exist
    """
    @wraps(resolve_attr)
    def _wrapper_(obj, url_param_name, viewname):
        val = get_value_for(obj, path)
        return '' if val is None else str(val)
    return _wrapper_


class Urls:

    settings = None
    """
        dictionary where each key is 'some_content_name' and value is 'view_name' or ('view_name', default_kwparameters)
        where 'view_name' is something like 'appname:namespace:url_path_name'.
        if url does not need to be parameterised then default_kwparameters should be omitted.
        default_kwparameters are intended for parameterised url and
        must be some value that possible be converted into dict object   
    """

    def __init__(self, **kwargs):
        """
            kwargs are set of 'content_name': 'view_name' or ('view_name', default_kwparameters)
            what will interpreted as pair of default parameters for evaluation the 'view_name'

            :param kwargs:
        """
        self._attr_name = None
        self.settings = {}
        for k, v in kwargs.items():
            self.add(k, v)

    def __set_name__(self, owner, name):
        self._attr_name = name

    def __get__(self, instance, owner=None):
        if not instance:
            return self
        result = self.reverse_all(instance)
        setattr(instance, self._attr_name, result)
        return result

    @staticmethod
    def get_current_app(instance, request=None):
        current_app = None
        if request is None and isinstance(instance, View):
            request = instance.request
        if request:
            current_app = request.resolver_match.namespace
        return current_app

    def _reverse(self, viewname, params, instance, current_app):
        # viewname is string like app:ns:path_name and params are parameters (dict) for reverse by viewname
        kwargs = {}
        for url_param_name, v in params.items():
            if callable(v):
                kwargs[url_param_name] = v(instance, url_param_name, viewname)
            else:
                kwargs[url_param_name] = v

        return reverse(viewname, kwargs=kwargs, current_app=current_app)

    def reverse_for(self, key, instance, request=None, none_if_fail=False):
        """
        :param key: Key in self.settings
        :param instance: This parameter will be passed into get_value_for(...) as obj parameter
        if you use resolve_attr(attr_path) or other callable as value of named parameter for reverse function.
        also if request=None and instance is instance of View then it will used to resolve current_app automatically
        :param request: It will used to get current_app that used as same named parameter in reverse function.
        :param none_if_fail: if False - will return error string if key is not exists or NoReverseMatch. Otherwise - None
        :return: url or error string. No exception will be raised.
        """
        result = None
        if not none_if_fail:
            result = 'Urls settings has no item with key %s. Available keys are "%s"' % (key, ','.join(self.settings.keys()))

        current_app = self.get_current_app(instance, request)
        viewname = self.settings.get(key)
        if viewname:
            # viewname[0] is viewname (string like app:ns:path_name) and viewname[1] parameters for viewname[0]
            try:
                result = self._reverse(viewname[0], viewname[1], instance, current_app)
            except NoReverseMatch as err:
                if not none_if_fail:
                    result = 'Context key is "%s": NoReverseMatch "%s"' % (key, err)

        return result

    def reverse_all(self, instance, request=None):
        result = {}
        current_app = self.get_current_app(instance, request)
        for key, (viewname, params) in self.settings.items():
            # key is context key (key in result dictionary)
            # viewname is string like app:ns:path_name and params are parameters for reversing the viewname
            try:
                result[key] = self._reverse(viewname, params, instance, current_app)
            except NoReverseMatch as err:
                result[key] = 'Context key is "%s": NoReverseMatch "%s"' % (key, err)
        return result

    def add(self, key, viewname):
        resv = []
        if isinstance(viewname, str):
            resv.append(viewname)
        elif hasattr(viewname, '__iter__'):
            i = 0
            for v in viewname:
                if i == 0:
                    resv.append(str(v))
                    resv.append({})
                else:
                    try:
                        v = dict(v)
                    except ValueError as err:
                        err.args = ('positional parameters are not supported',) + err.args
                        raise err
                    else:
                        resv[1].update(v)
                i += 1

        self.settings[key] = resv
