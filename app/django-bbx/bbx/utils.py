# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.utils.text import capfirst
from django.core.files.storage import FileSystemStorage
from django.contrib.humanize.templatetags.humanize import apnumber

from bbx.settings import THUMBNAILS_ROOT, THUMBNAILS_URL

import os
import errno
import math
import logging

logger = logging.getLogger(__name__)


def check_if_path_exists_or_create(path):
    """Function to check or create a given path.

    Atributos:
        path: check if "path" exist or create
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def convertToGB(size, unit):
    allowed_units = ('MB', 'GB', 'TB')
    if unit not in allowed_units:
        return False
    
    if unit == 'MB':
        size = float(size)/1000
    if unit == 'GB':
        size = float(size)
    if unit == 'TB':
        size = float(size) * 1000
    return str(round(size, 2)) + 'GB'

def dumpclean(obj):
    """Function to print all field/dictionary of a given object.

    Atributos:
        obj: print all field/dictionary of "obj"
    """
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print repr(k)
                dumpclean(v)
            else:
		print k.encode('ascii', 'ignore') + " : " + v.encode('ascii', 'ignore')
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v.encode('ascii', 'ignore')
    else:
        print obj.encode('ascii', 'ignore')


class MultiSelectFormField(forms.MultipleChoiceField):
    """Multi Select Field, originally taken from:
        http://djangosnippets.org/snippets/1200/
    """
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 5)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError(
                'You must select a maximum of %s choice%s.'
                % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value


class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        # choicedict = dict(field.choices)
        # TODO: Return value or what?
        raise RuntimeError("Please implement: " + str(value))

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text,
                    'choices': self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def validate(self, value, model_instance):
        # Needed couse it's a custom field .. see more:
        # https://groups.google.com/forum/#!topic/django-users/J0NXIUo7TdY
        # Should do something?
        return

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        return value.split(",")

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(
                self.choices
            ): ",".join(
                [choicedict.get(value, value) for
                 value in getattr(self, fieldname)]
            )
            setattr(cls, 'get_%s_display' % self.name, func)


class ThumbnailStorage(FileSystemStorage):
    def __init__(self, **kwargs):
        super(ThumbnailStorage, self).__init__(
            location=THUMBNAILS_ROOT, base_url=THUMBNAILS_URL)
