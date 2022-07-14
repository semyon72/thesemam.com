# Project: blog_7myon_com
# Package: 
# Filename: common.py
# Generated: 2021 May 28 at 18:14 
# Description of <common>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from functools import cached_property

from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.safestring import mark_safe

from ...html.contenttools import StringTruncator, HTMLTruncator


def response_to_content(response):
    if not isinstance(response, HttpResponse):
        raise TypeError('response %r is not instance of HttpResponse' % response)
    if 199 > response.status_code or response.status_code > 299:
        return 'Something went wrong (if details do not visible, look at html source): %s' % response
    if hasattr(response, 'render') and callable(response.render):
        response = response.render()
    return response.content.decode(encoding=response.charset)


class AttrTruncateMixin:
    """
    Main purpose is the using in View to create truncate version
    of some object attribute (text|html). It does not work automatically.
    Need use truncate_attr(object)
        truncate_length_default = None - no truncation
        truncate_length_url_kwarg = 'tl' - request.GET parameter that will redefine default value
        truncate_attr_name = '' - source object's attribute name
        truncated_attr_name = '' - target (truncated) object's attribute name
    """

    truncate_length_default = None
    truncate_length_url_kwarg = 'tl'
    truncate_attr_name = ''
    truncated_attr_name = ''

    def get_truncated_attr_name(self):
        if self.truncated_attr_name:
            return str(self.truncated_attr_name)
        return '%s_truncated' % str(self.truncate_attr_name)

    @cached_property
    def truncate_length(self):
        ttl = self.request.GET.get(self.truncate_length_url_kwarg, None)
        if ttl is None:
            ttl = 0 if self.truncate_length_default is None else int(self.truncate_length_default)
        else:
            ttl = int(ttl)
        return ttl

    @cached_property
    def truncator(self):
        html_trunc = HTMLTruncator(self.truncate_length)
        html_trunc.ellipsis.tag = 'span'
        html_trunc.ellipsis.attrs = {'class': 'truncated-text'}
        html_trunc.ellipsis.add_data(str(StringTruncator.ellipsis))
        return html_trunc

    def truncate_attr(self, obj):
        val = getattr(obj, self.truncate_attr_name, None)
        if obj and val:
            self.truncator.reset()
            setattr(obj, self.get_truncated_attr_name(), str(self.truncator.feed(val)))



