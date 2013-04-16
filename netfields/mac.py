import netaddr


class mac_unix_common(netaddr.mac_eui48):
    """Common form of UNIX MAC address dialect class"""
    word_sep  = ':'
    word_fmt  = '%.2x'
