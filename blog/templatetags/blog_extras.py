# Project: blog_7myon_com
# Package: 
# Filename: blog_extras.py
# Generated: 2020 Oct 17 at 19:19 
# Description of <blog_extras>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django import template
from django.forms.utils import pretty_name
from django.db.models import Model, Field
from django.template import RequestContext
from django.forms.models import ModelForm
from django.utils.text import capfirst

from blog.views.base.content_tools import create_button

register = template.Library()


@register.filter(name='concat')
def concat(val, arg):
    return ''.join([str(val), str(arg)])


@register.filter(name='verbose_name')
def verbose_name(obj: Model, fieldname):
    # Logic is same as in django.forms.boundfield.BoundField.__init__(...) by default
    result = pretty_name(fieldname)
    if obj is None:
        return result
    # No differences this is Model or instance
    found_field = [ f for f in obj._meta.get_fields() if f.name == fieldname]
    if not found_field:
        return result

    field: Field = found_field[0]
    if field.verbose_name:
        # Logic is same as in django.db.models.fields.Field.formfield(...)
        # Probably, field.formfield().label can be used instead but we try to reduce the extra loading
        result = capfirst(field.verbose_name)

    return result


@register.simple_tag()
def get_attr(obj, attr):
    """
    Returns, either dictionary value by attr value which interpreted as dictionary key
    or object's attribute by attr value which interpreted as attribute name
    or None if attr was not found.
    :param obj: Object from which we are going to get attr value.
    If Object is dict then will be returned obj[attr] value.
    :param attr: string Either key of dictionary or object's attribute name
    :return:
    """
    if isinstance(obj, dict):
        return obj.get(attr)
    else:
        return getattr(obj, attr, None)


@register.simple_tag()
def is_contains(seq, value, attr=None):
    """
    Returns True if value in sequence and attr is None.
    for example {% is_contains some_dict.values 'some_value' as is_value_exists %}
    And also returns True if value in sequence where each item is object and attr
    is string that identify name of attribute of object.
    {% is_contains some_dict.values 'some_value' 'some_attribute_name' as is_value_exists %}
    or {% is_contains some_list 'some_value' 'some_attribute_name' as is_value_exists %}
    :param seq: sequence
    :param value: value
    :param attr: attribute name if need to compare attribute's value of item of sequence
    :return:
    """
    for v in seq:
        if attr is not None:
            try:
                av = getattr(v, attr)
            except AttributeError:
                return False
            else:
                if av == value:
                    return True
        elif v == value:
            return True

    return False

def get_real_value(kv, context):
    if not isinstance(kv, str):
        return kv
    sep = '__'
    kvlist = kv.split(sep)
    if len(kvlist) == 1:  # was nothing split
        return kv

    if not kvlist[0]:
        kvlist.pop(0)

    obj = context
    while len(kvlist) > 0:
        attr = kvlist.pop(0)
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
            if callable(obj):
                obj = obj()
        elif hasattr(obj, '__getitem__'):
            obj = obj[attr]
        else:
            raise KeyError('Context does not contain "%s" attribute' % kv)

    return obj


@register.simple_tag(takes_context=True)
def get_querystring(context, *args, **kwargs):
    query_leader = '?'
    if len(args) > 0:
        if args[0] in ('', '&'):
            query_leader = args[0]
        else:
            raise ValueError (
                '"get_querystring" template tag got not supported leading querystring marks.'
                'Tag supports only next set of leading querystring marks ("?", "", "&").'
                'If first positional argument is omitted then "?" will used by default'
            )

    querystring = ''
    if context.request:
        updated = context.request.GET.copy()
        for k, value in kwargs.items():
            rk = get_real_value(k, context)
            if not rk:
                continue
            rk = str(rk)
            rv = get_real_value(value, context)
            if rv is None:
                if rk in updated:
                    del (updated[rk])
                continue
            updated[rk] = rv
        querystring = updated.urlencode()

    return query_leader+querystring if querystring else ''


@register.simple_tag(takes_context=True)
def change_context(context, **kwargs):
    for k, value in kwargs.items():
        context[k] = get_real_value(value, context)
    return ''


@register.simple_tag
def button(*args, **kwargs):
    type = args[0]
    url = kwargs.pop('url', '')
    return create_button(type, *args[1:], url=url, **kwargs)
