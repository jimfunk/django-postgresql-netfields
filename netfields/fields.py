from ipaddress import ip_interface, ip_network

from django import VERSION
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.six import with_metaclass, text_type
from netaddr import EUI
from netaddr.core import AddrFormatError

from netfields.forms import InetAddressFormField, CidrAddressFormField, MACAddressFormField
from netfields.mac import mac_unix_common
from netfields.managers import NET_OPERATORS, NET_TEXT_OPERATORS


class _NetAddressField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        super(_NetAddressField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return value

        if isinstance(value, bytes):
            value = value.decode('ascii')

        try:
            return self.python_type()(value)
        except (AddrFormatError, ValueError) as e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if (lookup_type in NET_OPERATORS and
                    NET_OPERATORS[lookup_type] not in NET_TEXT_OPERATORS):
            if (lookup_type.startswith('net_contained') or
                    lookup_type.endswith('prefixlen')) and value is not None:
                # Argument will be CIDR
                return str(value)
            return self.get_prep_value(value)

        return super(_NetAddressField, self).get_prep_lookup(
            lookup_type, value)

    def get_prep_value(self, value):
        if not value:
            return None

        return str(self.to_python(value))

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        if not value:
            return []

        if (lookup_type in NET_OPERATORS and
                    NET_OPERATORS[lookup_type] not in NET_TEXT_OPERATORS):
            return [value] if prepared else [self.get_prep_value(value)]

        return super(_NetAddressField, self).get_db_prep_lookup(
            lookup_type, value, connection=connection, prepared=prepared)

    def formfield(self, **kwargs):
        defaults = {'form_class': self.form_class()}
        defaults.update(kwargs)
        return super(_NetAddressField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(_NetAddressField, self).deconstruct()
        if self.max_length is not None:
            kwargs['max_length'] = self.max_length
        return name, path, args, kwargs


if VERSION < (1, 8):
    # SubFieldBase has been deprecated in Django 1.8
    # see https://docs.djangoproject.com/en/1.9/releases/1.8/#subfieldbase
    _field_base_class = with_metaclass(models.SubfieldBase, _NetAddressField)
    _mac_field_base_class = with_metaclass(models.SubfieldBase, models.Field)
else:
    _field_base_class = _NetAddressField
    _mac_field_base_class = models.Field


class InetAddressField(_field_base_class):
    description = "PostgreSQL INET field"
    max_length = 39

    def __init__(self, *args, **kwargs):
        self.store_prefix_length = kwargs.pop('store_prefix_length', True)
        super(InetAddressField, self).__init__(*args, **kwargs)

    if VERSION >= (1, 8):
        def from_db_value(self, value, expression, connection, context):
            return self.to_python(value)

    def db_type(self, connection):
        return 'inet'

    def python_type(self):
        return ip_interface

    def to_python(self, value):
        value = super(InetAddressField, self).to_python(value)
        if not value:
            return

        if self.store_prefix_length:
            return value
        else:
            return value.ip

    def form_class(self):
        return InetAddressFormField


class CidrAddressField(_field_base_class):
    description = "PostgreSQL CIDR field"
    max_length = 43

    if VERSION >= (1, 8):
        def from_db_value(self, value, expression, connection, context):
            return self.to_python(value)

    def db_type(self, connection):
        return 'cidr'

    def python_type(self):
        return ip_network

    def form_class(self):
        return CidrAddressFormField


class MACAddressField(_mac_field_base_class):
    description = "PostgreSQL MACADDR field"
    max_length = 17

    def db_type(self, connection):
        return 'macaddr'

    if VERSION >= (1, 8):
        def from_db_value(self, value, expression, connection, context):
            return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value

        try:
            return EUI(value, dialect=mac_unix_common)
        except AddrFormatError as e:
            raise ValidationError(e)

    def get_prep_value(self, value):
        if not value:
            return None

        return text_type(self.to_python(value))

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)
