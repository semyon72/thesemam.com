# Project: blog_7myon_com
# Package: 
# Filename: __init__.py
# Generated: 2021 Jan 26 at 17:28 
# Description of <__init__.py>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

from dataclasses import Field


def remove_specific_validators(field: Field):
    # Field.default_validators is default set of validators that specific for certain Field
    # For example: EmailField has as default_validators the EmailValidator
    default_validators_types = tuple(type(validator) for validator in field.default_validators)
    if len(default_validators_types) > 0:
        idx_for_remove = [i for i, v in enumerate(field.validators) if isinstance(v, default_validators_types)]
        for idx in idx_for_remove:
            del field.validators[idx]

