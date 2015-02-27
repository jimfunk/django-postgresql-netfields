from netaddr import IPAddress, IPNetwork, EUI, AddrFormatError

from django import forms
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
        return mark_safe(u'<input%s />' % forms.util.flatatt(final_attrs))


class InetAddressFormField(forms.Field):
    widget = NetInput
    default_error_messages = {
        'invalid': u'Enter a valid IP Address.',
    }

    def __init__(self, *args, **kwargs):
        super(InetAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, IPAddress):
            return value

        try:
            return IPAddress(value)
        except (AddrFormatError, TypeError) as e:
            raise ValidationError(str(e))


class CidrAddressFormField(forms.Field):
    widget = NetInput
    default_error_messages = {
        'invalid': u'Enter a valid CIDR Address.',
    }

    def __init__(self, *args, **kwargs):
        super(CidrAddressFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, IPNetwork):
            return value

        try:
            return IPNetwork(value)
        except (AddrFormatError, TypeError) as e:
            raise ValidationError(str(e))


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
