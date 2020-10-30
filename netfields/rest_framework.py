from __future__ import absolute_import

from ipaddress import AddressValueError

from netaddr import EUI
from netaddr.core import AddrFormatError
from rest_framework import serializers

from netfields.compat import text_type
from netfields.mac import mac_unix_common
from netfields.address_families import BOTH_FAMILIES, get_interface_type_by_address_family, \
    get_address_type_by_address_family, get_network_type_by_address_family


class InetAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid IP address.',
        'invalid_address_family': 'Invalid {address_family} address.',
    }

    def __init__(self, store_prefix=True, address_family=BOTH_FAMILIES, *args, **kwargs):
        self.store_prefix = store_prefix
        self.address_family = address_family
        super(InetAddressField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if value is None:
            return value
        return text_type(value)

    def to_internal_value(self, data):
        if data is None:
            return data
        try:
            if self.store_prefix:
                return get_interface_type_by_address_family(self.address_family)(data)
            else:
                return get_address_type_by_address_family(self.address_family)(data)
        except (ValueError, AddressValueError):
            if self.address_family != BOTH_FAMILIES:
                self.fail('invalid_address_family', address_family=self.address_family)
            self.fail('invalid')


class CidrAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid CIDR address.',
        'invalid_address_family': 'Invalid {address_family} CIDR address.',
        'network': 'Must be a network address.',
    }

    def __init__(self, address_family=BOTH_FAMILIES, **kwargs):
        self.address_family = address_family
        super(CidrAddressField, self).__init__(**kwargs)

    def to_representation(self, value):
        if value is None:
            return value
        return text_type(value)

    def to_internal_value(self, data):
        if data is None:
            return data
        try:
            return get_network_type_by_address_family(self.address_family)(data)
        except (ValueError, AddressValueError) as e:
            if 'has host bits' in e.args[0]:
                self.fail('network')
            if self.address_family != BOTH_FAMILIES:
                self.fail('invalid_address_family', address_family=self.address_family)
            self.fail('invalid')


class MACAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid MAC address.'
    }

    def to_representation(self, value):
        if value is None:
            return value
        return text_type(value)

    def to_internal_value(self, data):
        if data is None:
            return data
        try:
            return EUI(data, dialect=mac_unix_common)
        except AddrFormatError:
            self.fail('invalid')
