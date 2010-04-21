import re
from IPy import IP

from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class NetInput(forms.Widget):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        # Default forms.Widget compares value != '' which breaks IP...
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value:
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % forms.util.flatatt(final_attrs))


class NetAddressFormField(forms.Field):
    widget = NetInput
    default_error_messages = {
        'invalid': u'Enter a valid IP Address.',
    }

    def __init__(self, *args, **kwargs):
        super(NetAddressFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(NetAddressFormField, self).clean(value)

        if value in (None, ''):
            return None
        if isinstance(value, IP):
            return value
        try:
            return IP(value)
        except ValueError, e:
            raise forms.ValidationError(e)


mac_re = re.compile(r'^(([A-F0-9]{2}:){5}[A-F0-9]{2})$')

class MACAddressFormField(forms.RegexField):
    default_error_messages = {
        'invalid': u'Enter a valid MAC address.',
    }

    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(mac_re, *args, **kwargs)
