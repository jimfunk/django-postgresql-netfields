from IPy import IP
from netaddr import EUI

from django.db import IntegrityError
from django.forms import ModelForm
from django.test import TestCase

from netfields.models import (CidrTestModel, InetTestModel, NullCidrTestModel,
                              NullInetTestModel, MACTestModel)
from netfields.mac import mac_unix_common


class BaseSqlTestCase(object):
    select = 'SELECT "table"."id", "table"."field" FROM "table" '

    def assertSqlEquals(self, qs, sql):
        sql = sql.replace('"table"', '"%s"' % self.table)
        self.assertEqual(qs.query.get_compiler(qs.db).as_sql()[0], sql)

    def assertSqlRaises(self, qs, error):
        self.assertRaises(error, qs.query.get_compiler(qs.db).as_sql)

    def test_init_with_blank(self):
        self.model()

    def test_isnull_true_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__isnull=True),
            self.select + 'WHERE "table"."field" IS NULL')

    def test_isnull_false_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__isnull=False),
            self.select + 'WHERE "table"."field" IS NOT NULL')

    def test_save(self):
        self.model(field=self.value1).save()

    def test_equals_lookup(self):
        self.assertSqlEquals(self.qs.filter(field=self.value1),
            self.select + 'WHERE "table"."field" = %s ')

    def test_exact_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__exact=self.value1),
            self.select + 'WHERE "table"."field" = %s ')

    def test_in_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__in=[self.value1, self.value2]),
            self.select + 'WHERE "table"."field" IN (%s, %s)')

    def test_gt_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__gt=self.value1),
            self.select + 'WHERE "table"."field" > %s ')

    def test_gte_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__gte=self.value1),
            self.select + 'WHERE "table"."field" >= %s ')

    def test_lt_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__lt=self.value1),
            self.select + 'WHERE "table"."field" < %s ')

    def test_lte_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__lte=self.value1),
            self.select + 'WHERE "table"."field" <= %s ')

    def test_range_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__range=(self.value1, self.value3)),
            self.select + 'WHERE "table"."field" BETWEEN %s and %s')



class BaseInetTestCase(BaseSqlTestCase):
    value1 = '10.0.0.1'
    value2 = '10.0.0.2'
    value3 = '10.0.0.10'

    def test_save_object(self):
        self.model(field=IP(self.value1)).save()

    def test_init_with_text_fails(self):
        self.assertRaises(ValueError, self.model, field='abc')

    def test_iexact_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iexact=self.value1),
            self.select + 'WHERE "table"."field" = %s ')

    def test_search_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__search='10'), ValueError)

    def test_year_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__year=1), ValueError)

    def test_month_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__month=1), ValueError)

    def test_day_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__day=1), ValueError)

    def test_net_contains_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__net_contains='10.0.0.1'),
            self.select + 'WHERE "table"."field" >> %s ')

    def test_net_contains_or_equals(self):
        self.assertSqlEquals(self.qs.filter(field__net_contains_or_equals='10.0.0.1'),
            self.select + 'WHERE "table"."field" >>= %s ')

    def test_net_contained(self):
        self.assertSqlEquals(self.qs.filter(field__net_contained='10.0.0.1'),
            self.select + 'WHERE "table"."field" << %s ')

    def test_net_contained_or_equals(self):
        self.assertSqlEquals(self.qs.filter(field__net_contained_or_equal='10.0.0.1'),
            self.select + 'WHERE "table"."field" <<= %s ')


class BaseInetFieldTestCase(BaseInetTestCase):
    def test_startswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__startswith='10.'),
            self.select + 'WHERE HOST("table"."field") ILIKE %s ')

    def test_istartswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__istartswith='10.'),
            self.select + 'WHERE HOST("table"."field") ILIKE %s ')

    def test_endswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__endswith='.1'),
            self.select + 'WHERE HOST("table"."field") ILIKE %s ')

    def test_iendswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iendswith='.1'),
            self.select + 'WHERE HOST("table"."field") ILIKE %s ')

    def test_regex_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__regex='10'),
            self.select + 'WHERE HOST("table"."field") ~* %s ')

    def test_iregex_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iregex='10'),
            self.select + 'WHERE HOST("table"."field") ~* %s ')


class BaseCidrFieldTestCase(BaseInetTestCase):
    def test_startswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__startswith='10.'),
            self.select + 'WHERE TEXT("table"."field") ILIKE %s ')

    def test_istartswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__istartswith='10.'),
            self.select + 'WHERE TEXT("table"."field") ILIKE %s ')

    def test_endswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__endswith='.1'),
            self.select + 'WHERE TEXT("table"."field") ILIKE %s ')

    def test_iendswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iendswith='.1'),
            self.select + 'WHERE TEXT("table"."field") ILIKE %s ')

    def test_regex_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__regex='10'),
            self.select + 'WHERE TEXT("table"."field") ~* %s ')

    def test_iregex_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iregex='10'),
            self.select + 'WHERE TEXT("table"."field") ~* %s ')


class TestInetField(BaseInetFieldTestCase, TestCase):
    def setUp(self):
        self.model = InetTestModel
        self.qs = self.model.objects.all()
        self.table = 'inet'

    def test_save_blank_fails(self):
        self.assertRaises(IntegrityError, self.model(field='').save)

    def test_save_none_fails(self):
        self.assertRaises(IntegrityError, self.model(field=None).save)

    def test_save_nothing_fails(self):
        self.assertRaises(IntegrityError, self.model().save)


class TestInetFieldNullable(BaseInetFieldTestCase, TestCase):
    def setUp(self):
        self.model = NullInetTestModel
        self.qs = self.model.objects.all()
        self.table = 'nullinet'

    def test_save_blank(self):
        self.model().save()

    def test_save_none(self):
        self.model(field=None).save()

    def test_save_nothing_fails(self):
        self.model().save()


class TestCidrField(BaseCidrFieldTestCase, TestCase):
    def setUp(self):
        self.model = CidrTestModel
        self.qs = self.model.objects.all()
        self.table = 'cidr'

    def test_save_blank_fails(self):
        self.assertRaises(IntegrityError, self.model(field='').save)

    def test_save_none_fails(self):
        self.assertRaises(IntegrityError, self.model(field=None).save)

    def test_save_nothing_fails(self):
        self.assertRaises(IntegrityError, self.model().save)


class TestCidrFieldNullable(BaseCidrFieldTestCase, TestCase):
    def setUp(self):
        self.model = NullCidrTestModel
        self.qs = self.model.objects.all()
        self.table = 'nullcidr'

    def test_save_blank(self):
        self.model().save()

    def test_save_none(self):
        self.model(field=None).save()

    def test_save_nothing_fails(self):
        self.model().save()


class InetTestModelForm(ModelForm):
    class Meta:
        model = InetTestModel


class TestNetAddressFormField(TestCase):
    def test_form_ipv4_valid(self):
        form = InetTestModelForm({'field': '10.0.0.1'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], IP('10.0.0.1'))

    def test_form_ipv4_invalid(self):
        form = InetTestModelForm({'field': '10.0.0.1.2'})
        self.assertFalse(form.is_valid())

    def test_form_ipv6(self):
        form = InetTestModelForm({'field': '2001:0:1::2'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['field'], IP('2001:0:1::2'))

    def test_form_ipv6_invalid(self):
        form = InetTestModelForm({'field': '2001:0::1::2'})
        self.assertFalse(form.is_valid())


class BaseMacTestCase(BaseSqlTestCase):
    value1 = '00:aa:2b:c3:dd:44'
    value2 = '00:aa:2b:c3:dd:45'
    value3 = '00:aa:2b:c3:dd:ff'

    def test_save_object(self):
        self.model(field=EUI(self.value1)).save()

    def test_iexact_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iexact=self.value1),
            self.select + 'WHERE UPPER("table"."field"::text) = UPPER(%s) ')

    def test_startswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__startswith='00:'),
            self.select + 'WHERE "table"."field"::text LIKE %s ')

    def test_istartswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__istartswith='00:'),
            self.select + 'WHERE UPPER("table"."field"::text) LIKE UPPER(%s) ')

    def test_endswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__endswith=':ff'),
            self.select + 'WHERE "table"."field"::text LIKE %s ')

    def test_iendswith_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iendswith=':ff'),
            self.select + 'WHERE UPPER("table"."field"::text) LIKE UPPER(%s) ')

    def test_regex_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__regex='00'),
            self.select + 'WHERE "table"."field" ~ %s ')

    def test_iregex_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iregex='00'),
            self.select + 'WHERE "table"."field" ~* %s ')


class TestMacAddressField(BaseMacTestCase, TestCase):
    def setUp(self):
        self.model = MACTestModel
        self.qs = self.model.objects.all()
        self.table = 'mac'

    def test_save_blank(self):
        self.model().save()

    def test_save_none(self):
        self.model(field=None).save()

    def test_save_nothing_fails(self):
        self.model().save()


class MacAddressTestModelForm(ModelForm):
    class Meta:
        model = MACTestModel


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

    def test_invalid(self):
        form = MacAddressTestModelForm({'field': 'notvalid'})
        self.assertFalse(form.is_valid())
