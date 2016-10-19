from __future__ import unicode_literals
import django
from django import VERSION
from django.core.exceptions import ValidationError
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
    ip_address,
    ip_interface,
    ip_network,
)
from netaddr import EUI

from django.db import IntegrityError
from django.db.models.sql import EmptyResultSet
from django.core.exceptions import FieldError
from django.test import TestCase
from unittest import skipIf

from test.models import (
    CidrArrayTestModel,
    CidrTestModel,
    InetArrayTestModel,
    InetTestModel,
    NullCidrTestModel,
    NullInetTestModel,
    UniqueInetTestModel,
    UniqueCidrTestModel,
    NoPrefixInetTestModel,
    MACArrayTestModel,
    MACTestModel
)


class BaseSqlTestCase(object):
    select = u'SELECT "table"."id", "table"."field" FROM "table" '

    def assertSqlEquals(self, qs, sql):
        sql = sql.replace('"table"', '"%s"' % self.table)
        self.assertEqual(
            qs.query.get_compiler(qs.db).as_sql()[0].strip().lower(),
            sql.strip().lower()
        )

    def compile_queryset(self, qs):
        qs.query.get_compiler(qs.db).as_sql()

    def test_init_with_blank(self):
        self.model()

    def test_isnull_true_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__isnull=True),
            self.select + 'WHERE "table"."field" IS NULL'
        )

    def test_isnull_false_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__isnull=False),
            self.select + 'WHERE "table"."field" IS NOT NULL'
        )

    def test_save(self):
        self.model(field=self.value1).save()

    def test_equals_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field=self.value1),
            self.select + 'WHERE "table"."field" = %s'
        )

    def test_exact_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__exact=self.value1),
            self.select + 'WHERE "table"."field" = %s'
        )

    def test_in_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__in=[self.value1, self.value2]),
            self.select + 'WHERE "table"."field" IN (%s, %s)'
        )

    def test_in_single_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__in=[self.value1]),
            self.select + 'WHERE "table"."field" IN (%s)'
        )

    def test_in_empty_lookup(self):
        with self.assertRaises(EmptyResultSet):
            self.qs.filter(field__in=[]).query.get_compiler(self.qs.db).as_sql()

    def test_gt_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__gt=self.value1),
            self.select + 'WHERE "table"."field" > %s'
        )

    def test_gte_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__gte=self.value1),
            self.select + 'WHERE "table"."field" >= %s'
        )

    def test_lt_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__lt=self.value1),
            self.select + 'WHERE "table"."field" < %s'
        )

    def test_lte_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__lte=self.value1),
            self.select + 'WHERE "table"."field" <= %s'
        )

    def test_range_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__range=(self.value1, self.value3)),
            self.select + 'WHERE "table"."field" BETWEEN %s AND %s'
        )


class BaseInetTestCase(BaseSqlTestCase):
    def test_save_object(self):
        self.model(field=self.value1).save()

    def test_save_with_text_fails(self):
        self.assertRaises(ValidationError, self.model.objects.create, field='abc')

    def test_iexact_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iexact=self.value1),
            self.select + 'WHERE UPPER("table"."field"::text) = UPPER(%s)'
        )

    def test_search_lookup_fails(self):
        with self.assertRaises(NotImplementedError):
            self.compile_queryset(self.qs.filter(field__search='10'))

    def test_year_lookup_fails(self):
        with self.assertRaises(FieldError):
            self.compile_queryset(self.qs.filter(field__year=1))

    def test_month_lookup_fails(self):
        with self.assertRaises(FieldError):
            self.compile_queryset(self.qs.filter(field__month=1))

    def test_day_lookup_fails(self):
        with self.assertRaises(FieldError):
            self.compile_queryset(self.qs.filter(field__day=1))

    def test_net_contained(self):
        self.assertSqlEquals(
            self.qs.filter(field__net_contained='10.0.0.0/24'),
            self.select + 'WHERE "table"."field" << %s'
        )

    def test_net_contained_or_equals(self):
        self.assertSqlEquals(
            self.qs.filter(field__net_contained_or_equal='10.0.0.0/24'),
            self.select + 'WHERE "table"."field" <<= %s'
        )

    def test_net_overlaps(self):
        self.assertSqlEquals(
            self.qs.filter(field__net_overlaps='10.0.0.0/24'),
            self.select + 'WHERE "table"."field" && %s',
        )

    def test_family_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__family=4),
            self.select + 'WHERE family("table"."field") = %s'
        )


class BaseInetFieldTestCase(BaseInetTestCase):
    value1 = '10.0.0.1'
    value2 = '10.0.0.2/24'
    value3 = '10.0.0.10'

    def test_startswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__startswith='10.'),
            self.select + 'WHERE HOST("table"."field") LIKE %s'
        )

    def test_istartswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__istartswith='10.'),
            self.select + 'WHERE HOST("table"."field") LIKE UPPER(%s)'
        )

    def test_endswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__endswith='.1'),
            self.select + 'WHERE HOST("table"."field") LIKE %s'
        )

    def test_iendswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iendswith='.1'),
            self.select + 'WHERE HOST("table"."field") LIKE UPPER(%s)'
        )

    def test_regex_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__regex='10'),
            self.select + 'WHERE HOST("table"."field") ~ %s'
        )

    def test_iregex_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iregex='10'),
            self.select + 'WHERE HOST("table"."field") ~* %s'
        )

    def test_query_filter_str(self):
        self.model.objects.filter(field='1.2.3.4')

    def test_query_filter_ipaddress(self):
        self.model.objects.filter(field=ip_interface('1.2.3.4'))

    def test_query_filter_contains_ipnetwork(self):
        self.model.objects.filter(field__net_contains=ip_network('1.2.3.0/24'))


class BaseCidrFieldTestCase(BaseInetTestCase):
    value1 = '10.0.0.1/32'
    value2 = '10.0.2.0/24'
    value3 = '10.5.0.0/16'

    def test_startswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__startswith='10.'),
            self.select + 'WHERE TEXT("table"."field") LIKE %s'
        )

    def test_istartswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__istartswith='10.'),
            self.select + 'WHERE TEXT("table"."field") LIKE UPPER(%s)'
        )

    def test_endswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__endswith='.1'),
            self.select + 'WHERE TEXT("table"."field") LIKE %s'
        )

    def test_iendswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iendswith='.1'),
            self.select + 'WHERE TEXT("table"."field") LIKE UPPER(%s)'
        )

    def test_regex_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__regex='10'),
            self.select + 'WHERE TEXT("table"."field") ~ %s'
        )

    def test_iregex_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iregex='10'),
            self.select + 'WHERE TEXT("table"."field") ~* %s'
        )

    def test_net_contains_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__net_contains='10.0.0.1'),
            self.select + 'WHERE "table"."field" >> %s'
        )

    def test_net_contains_or_equals(self):
        self.assertSqlEquals(
            self.qs.filter(field__net_contains_or_equals='10.0.0.1'),
            self.select + 'WHERE "table"."field" >>= %s'
        )

    def test_query_filter_str(self):
        self.model.objects.filter(field='1.2.3.0/24')

    def test_query_filter_ipnetwork(self):
        self.model.objects.filter(field=ip_network('1.2.3.0/24'))

    def test_max_prefixlen(self):
        self.assertSqlEquals(
            self.qs.filter(field__max_prefixlen='16'),
            self.select + 'WHERE masklen("table"."field") <= %s'
        )

    def test_min_prefixlen(self):
        self.assertSqlEquals(
            self.qs.filter(field__min_prefixlen='16'),
            self.select + 'WHERE masklen("table"."field") >= %s'
        )

    def test_prefixlen(self):
        self.assertSqlEquals(
            self.qs.filter(field__prefixlen='16'),
            self.select + 'WHERE masklen("table"."field") = %s'
        )


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

    def test_save_accepts_bytes(self):
        self.model(field=b'1.1.1.1/24').save()

    def test_retrieves_ipv4_ipinterface_type(self):
        instance = self.model.objects.create(field='10.1.2.3/24')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, IPv4Interface)

    def test_retrieves_ipv6_ipinterface_type(self):
        instance = self.model.objects.create(field='2001:db8::1/32')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, IPv6Interface)

    def test_save_preserves_prefix_length(self):
        instance = self.model.objects.create(field='10.1.2.3/24')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertEqual(str(instance.field), '10.1.2.3/24')


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


class TestInetFieldUnique(BaseInetFieldTestCase, TestCase):
    def setUp(self):
        self.model = UniqueInetTestModel
        self.qs = self.model.objects.all()
        self.table = 'uniqueinet'

    def test_save_nonunique(self):
        self.model(field='1.2.3.4').save()
        self.assertRaises(IntegrityError, self.model(field='1.2.3.4').save)


class TestInetFieldNoPrefix(BaseInetFieldTestCase, TestCase):
    def setUp(self):
        self.model = NoPrefixInetTestModel
        self.qs = self.model.objects.all()
        self.table = 'noprefixinet'

    def test_save_truncates_prefix_length(self):
        instance = self.model.objects.create(field='10.1.2.3/24')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertEqual(str(instance.field), '10.1.2.3')

    def test_retrieves_ipv4_ipaddress_type(self):
        instance = self.model.objects.create(field='10.1.2.3/24')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, IPv4Address)

    def test_retrieves_ipv6_ipaddress_type(self):
        instance = self.model.objects.create(field='2001:db8::1/32')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, IPv6Address)


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

    def test_retrieves_ipv4_ipnetwork_type(self):
        instance = self.model.objects.create(field='10.1.2.0/24')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, IPv4Network)

    def test_retrieves_ipv6_ipnetwork_type(self):
        instance = self.model.objects.create(field='2001:db8::0/32')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, IPv6Network)


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


class TestCidrFieldUnique(BaseCidrFieldTestCase, TestCase):
    def setUp(self):
        self.model = UniqueCidrTestModel
        self.qs = self.model.objects.all()
        self.table = 'uniquecidr'

    def test_save_nonunique(self):
        self.model(field='1.2.3.0/24').save()
        self.assertRaises(IntegrityError, self.model(field='1.2.3.0/24').save)


class BaseMacTestCase(BaseSqlTestCase):
    value1 = '00:aa:2b:c3:dd:44'
    value2 = '00:aa:2b:c3:dd:45'
    value3 = '00:aa:2b:c3:dd:ff'

    def test_save_object(self):
        self.model(field=EUI(self.value1)).save()

    def test_iexact_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iexact=self.value1),
            self.select + 'WHERE UPPER("table"."field"::text) = UPPER(%s)'
        )

    def test_startswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__startswith='00:'),
            self.select + 'WHERE "table"."field"::text LIKE %s'
        )

    def test_istartswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__istartswith='00:'),
            self.select + 'WHERE UPPER("table"."field"::text) LIKE UPPER(%s)'
        )

    def test_endswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__endswith=':ff'),
            self.select + 'WHERE "table"."field"::text LIKE %s'
        )

    def test_iendswith_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iendswith=':ff'),
            self.select + 'WHERE UPPER("table"."field"::text) LIKE UPPER(%s)'
        )

    def test_regex_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__regex='00'),
            self.select + 'WHERE "table"."field"::text ~ %s'
        )

    def test_iregex_lookup(self):
        self.assertSqlEquals(
            self.qs.filter(field__iregex='00'),
            self.select + 'WHERE "table"."field"::text ~* %s'
        )


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

    def test_invalid_fails(self):
        self.assertRaises(ValidationError, lambda: self.model(field='foobar').save())

    def test_retrieves_eui_type(self):
        instance = self.model.objects.create(field='00:aa:2b:c3:dd:44')
        instance = self.model.objects.get(pk=instance.pk)
        self.assertIsInstance(instance.field, EUI)


class TestInetAddressFieldArray(TestCase):
    def test_save_null(self):
        InetArrayTestModel().save()

    def test_save_single_item(self):
        InetArrayTestModel(field=['10.1.1.1/24']).save()

    def test_save_multiple_items(self):
        InetArrayTestModel(field=['10.1.1.1', '10.1.1.2']).save()

    @skipIf(VERSION < (1, 10), 'ArrayField does not return correct types in Django < 1.10. https://code.djangoproject.com/ticket/25143')
    def test_retrieves_ipv4_ipinterface_type(self):
        instance = InetArrayTestModel(field=['10.1.1.1/24'])
        instance.save()
        instance = InetArrayTestModel.objects.get(id=instance.id)
        self.assertEqual(instance.field, [IPv4Interface('10.1.1.1/24')])
        self.assertIsInstance(instance.field[0], IPv4Interface)


class TestCidrAddressFieldArray(TestCase):
    def test_save_null(self):
        CidrArrayTestModel().save()

    def test_save_single_item(self):
        CidrArrayTestModel(field=['10.1.1.0/24']).save()

    def test_save_multiple_items(self):
        CidrArrayTestModel(field=['10.1.1.0/24', '10.1.2.0/24']).save()

    @skipIf(VERSION < (1, 10), 'ArrayField does not return correct types in Django < 1.10. https://code.djangoproject.com/ticket/25143')
    def test_retrieves_ipv4_ipnetwork_type(self):
        instance = CidrArrayTestModel(field=['10.1.1.0/24'])
        instance.save()
        instance = CidrArrayTestModel.objects.get(id=instance.id)
        self.assertEqual(instance.field, [IPv4Network('10.1.1.0/24')])
        self.assertIsInstance(instance.field[0], IPv4Network)


class TestMACAddressFieldArray(TestCase):
    def test_save_null(self):
        MACArrayTestModel().save()

    def test_save_single_item(self):
        MACArrayTestModel(field=['00:aa:2b:c3:dd:44']).save()

    def test_save_multiple_items(self):
        MACArrayTestModel(field=['00:aa:2b:c3:dd:44', '00:aa:2b:c3:dd:45']).save()

    @skipIf(VERSION < (1, 10), 'ArrayField does not return correct types in Django < 1.10. https://code.djangoproject.com/ticket/25143')
    def test_retrieves_eui_type(self):
        instance = MACArrayTestModel(field=['00:aa:2b:c3:dd:44'])
        instance.save()
        instance = MACArrayTestModel.objects.get(id=instance.id)
        self.assertEqual(instance.field, [EUI('00:aa:2b:c3:dd:44')])
        self.assertIsInstance(instance.field[0], EUI)
