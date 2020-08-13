from ipaddress import ip_interface, IPv4Interface, IPv6Interface, ip_network, IPv4Network, IPv6Network, ip_address, \
    IPv4Address, IPv6Address

BOTH_PROTOCOLS = 'both'
IPV4_PROTOCOL = 'IPv4'
IPV6_PROTOCOL = 'IPv6'
PROTOCOLS = [BOTH_PROTOCOLS, IPV4_PROTOCOL, IPV6_PROTOCOL]


def get_interface_type_by_protocol(protocol):
    protocol_to_interface_type = {
        BOTH_PROTOCOLS: ip_interface,
        IPV4_PROTOCOL: IPv4Interface,
        IPV6_PROTOCOL: IPv6Interface,
    }

    if protocol in protocol_to_interface_type:
        return protocol_to_interface_type[protocol]

    raise ValueError('%s is not a supported protocol' % protocol)


def get_network_type_by_protocol(protocol):
    protocol_to_network_type = {
        BOTH_PROTOCOLS: ip_network,
        IPV4_PROTOCOL: IPv4Network,
        IPV6_PROTOCOL: IPv6Network,
    }

    if protocol in protocol_to_network_type:
        return protocol_to_network_type[protocol]

    raise ValueError('%s is not a supported protocol' % protocol)


def get_address_type_by_protocol(protocol):
    protocol_to_address_type = {
        BOTH_PROTOCOLS: ip_address,
        IPV4_PROTOCOL: IPv4Address,
        IPV6_PROTOCOL: IPv6Address,
    }

    if protocol in protocol_to_address_type:
        return protocol_to_address_type[protocol]

    raise ValueError('%s is not a supported protocol' % protocol)
