from __future__ import absolute_import

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from netfields import fields


class NetfieldsField(object):
    def __init__(self, *args, **kwargs):
        validators = kwargs.get('validators', [])
        validators.append(self._validate_netaddr)
        kwargs['validators'] = validators
        super(NetfieldsField, self).__init__(*args, **kwargs)

    def _validate_netaddr(self, value):
        """Convert Django validation errors to DRF validation errors.
        """
        try:
            self.netfields_type(value).to_python(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid {} address.".format(self.short_name))


class InetAddressField(NetfieldsField, serializers.CharField):
    netfields_type = fields.InetAddressField
    short_name = "IP"


class CidrAddressField(NetfieldsField, serializers.CharField):
    netfields_type = fields.CidrAddressField
    short_name = "CIDR"


class MACAddressField(NetfieldsField, serializers.CharField):
    netfields_type = fields.MACAddressField
    short_name = "MAC"
