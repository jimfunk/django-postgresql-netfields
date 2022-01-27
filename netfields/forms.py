from ipaddress import _IPAddressBase, _BaseNetwork, AddressValueError
from netaddr import EUI, AddrFormatError

from django import forms
from django.core.exceptions import ValidationError

from netfields.compat import text_type
from netfields.mac import mac_unix_common
from netfields.address_families import UNSPECIFIED, get_interface_type_by_address_family, \
    get_network_type_by_address_family, get_address_type_by_address_family


class InetAddressFormField(forms.Field):
    widget = forms.TextInput
    default_error_messages = {
        'invalid': u'Enter a valid IP address.',
        'invalid_address_family': u'Enter a valid %(address_family)s address.',
    }

    def __init__(self, address_family=UNSPECIFIED, **kwargs):
        self.address_family = address_family
        super(InetAddressFormField, self).__init__(**kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddressBase):
            return value

        if isinstance(value, text_type):
            value = value.strip()

        try:
            return get_interface_type_by_address_family(self.address_family)(value)
        except (ValueError, AddressValueError):
            if self.address_family != UNSPECIFIED:
                raise ValidationError(self.error_messages['invalid_address_family'],
                                      params={'address_family': 'IPv{}'.format(self.address_family)})
            raise ValidationError(self.error_messages['invalid'])


class NoPrefixInetAddressFormField(forms.Field):
    widget = forms.TextInput
    default_error_messages = {
        'invalid': u'Enter a valid IP address.',
        'invalid_address_family': u'Enter a valid %(address_family)s address.',
    }

    def __init__(self, address_family=UNSPECIFIED, **kwargs):
        self.address_family = address_family
        super(NoPrefixInetAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddressBase):
            return value

        if isinstance(value, text_type):
            value = value.strip()

        try:
            return get_address_type_by_address_family(self.address_family)(value)
        except (ValueError, AddressValueError):
            if self.address_family != UNSPECIFIED:
                raise ValidationError(self.error_messages['invalid_address_family'],
                                      params={'address_family': 'IPv{}'.format(self.address_family)})
            raise ValidationError(self.error_messages['invalid'])


class CidrAddressFormField(forms.Field):
    widget = forms.TextInput
    default_error_messages = {
        'invalid': u'Enter a valid CIDR address.',
        'invalid_address_family': u'Enter a valid %(address_family)s CIDR address.',
        'network': u'Must be a network address.',
    }

    def __init__(self, address_family=UNSPECIFIED, *args, **kwargs):
        self.address_family = address_family
        super(CidrAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _BaseNetwork):
            network = value

        if isinstance(value, text_type):
            value = value.strip()

        try:
            network = get_network_type_by_address_family(self.address_family)(value)
        except (ValueError, AddressValueError) as e:
            if 'has host bits' in e.args[0]:
                raise ValidationError(self.error_messages['network'])
            if self.address_family != UNSPECIFIED:
                raise ValidationError(self.error_messages['invalid_address_family'],
                                      params={'address_family': 'IPv{}'.format(self.address_family)})
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
        except (AddrFormatError, IndexError, TypeError):
            raise ValidationError(self.error_messages['invalid'])

    def widget_attrs(self, widget):
        attrs = super(MACAddressFormField, self).widget_attrs(widget)
        attrs.update({'maxlength': '17'})
        return attrs
