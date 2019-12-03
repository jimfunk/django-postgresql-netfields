from django.core.exceptions import ValidationError
from django.db import models

from ipaddress import ip_interface, ip_network
from netaddr import EUI
from netaddr.core import AddrFormatError

from netfields.compat import DatabaseWrapper, with_metaclass, text_type
from netfields.forms import InetAddressFormField, CidrAddressFormField, MACAddressFormField
from netfields.mac import mac_unix_common
from netfields.psycopg2_types import Inet, Macaddr


NET_OPERATORS = DatabaseWrapper.operators.copy()

for operator in ['contains', 'startswith', 'endswith']:
    NET_OPERATORS[operator] = 'ILIKE %s'
    NET_OPERATORS['i%s' % operator] = 'ILIKE %s'

NET_OPERATORS['iexact'] = NET_OPERATORS['exact']
NET_OPERATORS['regex'] = NET_OPERATORS['iregex']
NET_OPERATORS['net_contained'] = '<< %s'
NET_OPERATORS['net_contained_or_equal'] = '<<= %s'
NET_OPERATORS['net_contains'] = '>> %s'
NET_OPERATORS['net_contains_or_equals'] = '>>= %s'
NET_OPERATORS['net_overlaps'] = '&& %s'
NET_OPERATORS['max_prefixlen'] = '%s'
NET_OPERATORS['min_prefixlen'] = '%s'

NET_TEXT_OPERATORS = ['ILIKE %s', '~* %s']


class _NetAddressField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        super(_NetAddressField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, *args):
        if isinstance(value, list):
            # Aggregation detected, return a list of values. This is no longer
            # necessary in Django 2.1
            return [self.to_python(v) for v in value]
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value

        if isinstance(value, bytes):
            value = value.decode('ascii')

        try:
            return self.python_type()(value)
        except ValueError as e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if hasattr(value, '_prepare'):
            try:
                # Django 1.8
                return value._prepare()
            except TypeError:
                # Django 1.9
                return value._prepare(self)
        if (lookup_type in NET_OPERATORS and
                    NET_OPERATORS[lookup_type] not in NET_TEXT_OPERATORS):
            if (lookup_type.startswith('net_') or
                    lookup_type.endswith('prefixlen')) and value is not None:
                return str(value)
            return self.get_prep_value(value)

        return super(_NetAddressField, self).get_prep_lookup(
            lookup_type, value)

    def get_prep_value(self, value):
        if not value:
            return None

        return str(self.to_python(value))

    def get_db_prep_value(self, value, connection, prepared=False):
        # Django <= 1.8, ArrayField does not pass model to the base_field so we have to check for existance
        model = getattr(self, 'model', None)
        if model is None or model._meta.get_field(self.name).get_internal_type() == 'ArrayField':
            is_array_field = True
        else:
            is_array_field = False

        if prepared is False and is_array_field is False:
            return self.get_prep_value(value)

        return Inet(self.get_prep_value(value))

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        if not value:
            return []

        if (lookup_type in NET_OPERATORS and
                    NET_OPERATORS[lookup_type] not in NET_TEXT_OPERATORS):
            if prepared:
                return [value]
            if (lookup_type.startswith('net_') or
                    lookup_type.endswith('prefixlen')) and value is not None:
                return str(value)
            return [self.get_prep_value(value)]

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


class InetAddressField(_NetAddressField):
    description = "PostgreSQL INET field"
    max_length = 39

    def __init__(self, *args, **kwargs):
        self.store_prefix_length = kwargs.pop('store_prefix_length', True)
        super(InetAddressField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'inet'

    def python_type(self):
        return ip_interface

    def to_python(self, value):
        value = super(InetAddressField, self).to_python(value)
        if value:
            if self.store_prefix_length:
                return value
            else:
                return value.ip
        return value

    def form_class(self):
        return InetAddressFormField


class CidrAddressField(_NetAddressField):
    description = "PostgreSQL CIDR field"
    max_length = 43
    python_type = ip_network

    def db_type(self, connection):
        return 'cidr'

    def python_type(self):
        return ip_network

    def form_class(self):
        return CidrAddressFormField


class MACAddressField(models.Field):
    description = "PostgreSQL MACADDR field"
    max_length = 17

    def db_type(self, connection):
        return 'macaddr'

    def from_db_value(self, value, expression, connection, *args):
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

    def get_db_prep_value(self, value, connection, prepared=False):
        # Django <= 1.8, ArrayField does not pass model to the base_field so we have to check for existance
        model = getattr(self, 'model', None)
        if model is None or model._meta.get_field(self.name).get_internal_type() == 'ArrayField':
            is_array_field = True
        else:
            is_array_field = False

        if prepared is False and is_array_field is False:
            return self.get_prep_value(value)

        return Macaddr(self.get_prep_value(value))

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)
