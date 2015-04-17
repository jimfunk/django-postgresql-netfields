from django.apps import AppConfig

from django.db.models.lookups import default_lookups
from netfields.fields import CidrAddressField, InetAddressField
from netfields.lookups import NetContained, NetContains, NetContainedOrEqual, NetContainsOrEquals, InvalidLookup
from netfields.lookups import EndsWith, IEndsWith, StartsWith, IStartsWith, Regex, IRegex


class NetfieldsConfig(AppConfig):
    name = 'netfields'

    for lookup in default_lookups.keys():
        if lookup not in ['contains', 'startswith', 'endswith', 'icontains', 'istartswith', 'iendswith', 'isnull', 'in',
                          'exact', 'iexact', 'regex', 'iregex', 'lt', 'lte', 'gt', 'gte', 'equals', 'iequals', 'range']:
            invalid_lookup = InvalidLookup
            invalid_lookup.lookup_name = lookup
            CidrAddressField.register_lookup(invalid_lookup)
            InetAddressField.register_lookup(invalid_lookup)

    CidrAddressField.register_lookup(EndsWith)
    CidrAddressField.register_lookup(IEndsWith)
    CidrAddressField.register_lookup(StartsWith)
    CidrAddressField.register_lookup(IStartsWith)
    CidrAddressField.register_lookup(Regex)
    CidrAddressField.register_lookup(IRegex)
    CidrAddressField.register_lookup(NetContained)
    CidrAddressField.register_lookup(NetContains)
    CidrAddressField.register_lookup(NetContainedOrEqual)
    CidrAddressField.register_lookup(NetContainsOrEquals)

    InetAddressField.register_lookup(EndsWith)
    InetAddressField.register_lookup(IEndsWith)
    InetAddressField.register_lookup(StartsWith)
    InetAddressField.register_lookup(IStartsWith)
    InetAddressField.register_lookup(Regex)
    InetAddressField.register_lookup(IRegex)
    InetAddressField.register_lookup(NetContained)
    InetAddressField.register_lookup(NetContains)
    InetAddressField.register_lookup(NetContainedOrEqual)
    InetAddressField.register_lookup(NetContainsOrEquals)

