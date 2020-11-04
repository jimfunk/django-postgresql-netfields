from __future__ import absolute_import

from ipaddress import ip_interface, ip_network, ip_address
from netaddr import EUI
from netaddr.core import AddrFormatError
from rest_framework import serializers

from netfields.compat import text_type
from netfields.mac import mac_unix_common
from netfields import fields


class InetAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid IP address.'
    }

    def __init__(self, store_prefix=True, *args, **kwargs):
        self.store_prefix = store_prefix
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
                return ip_interface(data)
            else:
                return ip_address(data)
        except ValueError:
            self.fail('invalid')


class CidrAddressField(serializers.Field):
    default_error_messages = {
        'invalid': 'Invalid CIDR address.',
        'network': 'Must be a network address.',
    }

    def to_representation(self, value):
        if value is None:
            return value
        return text_type(value)

    def to_internal_value(self, data):
        if data is None:
            return data
        try:
            return ip_network(data)
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
        except (AddrFormatError, TypeError):
            self.fail('invalid')


class NetModelSerializer(serializers.ModelSerializer):
    pass


NetModelSerializer.serializer_field_mapping[fields.InetAddressField] = InetAddressField
NetModelSerializer.serializer_field_mapping[fields.CidrAddressField] = CidrAddressField
NetModelSerializer.serializer_field_mapping[fields.MACAddressField] = MACAddressField
