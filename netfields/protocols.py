from ipaddress import ip_interface, IPv4Interface, IPv6Interface, ip_network, IPv4Network, IPv6Network, ip_address, \
    IPv4Address, IPv6Address

BOTH_PROTOCOLS = 'both'
IPV4_PROTOCOL = 'IPv4'
IPV6_PROTOCOL = 'IPv6'
PROTOCOLS = [BOTH_PROTOCOLS, IPV4_PROTOCOL, IPV6_PROTOCOL]


def get_interface_type_by_protocol(protocol):
    if protocol == BOTH_PROTOCOLS:
        return ip_interface
    elif protocol == IPV4_PROTOCOL:
        return IPv4Interface
    elif protocol == IPV6_PROTOCOL:
        return IPv6Interface

    raise ValueError('%s is not a supported protocol' % protocol)


def get_network_type_by_protocol(protocol):
    if protocol == BOTH_PROTOCOLS:
        return ip_network
    elif protocol == IPV4_PROTOCOL:
        return IPv4Network
    elif protocol == IPV6_PROTOCOL:
        return IPv6Network

    raise ValueError('%s is not a supported protocol' % protocol)


def get_address_type_by_protocol(protocol):
    if protocol == BOTH_PROTOCOLS:
        return ip_address
    elif protocol == IPV4_PROTOCOL:
        return IPv4Address
    elif protocol == IPV6_PROTOCOL:
        return IPv6Address

    raise ValueError('%s is not a supported protocol' % protocol)
