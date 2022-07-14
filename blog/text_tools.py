# Project: blog_7myon_com
# Package: 
# Filename: text_tools.py
# Generated: 2021 May 19 at 21:44 
# Description of <text_tools>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import re

from django.utils.html import MLStripper
from django.utils.safestring import mark_safe


def strip_tags(s, convert_charrefs=False):
    if not isinstance(s, (str, bytes, bytearray)):
        raise TypeError('Parameter should be str type.')
    if not s:
        return ''
    else:
        p = MLStripper()
        p.convert_charrefs = bool(convert_charrefs)
        p.feed(s)
        return p.get_data()


def create_patterns_for_re_sub(texts, text_prefix, text_suffix):
    """
    Returns 2-tuple
       0 - '^(.*)(text1)(.*)(text2)(.*)$' as list
       1 - '\g<1>text_prefix\g<2>text_suffix\g<3>text_prefix\g<4>text_suffix\g<5>' as list

    :param texts: list of texts that should be wrapped into text_prefix and text_suffix parts
    :param text_prefix:
    :param text_suffix:
    :return:
    """
    p_list = ['('+re.escape(str(t).strip())+')' for t in texts if str(t).strip()]
    back_ref = r'\g<%s>'
    pattern, replace = [], []
    for i in range(len(p_list) * 2 + 1):
        p = r'(.*)'
        bp_items = [back_ref % str(i + 1)]
        if i % 2 > 0:
            p = p_list[i // 2]
            bp_items.insert(0, text_prefix)
            bp_items.append(text_suffix)
        pattern.append(p)
        replace.append(''.join(bp_items))

    if pattern:
        pattern.append(r'$')
        pattern.insert(0, r'^')

    return pattern, replace


def highlight_found_text(text: str,
                         search_text,
                         found_text_prefix='<span class="found-text">',
                         found_text_suffix='</span'
                         ):
    if not hasattr(search_text, '__iter__') or isinstance(search_text, str):
        search_text = str(search_text).split()

    result = text
    if search_text:
        pattern, replace = create_patterns_for_re_sub(
            search_text, found_text_prefix, found_text_suffix
        )
        result = mark_safe(
            re.sub(''.join(pattern), ''.join(replace), text, flags=re.I | re.S)
        )

    return result
