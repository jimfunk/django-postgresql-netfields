from IPy import IP

from django.db import IntegrityError
from django.test import TestCase

from netfields.models import (CidrTestModel, InetTestModel, NullCidrTestModel,
                              NullInetTestModel)


class BaseTestCase(object):
    select = 'SELECT "table"."id", "table"."field" FROM "table" '

    def assertSqlEquals(self, qs, sql):
        sql = sql.replace('"table"', '"%s"' % self.table)
        self.assertEqual(qs.query.get_compiler(qs.db).as_sql()[0], sql)

    def assertSqlRaises(self, qs, error):
        self.assertRaises(error, qs.query.get_compiler(qs.db).as_sql)

    def test_init_with_blank(self):
        self.model()

    def test_init_with_text_fails(self):
        self.assertRaises(ValueError, self.model, field='abc')

    def test_save(self):
        self.model(field='10.0.0.1').save()

    def test_save_object(self):
        self.model(field=IP('10.0.0.1')).save()

    def test_equals_lookup(self):
        self.assertSqlEquals(self.qs.filter(field='10.0.0.1'),
            self.select + 'WHERE "table"."field" = %s ')

    def test_exact_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__exact='10.0.0.1'),
            self.select + 'WHERE "table"."field" = %s ')

    def test_iexact_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__iexact='10.0.0.1'),
            self.select + 'WHERE "table"."field" = %s ')

    def test_net_contains_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__net_contains='10.0.0.1'),
            self.select + 'WHERE "table"."field" >> %s ')

    def test_in_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__in=['10.0.0.1', '10.0.0.2']),
            self.select + 'WHERE "table"."field" IN (%s, %s)')

    def test_gt_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__gt='10.0.0.1'),
            self.select + 'WHERE "table"."field" > %s ')

    def test_gte_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__gte='10.0.0.1'),
            self.select + 'WHERE "table"."field" >= %s ')

    def test_lt_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__lt='10.0.0.1'),
            self.select + 'WHERE "table"."field" < %s ')

    def test_lte_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__lte='10.0.0.1'),
            self.select + 'WHERE "table"."field" <= %s ')

    def test_range_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__range=('10.0.0.1', '10.0.0.10')),
            self.select + 'WHERE "table"."field" BETWEEN %s and %s')

    def test_year_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__year=1), ValueError)

    def test_month_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__month=1), ValueError)

    def test_day_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__day=1), ValueError)

    def test_isnull_true_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__isnull=True),
            self.select + 'WHERE "table"."field" IS NULL')

    def test_isnull_false_lookup(self):
        self.assertSqlEquals(self.qs.filter(field__isnull=False),
            self.select + 'WHERE "table"."field" IS NOT NULL')

    def test_search_lookup_fails(self):
        self.assertSqlRaises(self.qs.filter(field__search='10'), ValueError)

    def test_net_contains_or_equals(self):
        self.assertSqlEquals(self.qs.filter(field__net_contains_or_equals='10.0.0.1'),
            self.select + 'WHERE "table"."field" >>= %s ')

    def test_net_contained(self):
        self.assertSqlEquals(self.qs.filter(field__net_contained='10.0.0.1'),
            self.select + 'WHERE "table"."field" << %s ')

    def test_net_contained_or_equals(self):
        self.assertSqlEquals(self.qs.filter(field__net_contained_or_equal='10.0.0.1'),
            self.select + 'WHERE "table"."field" <<= %s ')


class BaseInetFieldTestCase(BaseTestCase):
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


class BaseCidrFieldTestCase(BaseTestCase):
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
