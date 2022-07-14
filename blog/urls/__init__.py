# Project: blog_7myon_com
# Package: 
# Filename: __init__.py
# Generated: 2021 Jun 09 at 16:38 
# Description of <__init__.py>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.urls import path, include

from . import settings, public, staff, auth

app_name = settings.APP_NAME

urlpatterns = [
    path('', include((public.urlpatterns, settings.PUBLIC_NAME))),
    path('accounts/%s/' % settings.AUTH_NAME, include((auth.urlpatterns, settings.AUTH_NAME))),
    path('accounts/%s/' % settings.STAFF_NAME, include((staff.urlpatterns, settings.STAFF_NAME)))
]
