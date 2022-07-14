import datetime

from django.db import models
from django.utils.text import Truncator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from . import model_action_urls
from .models_tools import get_full_model_name, IterableFieldsModelMixin

# Create your models here.

TEXTFIELD_TRUNCATION_LENGTH = 100
TEXTFIELD_TRUNCATION_STRING = '...'

# This structure was inspired by Django official documentation

UserModel = get_user_model()


class BaseBlogModel(model_action_urls.AbsoluteURLActionAwareModelMixin, IterableFieldsModelMixin, models.Model):

    class Meta:
        abstract = True

    @classmethod
    def get_model_name(cls):
        return get_full_model_name(cls)


class Registration(models.Model):

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    registration_email = type(getattr(UserModel, UserModel.get_email_field_name()).field)(
        editable=False,
        blank=False,
        null=False,
        verbose_name=_('Email used at registration stage')
    )
    requested = models.DateTimeField(
        editable=False,
        blank=False,
        null=False,
        default=datetime.datetime.today,
        verbose_name=_('Registration was requested')
    )
    confirmed = models.DateTimeField(
        editable=False,
        null=True,
        default=None,
        verbose_name=_('Registration was confirmed')
    )
    is_active = models.BooleanField(
        editable=False,
        blank=False,
        null=False,
        default=False,
        verbose_name=_('Registration is active')
    )

    def __str__(self):
        return self.user.name


class Blog(BaseBlogModel):

    fields_order = []

    name = models.CharField(
        max_length=64,
        verbose_name=_('Blog\'s name'),  # will used as label in form. In general it changes
                                         # the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    tagline = models.CharField(
        max_length=128,
        verbose_name=_('Tagline'),  # слоган will used as label in form. In general it changes the field name.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return self.name


class Author(BaseBlogModel):
    user = models.OneToOneField(
        UserModel,
        on_delete=models.SET_DEFAULT, null=True, blank=True, default=None,
        # # SELECT * FROM django_blog.auth_user u LEFT outer join django_blog.blog_author a on a.user_id = u.id
        # # WHERE u.is_superuser = False and a.user_id is null
        # limit_choices_to= models.Q(is_superuser=False, author__isnull=True) & models.Q(author__user_id__isnull=True)
    )
    name = models.CharField(
        max_length=128,
        verbose_name=_('Author\'s name'),  # will used as label in form. In general it changes the field name in
                                           # admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    email = models.EmailField(
        verbose_name=_('Email address'),  # will used as label in form. In general it changes the field name.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return self.name


class Entry(BaseBlogModel):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        verbose_name=_('Blog'),  # will used as label in form. In general it changes the field name.
        help_text='',  # will used as input's title attribute to bring helping information
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name=_('Author'),  # will used as label in form.
                                   # In general it changes the field name in admin interface.
        help_text='',  # will used as input's title attribute to bring helping information
    )
    coauthors = models.ManyToManyField(
        Author,
        blank=True,
        default=None,
        related_name='entries_as_coauthor_set',
        verbose_name=_('Co-author')
    )
    headline = models.CharField(
        max_length=256,
        verbose_name=_('Entry\'s headline'),  # will used as label in form.
                                              # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    create_date = models.DateField(
        editable=False,
        default=datetime.date.today,
        null=False,
        verbose_name=_('Creation'),  # will used as label in form.
                                     # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    pub_date = models.DateField(
        verbose_name=_('Published'),  # will used as label in form. In general it changes the field name.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    mod_date = models.DateField(
        default=datetime.date.today,
        verbose_name=_('Modified'),  # will used as label in form.
                                     # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    inactive = models.BooleanField(
        null=False,
        default=False,
        verbose_name=_('Inactive'),  # will used as label in form.
                                     # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return self.headline


class EntryText(BaseBlogModel):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, verbose_name=_('Entry'))
    body_text = models.TextField(
        verbose_name=_('Text of entry'),  # will used as label in form. In general it changes
                                          # the field name in admin interface.
        help_text=_('Entry\'s text')  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return Truncator(self.body_text).chars(TEXTFIELD_TRUNCATION_LENGTH, TEXTFIELD_TRUNCATION_STRING)


class EntryComment(BaseBlogModel):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    pub_date = models.DateField(
        verbose_name=_('Published'),  # will used as label in form.
                                      # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    mod_date = models.DateField(
        verbose_name=_('Modified'),  # will used as label in form.
                                     # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    comment = models.TextField(
        verbose_name=_('Comment'),  # will used as label in form.
                                    # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    inactive = models.BooleanField(
        null=False,
        default=False,
        verbose_name=_('Inactive'),  # will used as label in form.
                                     # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return Truncator(self.comment).chars(TEXTFIELD_TRUNCATION_LENGTH, TEXTFIELD_TRUNCATION_STRING)


class EntryStat(models.Model):
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE, parent_link=True)
    number_of_comments = models.IntegerField(
        verbose_name=_('Comments\' amount'),  # will used as label in form.
                                              # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    number_of_pingbacks = models.IntegerField(
        verbose_name=_('Pingbacks\' amount'),  # will used as label in form.
                                               # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )
    rating = models.IntegerField(
        verbose_name=_('Rating'),  # will used as label in form.
                                   # In general it changes the field name in admin interface.
        help_text=''  # will used as input's title attribute to bring helping information
    )

    def __str__(self):
        return 'pk:{3} comments:{0} pingbacks:{1} rating:{2}'.format(
            self.number_of_comments,
            self.number_of_pingbacks,
            self.rating,
            self.pk
        )
