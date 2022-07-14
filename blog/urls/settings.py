# Project: blog_7myon_com
# Package: 
# Filename: urls_names.py
# Generated: 2021 Feb 13 at 12:12 
# Description of <urls_names>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

import posixpath

from django.urls import path, include
from django.contrib.auth.models import User

APP_NAME = 'blog'

AUTHOR_NAME = 'author'
STAFF_NAME = 'staff'
AUTH_NAME = 'auth'
PUBLIC_NAME = 'public'


def get_app_name(section=PUBLIC_NAME):
    return ':'.join([APP_NAME, section])


def get_view_name(view_name, section=PUBLIC_NAME):
    return ':'.join([get_app_name(section), view_name])


def get_section_for_user(user: User):
    if user.is_authenticated and not user.is_superuser:
        if user.is_staff:
            return STAFF_NAME
        else:
            return AUTHOR_NAME
    return PUBLIC_NAME


def get_app_name_for_user(user: User):
    return get_app_name(get_section_for_user(user))
