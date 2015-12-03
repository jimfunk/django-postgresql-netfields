from __future__ import absolute_import

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from netfields import fields


class NetfieldsField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        super(NetfieldsField, self).__init__(*args, **kwargs)
        self.validators.append(self._validate_netaddr)

    def _validate_netaddr(self, value):
        """Convert Django validation errors to DRF validation errors.
        """
        try:
            self.netfields_type(value).to_python(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid {} address.".format(self.address_type))


class InetAddressField(NetfieldsField):
    netfields_type = fields.InetAddressField
    address_type = "IP"


class CidrAddressField(NetfieldsField):
    netfields_type = fields.CidrAddressField
    address_type = "CIDR"


class MACAddressField(NetfieldsField):
    netfields_type = fields.MACAddressField
    address_type = "MAC"
