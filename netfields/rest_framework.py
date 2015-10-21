from __future__ import absolute_import

from functools import partial

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from netfields import fields


def _validate_netaddr(netfields_type, value):
    """Convert Django validation errors to DRF validation errors.
    """
    try:
        field = netfields_type(value)
        field.to_python(value)
    except DjangoValidationError:
        raise serializers.ValidationError("Invalid {} address.".format(field.short_name))


class NetfieldsField(object):
    def __init__(self, *args, **kwargs):
        validators = kwargs.get('validators', [])
        validators.append(partial(_validate_netaddr, self.netfields_type))
        kwargs['validators'] = validators
        super(NetfieldsField, self).__init__(*args, **kwargs)


class InetAddressField(NetfieldsField, serializers.CharField):
    netfields_type = fields.InetAddressField


class CidrAddressField(NetfieldsField, serializers.CharField):
    netfields_type = fields.CidrAddressField


class MACAddressField(NetfieldsField, serializers.CharField):
    netfields_type = fields.MACAddressField
