from IPy import IP

from django.db import models, connection, DEFAULT_DB_ALIAS

from netfields import *

class InetTestModel(models.Model):
    '''
    >>> cursor = connection.cursor()

    >>> InetTestModel(inet='10.0.0.1').save()

    >>> InetTestModel(inet=IP('10.0.0.1')).save()

    >>> InetTestModel(inet='').save()
    Traceback (most recent call last):
        ...
    IntegrityError: inet.inet may not be NULL

    >>> InetTestModel(inet='az').save()
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'az'

    >>> InetTestModel(inet=None).save()
    Traceback (most recent call last):
        ...
    IntegrityError: inet.inet may not be NULL

    >>> InetTestModel().save()
    Traceback (most recent call last):
        ...
    IntegrityError: inet.inet may not be NULL

    >>> InetTestModel.objects.filter(inet='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" = %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__exact='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" = %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__iexact='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" = %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contains='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" >> %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__in=['10.0.0.1', '10.0.0.2']).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" IN (%s, %s)', (u'10.0.0.1', u'10.0.0.2'))

    >>> InetTestModel.objects.filter(inet__gt='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" > %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__gte='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" >= %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__lt='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" < %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__lte='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" <= %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__startswith='10.').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__istartswith='10.').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__endswith='.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__iendswith='.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__range=('10.0.0.1', '10.0.0.10')).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" BETWEEN %s and %s', (u'10.0.0.1', u'10.0.0.10'))

    >>> InetTestModel.objects.filter(inet__year=1).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "year"

    >>> InetTestModel.objects.filter(inet__month=1).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "month"

    >>> InetTestModel.objects.filter(inet__day=1).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "day"

    >>> InetTestModel.objects.filter(inet__isnull=True).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" IS NULL', ())

    >>> InetTestModel.objects.filter(inet__isnull=False).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" IS NOT NULL', ())

    >>> InetTestModel.objects.filter(inet__search='10').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "search"

    >>> InetTestModel.objects.filter(inet__regex=u'10').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ~* %s ', (u'10',))

    >>> InetTestModel.objects.filter(inet__iregex=u'10').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ~* %s ', (u'10',))

    >>> InetTestModel.objects.filter(inet__net_contains_or_equals='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" >>= %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contained='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" << %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contained_or_equal='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" <<= %s ', (u'10.0.0.1',))
    '''

    inet = InetAddressField()
    objects = NetManager()

    class Meta:
        db_table = 'inet'

class NullInetTestModel(models.Model):
    '''
    >>> NullInetTestModel(inet='10.0.0.1').save()

    >>> NullInetTestModel(inet=IP('10.0.0.1')).save()

    >>> NullInetTestModel(inet='').save()

    >>> NullInetTestModel(inet=None).save()

    >>> NullInetTestModel().save()
    '''

    inet = InetAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'nullinet'

class CidrTestModel(models.Model):
    '''
    >>> CidrTestModel.objects.filter(cidr='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" = %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__exact='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" = %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__iexact='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" = %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__net_contains='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" >> %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__in=['10.0.0.1', '10.0.0.2']).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" IN (%s, %s)', (u'10.0.0.1', u'10.0.0.2'))

    >>> CidrTestModel.objects.filter(cidr__gt='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" > %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__gte='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" >= %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__lt='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" < %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__lte='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" <= %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__startswith='10.').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'10.%',))

    >>> CidrTestModel.objects.filter(cidr__istartswith='10.').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'10.%',))

    >>> CidrTestModel.objects.filter(cidr__endswith='.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'%.1',))

    >>> CidrTestModel.objects.filter(cidr__iendswith='.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'%.1',))

    >>> CidrTestModel.objects.filter(cidr__range=('10.0.0.1', '10.0.0.10')).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" BETWEEN %s and %s', (u'10.0.0.1', u'10.0.0.10'))

    >>> CidrTestModel.objects.filter(cidr__year=1).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "year"

    >>> CidrTestModel.objects.filter(cidr__month=1).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "month"

    >>> CidrTestModel.objects.filter(cidr__day=1).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "day"

    >>> CidrTestModel.objects.filter(cidr__isnull=True).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" IS NULL', ())

    >>> CidrTestModel.objects.filter(cidr__isnull=False).query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" IS NOT NULL', ())

    >>> CidrTestModel.objects.filter(cidr__search='10').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "search"

    >>> CidrTestModel.objects.filter(cidr__regex=u'10').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ~* %s ', (u'10',))

    >>> CidrTestModel.objects.filter(cidr__iregex=u'10').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ~* %s ', (u'10',))

    >>> CidrTestModel.objects.filter(cidr__net_contains_or_equals='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" >>= %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__net_contained='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" << %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__net_contained_or_equal='10.0.0.1').query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" <<= %s ', (u'10.0.0.1',))
    '''

    cidr = CidrAddressField()
    objects = NetManager()

    class Meta:
        db_table = 'cidr'

class MACTestModel(models.Model):
    mac = MACAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'mac'

