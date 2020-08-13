from ipaddress import _IPAddressBase, _BaseNetwork, AddressValueError
from netaddr import EUI, AddrFormatError

from django import forms
from django.core.exceptions import ValidationError

from netfields.compat import text_type
from netfields.mac import mac_unix_common
from netfields.protocols import BOTH_PROTOCOLS, get_interface_type_by_protocol, get_network_type_by_protocol


class InetAddressFormField(forms.Field):
    widget = forms.TextInput
    default_error_messages = {
        'invalid': u'Enter a valid IP address.',
        'invalid_protocol': u'Enter a valid %(protocol)s address.',
    }

    def __init__(self, protocol=BOTH_PROTOCOLS, **kwargs):
        self.protocol = protocol
        super(InetAddressFormField, self).__init__(**kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddressBase):
            return value

        if isinstance(value, text_type):
            value = value.strip()

        try:
            return get_interface_type_by_protocol(self.protocol)(value)
        except (ValueError, AddressValueError) as e:
            if self.protocol != BOTH_PROTOCOLS:
                raise ValidationError(self.error_messages['invalid_protocol'], params={'protocol': self.protocol})
            raise ValidationError(self.error_messages['invalid'])


class CidrAddressFormField(forms.Field):
    widget = forms.TextInput
    default_error_messages = {
        'invalid': u'Enter a valid CIDR address.',
        'invalid_protocol': u'Enter a valid %(protocol)s CIDR address.',
        'network': u'Must be a network address.',
    }

    def __init__(self, protocol=BOTH_PROTOCOLS, *args, **kwargs):
        self.protocol = protocol
        super(CidrAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _BaseNetwork):
            network = value

        if isinstance(value, text_type):
            value = value.strip()

        try:
            network = get_network_type_by_protocol(self.protocol)(value)
        except (ValueError, AddressValueError) as e:
            if 'has host bits' in e.args[0]:
                raise ValidationError(self.error_messages['network'])
            if self.protocol != BOTH_PROTOCOLS:
                raise ValidationError(self.error_messages['invalid_protocol'], params={'protocol': self.protocol})
            raise ValidationError(self.error_messages['invalid'])

        return network


class MACAddressFormField(forms.Field):
    default_error_messages = {
        'invalid': u'Enter a valid MAC address.',
    }

    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, EUI):
            return value

        if isinstance(value, text_type):
            value = value.strip()

        try:
            return EUI(value, dialect=mac_unix_common)
        except (AddrFormatError, TypeError):
            raise ValidationError(self.error_messages['invalid'])

    def widget_attrs(self, widget):
        attrs = super(MACAddressFormField, self).widget_attrs(widget)
        attrs.update({'maxlength': '17'})
        return attrs
