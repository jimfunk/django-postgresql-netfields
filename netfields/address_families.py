from ipaddress import ip_interface, IPv4Interface, IPv6Interface, ip_network, IPv4Network, IPv6Network, ip_address, \
    IPv4Address, IPv6Address

UNSPECIFIED = None
IPV4 = 4
IPV6 = 6
ADDRESS_FAMILIES = [UNSPECIFIED, IPV4, IPV6]

ADDRESS_FAMILY_TO_INTERFACE_TYPE = {
    UNSPECIFIED: ip_interface,
    IPV4: IPv4Interface,
    IPV6: IPv6Interface,
}

ADDRESS_FAMILY_TO_NETWORK_TYPE = {
    UNSPECIFIED: ip_network,
    IPV4: IPv4Network,
    IPV6: IPv6Network,
}

ADDRESS_FAMILY_TO_ADDRESS_TYPE = {
    UNSPECIFIED: ip_address,
    IPV4: IPv4Address,
    IPV6: IPv6Address,
}


def get_interface_type_by_address_family(address_family):
    if address_family in ADDRESS_FAMILY_TO_INTERFACE_TYPE:
        return ADDRESS_FAMILY_TO_INTERFACE_TYPE[address_family]

    raise ValueError('%s is not a supported address family' % address_family)


def get_network_type_by_address_family(address_family):
    if address_family in ADDRESS_FAMILY_TO_NETWORK_TYPE:
        return ADDRESS_FAMILY_TO_NETWORK_TYPE[address_family]

    raise ValueError('%s is not a supported address family' % address_family)


def get_address_type_by_address_family(address_family):
    if address_family in ADDRESS_FAMILY_TO_ADDRESS_TYPE:
        return ADDRESS_FAMILY_TO_ADDRESS_TYPE[address_family]

    raise ValueError('%s is not a supported address family' % address_family)
