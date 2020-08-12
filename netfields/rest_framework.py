from __future__ import absolute_import

from netaddr import EUI
from netaddr.core import AddrFormatError
from rest_framework import serializers

from netfields.compat import text_type
from netfields.mac import mac_unix_common
from netfields.protocols import BOTH_PROTOCOLS, get_interface_type_by_protocol, get_address_type_by_protocol, \
    get_network_type_by_protocol


class InetAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid IP address.'
    }

    def __init__(self, store_prefix=True, protocol=BOTH_PROTOCOLS, *args, **kwargs):
        self.store_prefix = store_prefix
        self.protocol = protocol
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
                return get_interface_type_by_protocol(self.protocol)(data)
            else:
                return get_address_type_by_protocol(self.protocol)(data)
        except ValueError:
            self.fail('invalid')


class CidrAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid CIDR address.',
        'network': 'Must be a network address.',
    }

    def __init__(self, protocol=BOTH_PROTOCOLS, *args, **kwargs):
        self.protocol = protocol
        super(CidrAddressField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if value is None:
            return value
        return text_type(value)

    def to_internal_value(self, data):
        if data is None:
            return data
        try:
            return get_network_type_by_protocol(self.protocol)(data)
        except ValueError as e:
            if 'has host bits' in e.args[0]:
                self.fail('network')
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
