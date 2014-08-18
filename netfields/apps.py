from django.apps import AppConfig

from netfields.fields import CidrAddressField, InetAddressField
from netfields.lookups import NetContained, NetContains, NetContainedOrEqual, NetContainsOrEquals


class NetfieldsConfig(AppConfig):
    name = 'netfields'

    CidrAddressField.register_lookup(NetContained)
    CidrAddressField.register_lookup(NetContains)
    CidrAddressField.register_lookup(NetContainedOrEqual)
    CidrAddressField.register_lookup(NetContainsOrEquals)

    InetAddressField.register_lookup(NetContained)
    InetAddressField.register_lookup(NetContains)
    InetAddressField.register_lookup(NetContainedOrEqual)
    InetAddressField.register_lookup(NetContainsOrEquals)

