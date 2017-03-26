from __future__ import unicode_literals
from ipaddress import ip_address, ip_interface, ip_network
from netaddr import EUI

from django.forms import ModelForm
from django.test import TestCase

from test.models import (
    CidrTestModel,
    InetTestModel,
    UniqueInetTestModel,
    UniqueCidrTestModel,
    NoPrefixInetTestModel,
    MACTestModel
)
from netfields.mac import mac_unix_common


class InetAddressTestModelForm(ModelForm):
    class Meta:
        model = InetTestModel
        exclude = []


class TestInetAddressFormField(TestCase):
    form_class = InetAddressTestModelForm

    def test_form_ipv4_valid(self):
        form = self.form_class({'field': '10.0.0.1'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_interface('10.0.0.1'))

    def test_form_ipv4_invalid(self):
        form = self.form_class({'field': '10.0.0.1.2'})
        self.assertFalse(form.is_valid())

    def test_form_ipv4_strip(self):
        form = self.form_class({'field': ' 10.0.0.1 '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_interface('10.0.0.1'))

    def test_form_ipv4_change(self):
        instance = InetTestModel.objects.create(field='10.1.2.3/24')
        form = self.form_class({'field': '10.1.2.4/24'}, instance=instance)
        self.assertTrue(form.is_valid())
        form.save()
        instance = InetTestModel.objects.get(pk=instance.pk)
        self.assertEqual(instance.field, ip_interface('10.1.2.4/24'))

    def test_form_ipv6_valid(self):
        form = self.form_class({'field': '2001:0:1::2'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_interface('2001:0:1::2'))

    def test_form_ipv6_invalid(self):
        form = self.form_class({'field': '2001:0::1::2'})
        self.assertFalse(form.is_valid())

    def test_form_ipv6_strip(self):
        form = self.form_class({'field': ' 2001:0:1::2 '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_interface('2001:0:1::2'))

    def test_form_ipv6_change(self):
        instance = InetTestModel.objects.create(field='2001:0:1::2/64')
        form = self.form_class({'field': '2001:0:1::3/64'}, instance=instance)
        self.assertTrue(form.is_valid())
        form.save()
        instance = InetTestModel.objects.get(pk=instance.pk)
        self.assertEqual(instance.field, ip_interface('2001:0:1::3/64'))


class NoPrefixInetAddressTestModelForm(ModelForm):
    class Meta:
        model = NoPrefixInetTestModel
        exclude = []


class TestNoPrefixInetAddressFormField(TestCase):
    form_class = NoPrefixInetAddressTestModelForm

    def test_form_ipv4_valid(self):
        form = self.form_class({'field': '10.0.0.1'})
        self.assertTrue(form.is_valid())
        # Form always passes ip_interface. Model field will return the requested type
        self.assertEqual(form.cleaned_data['field'], ip_interface('10.0.0.1'))

    def test_form_ipv4_invalid(self):
        form = self.form_class({'field': '10.0.0.1.2'})
        self.assertFalse(form.is_valid())

    def test_form_ipv4_strip(self):
        form = self.form_class({'field': ' 10.0.0.1 '})
        self.assertTrue(form.is_valid())
        # Form always passes ip_interface. Model field will return the requested type
        self.assertEqual(form.cleaned_data['field'], ip_interface('10.0.0.1'))

    def test_form_ipv4_change(self):
        instance = NoPrefixInetTestModel.objects.create(field='10.1.2.3/24')
        form = self.form_class({'field': '10.1.2.4/24'}, instance=instance)
        self.assertTrue(form.is_valid())
        form.save()
        instance = NoPrefixInetTestModel.objects.get(pk=instance.pk)
        self.assertEqual(instance.field, ip_address('10.1.2.4'))

    def test_form_ipv6_valid(self):
        form = self.form_class({'field': '2001:0:1::2'})
        self.assertTrue(form.is_valid())
        # Form always passes ip_interface. Model field will return the requested type
        self.assertEqual(form.cleaned_data['field'], ip_interface('2001:0:1::2'))

    def test_form_ipv6_invalid(self):
        form = self.form_class({'field': '2001:0::1::2'})
        self.assertFalse(form.is_valid())

    def test_form_ipv6_strip(self):
        form = self.form_class({'field': ' 2001:0:1::2 '})
        self.assertTrue(form.is_valid())
        # Form always passes ip_interface. Model field will return the requested type
        self.assertEqual(form.cleaned_data['field'], ip_interface('2001:0:1::2'))

    def test_form_ipv6_change(self):
        instance = NoPrefixInetTestModel.objects.create(field='2001:0:1::2/64')
        form = self.form_class({'field': '2001:0:1::3/64'}, instance=instance)
        self.assertTrue(form.is_valid())
        form.save()
        instance = NoPrefixInetTestModel.objects.get(pk=instance.pk)
        self.assertEqual(instance.field, ip_address('2001:0:1::3'))


class UniqueInetAddressTestModelForm(ModelForm):
    class Meta:
        model = UniqueInetTestModel
        exclude = []


class TestUniqueInetAddressFormField(TestInetAddressFormField):
    form_class = UniqueInetAddressTestModelForm


class CidrAddressTestModelForm(ModelForm):
    class Meta:
        model = CidrTestModel
        exclude = []


class TestCidrAddressFormField(TestCase):
    form_class = CidrAddressTestModelForm

    def test_form_ipv4_valid(self):
        form = self.form_class({'field': '10.0.1.0/24'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_network('10.0.1.0/24'))

    def test_form_ipv4_invalid(self):
        form = self.form_class({'field': '10.0.0.1.2/32'})
        self.assertFalse(form.is_valid())

    def test_form_ipv4_strip(self):
        form = self.form_class({'field': ' 10.0.1.0/24 '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_network('10.0.1.0/24'))

    def test_form_ipv4_bits_to_right_of_mask(self):
        form = self.form_class({'field': '10.0.0.1.2/24'})
        self.assertFalse(form.is_valid())

    def test_form_ipv6_valid(self):
        form = self.form_class({'field': '2001:0:1::/64'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_network('2001:0:1::/64'))

    def test_form_ipv6_invalid(self):
        form = self.form_class({'field': '2001:0::1::2/128'})
        self.assertFalse(form.is_valid())

    def test_form_ipv6_strip(self):
        form = self.form_class({'field': ' 2001:0:1::/64 '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], ip_network('2001:0:1::/64'))

    def test_form_ipv6_bits_to_right_of_mask(self):
        form = self.form_class({'field': '2001:0::1::2/64'})
        self.assertFalse(form.is_valid())


class UniqueCidrAddressTestModelForm(ModelForm):
    class Meta:
        model = UniqueCidrTestModel
        exclude = []


class TestUniqueCidrAddressFormField(TestCidrAddressFormField):
    form_class = UniqueCidrAddressTestModelForm


class MacAddressTestModelForm(ModelForm):
    class Meta:
        model = MACTestModel
        exclude = []


class TestMacAddressFormField(TestCase):
    def setUp(self):
        self.mac = EUI('00:aa:2b:c3:dd:44', dialect=mac_unix_common)

    def test_unix(self):
        form = MacAddressTestModelForm({'field': '0:AA:2b:c3:dd:44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_unix_common(self):
        form = MacAddressTestModelForm({'field': '00:aa:2b:c3:dd:44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_eui48(self):
        form = MacAddressTestModelForm({'field': '00-AA-2B-C3-DD-44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_cisco(self):
        form = MacAddressTestModelForm({'field': '00aa.2bc3.dd44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_24bit_colon(self):
        form = MacAddressTestModelForm({'field': '00aa2b:c3dd44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_24bit_hyphen(self):
        form = MacAddressTestModelForm({'field': '00aa2b-c3dd44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_bare(self):
        form = MacAddressTestModelForm({'field': '00aa2b:c3dd44'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_strip(self):
        form = MacAddressTestModelForm({'field': ' 00:aa:2b:c3:dd:44 '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], self.mac)

    def test_invalid(self):
        form = MacAddressTestModelForm({'field': 'notvalid'})
        self.assertFalse(form.is_valid())
