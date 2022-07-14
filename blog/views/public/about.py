# Project: blog_7myon_com
# Package: 
# Filename: about.py
# Generated: 2021 May 22 at 21:40 
# Description of <about>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'blog/public/about.html'
