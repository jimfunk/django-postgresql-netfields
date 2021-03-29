from ipaddress import ip_interface, IPv4Interface, IPv6Interface, ip_network, IPv4Network, IPv6Network, ip_address, \
    IPv4Address, IPv6Address

BOTH_FAMILIES = None
IPV4_FAMILY = 4
IPV6_FAMILY = 6
ADDRESS_FAMILIES = [BOTH_FAMILIES, IPV4_FAMILY, IPV6_FAMILY]


def get_interface_type_by_address_family(address_family):
    address_family_to_interface_type = {
        BOTH_FAMILIES: ip_interface,
        IPV4_FAMILY: IPv4Interface,
        IPV6_FAMILY: IPv6Interface,
    }

    if address_family in address_family_to_interface_type:
        return address_family_to_interface_type[address_family]

    raise ValueError('%s is not a supported address family' % address_family)


def get_network_type_by_address_family(address_family):
    address_family_to_network_type = {
        BOTH_FAMILIES: ip_network,
        IPV4_FAMILY: IPv4Network,
        IPV6_FAMILY: IPv6Network,
    }

    if address_family in address_family_to_network_type:
        return address_family_to_network_type[address_family]

    raise ValueError('%s is not a supported address family' % address_family)


def get_address_type_by_address_family(address_family):
    address_family_to_address_type = {
        BOTH_FAMILIES: ip_address,
        IPV4_FAMILY: IPv4Address,
        IPV6_FAMILY: IPv6Address,
    }

    if address_family in address_family_to_address_type:
        return address_family_to_address_type[address_family]

    raise ValueError('%s is not a supported address family' % address_family)
