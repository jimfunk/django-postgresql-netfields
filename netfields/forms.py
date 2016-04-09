from ipaddress import ip_interface, ip_network, _IPAddressBase, _BaseNetwork
from netaddr import EUI, AddrFormatError

from django import forms
import django
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

from netfields.mac import mac_unix_common


class NetInput(forms.Widget):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        # Default forms.Widget compares value != '' which breaks IP...
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value:
            final_attrs['value'] = value
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class InetAddressFormField(forms.Field):
    widget = NetInput
    default_error_messages = {
        'invalid': u'Enter a valid IP address.',
    }

    def __init__(self, *args, **kwargs):
        super(InetAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddressBase):
            return value

        try:
            return ip_interface(value)
        except ValueError as e:
            raise ValidationError(self.default_error_messages['invalid'])


class CidrAddressFormField(forms.Field):
    widget = NetInput
    default_error_messages = {
        'invalid': u'Enter a valid CIDR address.',
    }

    def __init__(self, *args, **kwargs):
        super(CidrAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _BaseNetwork):
            network = value

        try:
            network = ip_network(value)
        except ValueError as e:
            raise ValidationError(self.default_error_messages['invalid'])

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

        try:
            return EUI(value, dialect=mac_unix_common)
        except (AddrFormatError, TypeError):
            raise ValidationError(self.error_messages['invalid'])

    def widget_attrs(self, widget):
        attrs = super(MACAddressFormField, self).widget_attrs(widget)
        attrs.update({'maxlength': '17'})
        return attrs
