# Project: blog_7myon_com
# Package: 
# Filename: contact.py
# Generated: 2021 May 24 at 03:26 
# Description of <contact>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>
import smtplib

import django.forms as forms
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

from sm_flexdata.html.form_elements import FlexForm
from ...models import Author
from ...urls import settings


class ContactForm(FlexForm, forms.Form):

    author = forms.ModelChoiceField(
        Author.objects.all(),
        label=_('Author'),
        help_text=_('select an author'),
    )

    name = forms.CharField(
        max_length=128,
        label=_('Name'),
        help_text=_('your name')
    )

    email = forms.EmailField(
        max_length=128,
        label=_('Email'),
        help_text=_('your email address')
    )

    headline = forms.CharField(
        max_length=128,
        label=_('Headline'),
        help_text=_('short description of message'),
        required=False
    )

    message = forms.CharField(
        max_length=512,
        label=_('Message'),
        help_text=_('message'),
        widget=forms.Textarea
    )


class ContactView(FormView):
    form_class = ContactForm
    success_url = reverse_lazy(settings.get_view_name('index_contact_success'))
    success_message_template_name = 'blog/public/contact/contact_success_message.html'
    template_name = 'blog/public/contact/contact_form.html'
    email_template_name = 'blog/public/contact/contact_form_email.txt'
    html_email_template_name = 'blog/public/contact/contact_form_email.html'
    author_url_kwarg = 'author'

    def send_email(self, form):
        context = {'form': form}
        email_message = EmailMultiAlternatives(
            subject=''.join('Some subject'.splitlines()),
            body=render_to_string(self.email_template_name, context, self.request),
            from_email=form.cleaned_data['email'],
            to=(form.cleaned_data['author'].email,),
            reply_to=(form.cleaned_data['email'], )
        )
        html_email = render_to_string(self.html_email_template_name, context, self.request)
        email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def set_success_message(self, form):
        context = {'form': form}
        message = render_to_string(self.success_message_template_name, context, self.request)
        messages.success(self.request, message)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('GET', ) and self.author_url_kwarg in self.request.GET:
            author_id = self.request.GET.get(self.author_url_kwarg)
            if author_id is not None:
                authors = Author.objects.filter(pk=int(author_id))
                if len(authors) == 1:
                    kwargs['initial'][self.author_url_kwarg] = authors[0].pk
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if form.is_valid():
            try:
                self.send_email(form)
            except smtplib.SMTPException:
                form.add_error(None, _('Something went wrong. Message was not sent.'))
            else:
                self.set_success_message(form)

        return form


class ContactSuccessView(TemplateView):
    template_name = 'blog/public/contact/contact_success.html'
