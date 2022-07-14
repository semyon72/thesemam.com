# Project: blog_7myon_com
# Package: 
# Filename: unused.py
# Generated: 2021 Jun 10 at 21:59 
# Description of <unused>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from blog.forms.base.entry import EntryTextModelForm, EntryModelForm


class EntryWithTextModelForm(EntryModelForm):
    """
    Form that allow edit and save at once two tables that related OneToOne relation
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        args_copy = [*args]
        kwargs_copy = kwargs.copy()
        if len(args_copy) > 8:
            del args_copy[8]  # instance
        if hasattr(self.instance, 'entrytext'):
            kwargs_copy['instance'] = self.instance.entrytext
        else:
            kwargs_copy.pop('instance', None)
        kwargs_copy['prefix'] = EntryTextModelForm.__name__.lower()

        self.entrytext_form = EntryTextModelForm(*args_copy, **kwargs_copy)
        for etfield_name, etfield in self.entrytext_form.fields.items():
            self.fields[self.add_prefix(self.entrytext_form.add_prefix(etfield_name))] = etfield

        self.__getitem__handlers = self._get__getitem__handlers()

    def _get__getitem__handlers(self):
        # caller like super().__getitem__ or self.entrytext_form.__getitem__ and original fieldname
        result = {self.add_prefix(field_name): (super(self.__class__, self).__getitem__, self.add_prefix(field_name)) for field_name in self.fields}
        for field_name in self.entrytext_form.fields:
            prefixed_name = self.add_prefix(self.entrytext_form.add_prefix(field_name))
            result[prefixed_name] = (self.entrytext_form.__getitem__, field_name)
        return result

    def __getitem__(self, name):
        func__getitem__, real_fieldname = self.__getitem__handlers[name]
        return func__getitem__(real_fieldname)

    def save(self, commit=True):
        self.entrytext_form.instance.entry = super().save(commit=commit)
        self.entrytext_form.save(commit=commit)
        return self.instance

