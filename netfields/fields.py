from netaddr import IPAddress, IPNetwork, EUI
from netaddr.core import AddrFormatError

from django import VERSION as DJANGO_VERSION
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.six import with_metaclass

from netfields.managers import NET_OPERATORS, NET_TEXT_OPERATORS
from netfields.forms import InetAddressFormField, CidrAddressFormField, MACAddressFormField
from netfields.mac import mac_unix_common


class _NetAddressField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        super(_NetAddressField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return value

        try:
            return self.python_type()(value)
        except AddrFormatError as e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if not value:
            return None
        if type(value) is list and len(value) == 1:
            value = value[0]

        if (lookup_type in NET_OPERATORS and
                NET_OPERATORS[lookup_type] not in NET_TEXT_OPERATORS):
            if lookup_type.startswith('net_contained') and value is not None:
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

    if DJANGO_VERSION[:2] >= (1, 7):
        def deconstruct(self):
            name, path, args, kwargs = super(_NetAddressField, self).deconstruct()
            if self.max_length is not None:
                kwargs['max_length'] = self.max_length
            return name, path, args, kwargs


class InetAddressField(with_metaclass(models.SubfieldBase, _NetAddressField)):
    description = "PostgreSQL INET field"
    max_length = 39

    def db_type(self, connection):
        return 'inet'

    def python_type(self):
        return IPAddress

    def form_class(self):
        return InetAddressFormField


class CidrAddressField(with_metaclass(models.SubfieldBase, _NetAddressField)):
    description = "PostgreSQL CIDR field"
    max_length = 43

    def db_type(self, connection):
        return 'cidr'

    def python_type(self):
        return IPNetwork

    def form_class(self):
        return CidrAddressFormField


class MACAddressField(models.Field):
    description = "PostgreSQL MACADDR field"

    def db_type(self, connection):
        return 'macaddr'

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

        return str(self.to_python(value))

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)

if DJANGO_VERSION[:2] < (1, 7):
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules([], [
            "^netfields\.fields\.InetAddressField",
            "^netfields\.fields\.CidrAddressField",
            "^netfields\.fields\.MACAddressField",
        ])
    except ImportError:
        pass
