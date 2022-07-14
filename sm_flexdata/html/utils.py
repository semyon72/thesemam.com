# Project: blog_7myon_com
# Package: 
# Filename: utils.py
# Generated: 2021 Jun 10 at 14:09 
# Description of <utils>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from .elements import NamedHTMLElement


def merge_classes(str1, str2):
    cls2 = filter(None, str2.split())  # clean empty
    result = [v for v in str1.split() if v and v not in cls2]  # clean empty and not exists in str2
    result.extend(cls2)
    return ' '.join(result)


def make_tag(tag, *data, element_name='', class_attr='', **attrs):
    """
    Need to use class_attr parameter name instead class because class is reserved word
    or 'class' key inside attrs dict that unpacking in make_tag.
    String of class_attr parameter will be used as 'class' attribute of HTML tag after
    joining with attrs['class'].

    :param tag: str HTML tag - a, div, span etc.
    :param data: Any Things that will inside this HTML tag
    :param class_attr: str - representation string for 'class' HTML tag attribute
    :param element_name: internal NamedHTMLElement name not attribute 'name' of tag
    if need to set 'name' attribute for tag then it must be passed as named parameter
    :param attrs: dict of HTML tag attributes
    :return: NamedHTMLElement
    """
    attrs['class'] = merge_classes(class_attr, attrs.pop('class', ''))
    return NamedHTMLElement(data, tag, attrs, element_name)
