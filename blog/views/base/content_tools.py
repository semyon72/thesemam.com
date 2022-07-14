# Project: blog_7myon_com
# Package: 
# Filename: content_tools.py
# Generated: 2021 Jun 09 at 22:00 
# Description of <content_tools>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
from urllib import parse

from django.utils.translation import gettext as _

from sm_flexdata.html.utils import make_tag

button_definitions = {
    'create': {
        'label': _('Create'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-plus-square']
    },
    'delete': {
        'label': _('Delete'),
        'btn_classes': 'btn btn-sm btn-outline-danger',
        'icon_classes': ['bi bi-x-square']
    },
    'edit': {
        'label': _('Edit'),
        'btn_classes': 'btn btn-sm btn-outline-warning',
        'icon_classes': ['bi bi-pencil-square']
    },
    'update': {
        'label': _('Update'),
        'btn_classes': 'btn btn-sm btn-outline-warning',
        'icon_classes': ['bi bi-save']
    },
    'detail': {
        'label': _('Detail'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-card-text']
    },
    'filter': {
        'label': _('Filter'),
        'btn_classes': 'btn btn-sm btn-outline-success',
        'icon_classes': ['bi bi-funnel']
    },
    'list': {
        'label': _('List'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-list']
    },
    'back_to_list': {
        'label': _('Back to list'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-backspace', 'bi bi-list']
    },
    'login': {
        'label': _('Login'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-box-arrow-in-right']
    },
    'logout': {
        'label': _('Logout'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-box-arrow-right']
    },
    'sign_up': {
        'label': _('Sign Up'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-person-plus']
    },
    'change_password': {
        'label': _('Change password'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-arrow-repeat']
    },
    'reset_password': {
        'label': _('Reset password'),
        'btn_classes': 'btn btn-sm btn-outline-primary',
        'icon_classes': ['bi bi-x-octagon']
    },
}


def create_button(type, *args, url=None, **kwargs):
    """
    Main purpose is using in template as tag. You must heed be careful with kwargs and args.
    If args is simple types like str, int .... then they  will be automatically escaped
    for safe view otherwise you need to do it manually. kwargs  values lay on your responsibility.
    Also it is touching the url. If url contains space ' ', that almost impossible,
    then it will be escaped by urllib.parse.quote(...) otherwise it will used as is.
    Thus, You must have responsibilities for data that you pass inside as args,
    url and kwargs parameters.
    :param type: str that identifying default set of bootstrap parameters for button or <a ...> as button
    :param args: set of HTML elements that will be included instead default icons (elements)
    inside <button></button> tag
    :param url: If this parameter exists then returned element will be <a...> tag otherwise <button..>
    :param kwargs: HTML attributes for <a...> or <button...> tag. It will redefine default attributes
    :return: NamedHTMLElement that compatible with safe string that can be used in Template
    """

    if type not in button_definitions:
        raise ValueError('Button\'s type not in list %s' % button_definitions.keys())

    bdefs = button_definitions[type]
    label = bdefs['label']
    if args:
        icons = args
    else:
        icons = [make_tag('i', class_attr=icon_clss) for icon_clss in bdefs['icon_classes']]
    attrs = {'class': bdefs['btn_classes']}
    tag = 'button'
    if url:
        if ' ' in url:  # simple test is url unquoted. But by default we suppose that url is safe
            url = parse.quote(url)
        attrs['href'] = url
        tag = 'a'
    else:
        attrs['type'] = 'submit'
        attrs['value'] = label

    if kwargs:
        attrs.update(kwargs)

    attrs = {k:v for k, v in attrs.items() if v}  # cleaning empty
    return make_tag(tag, *icons, label, **attrs)