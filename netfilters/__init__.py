from IPy import IP

from django.db import models, connection
from django.db.models import sql, query
from django.db.models.query_utils import QueryWrapper

from netfilters.forms import NetAddressFormField, MACAddressFormField

NET_OPERATORS = connection.operators.copy()

for operator in ['contains', 'startswith', 'endswith']:
    NET_OPERATORS[operator] = 'ILIKE %s'
    NET_OPERATORS['i%s' % operator] = 'ILIKE %s'

NET_OPERATORS['iexact'] = NET_OPERATORS['exact']
NET_OPERATORS['regex'] = NET_OPERATORS['iregex']
NET_OPERATORS['net_contained'] = '<< %s'
NET_OPERATORS['net_contained_or_equal'] = '<<= %s'
NET_OPERATORS['net_contains'] = '>> %s'
NET_OPERATORS['net_contains_or_equals'] = '>>= %s'

NET_TEXT_OPERATORS = ['ILIKE %s', '~* %s']


class NetQuery(sql.Query):
    query_terms = sql.Query.query_terms.copy()
    query_terms.update(NET_OPERATORS)

    def add_filter(self, (filter_string, value), *args, **kwargs):
        # IP(...) == '' fails so make sure to force to string while we can
        if isinstance(value, IP):
            value = unicode(value)
        return super(NetQuery, self).add_filter(
            (filter_string, value), *args, **kwargs)


class NetWhere(sql.where.WhereNode):
    def make_atom(self, child, qn):
        table_alias, name, db_type, lookup_type, value_annot, params = child

        if db_type not in ['inet', 'cidr']:
            return super(NetWhere, self).make_atom(child, qn)

        if table_alias:
            field_sql = '%s.%s' % (qn(table_alias), qn(name))
        else:
            field_sql = qn(name)

        if NET_OPERATORS.get(lookup_type, '') in NET_TEXT_OPERATORS:
            if db_type == 'inet':
                field_sql  = 'HOST(%s)' % field_sql
            else:
                field_sql  = 'TEXT(%s)' % field_sql

        if isinstance(params, QueryWrapper):
            extra, params = params.data
        else:
            extra = ''

        if lookup_type in NET_OPERATORS:
            return (' '.join([field_sql, NET_OPERATORS[lookup_type], extra]), params)
        elif lookup_type == 'in':
            if not value_annot:
                raise sql.datastructures.EmptyResultSet
            if extra:
                return ('%s IN %s' % (field_sql, extra), params)
            return ('%s IN (%s)' % (field_sql, ', '.join(['%s'] * len(params))), params)
        elif lookup_type == 'range':
            return ('%s BETWEEN %%s and %%s' % field_sql, params)
        elif lookup_type == 'isnull':
            return ('%s IS %sNULL' % (field_sql, (not value_annot and 'NOT ' or '')), params)

        raise ValueError('Invalid lookup type "%s"' % lookup_type)


class NetManger(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        q = NetQuery(self.model, connection, NetWhere)
        return query.QuerySet(self.model, q)


class _NetAddressField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        super(_NetAddressField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = None

        if value is None:
            return value

        return IP(value)

    def get_db_prep_value(self, value):
        if value is None:
            return value

        return unicode(self.to_python(value))

    def get_db_prep_lookup(self, lookup_type, value):
        if value is None:
            return value

        if (lookup_type in NET_OPERATORS and
                NET_OPERATORS[lookup_type] not in NET_TEXT_OPERATORS):
            return [self.get_db_prep_value(value)]

        return super(_NetAddressField, self).get_db_prep_lookup(
            lookup_type, value)

    def formfield(self, **kwargs):
        defaults = {'form_class': NetAddressFormField}
        defaults.update(kwargs)
        return super(_NetAddressField, self).formfield(**defaults)


class InetAddressField(_NetAddressField):
    description = "PostgreSQL INET field"
    max_length = 39
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'inet'


class CidrAddressField(_NetAddressField):
    description = "PostgreSQL CIDR field"
    max_length = 43
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'cidr'


class MACAddressField(models.Field):
    description = "PostgreSQL MACADDR field"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'macaddr'

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)


# ---- TESTS ----
class InetTestModel(models.Model):
    '''
    >>> cursor = connection.cursor()

    >>> InetTestModel(inet='10.0.0.1').save()

    >>> InetTestModel(inet=IP('10.0.0.1')).save()

    >>> InetTestModel(inet='').save()
    Traceback (most recent call last):
        ...
    IntegrityError: null value in column "inet" violates not-null constraint
    <BLANKLINE>

    >>> cursor.execute('ROLLBACK')

    >>> InetTestModel(inet='az').save()
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'az'

    >>> InetTestModel(inet=None).save()
    Traceback (most recent call last):
        ...
    IntegrityError: null value in column "inet" violates not-null constraint
    <BLANKLINE>

    >>> cursor.execute('ROLLBACK')

    >>> InetTestModel().save()
    Traceback (most recent call last):
        ...
    IntegrityError: null value in column "inet" violates not-null constraint
    <BLANKLINE>

    >>> cursor.execute('ROLLBACK')

    >>> InetTestModel.objects.filter(inet='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" = %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__exact='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" = %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__iexact='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" = %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contains='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" >> %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__in=['10.0.0.1', '10.0.0.2']).query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" IN (%s, %s)', (u'10.0.0.1', u'10.0.0.2'))

    >>> InetTestModel.objects.filter(inet__gt='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" > %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__gte='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" >= %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__lt='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" < %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__lte='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" <= %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__startswith='10.').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__istartswith='10.').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__endswith='.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__iendswith='.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ILIKE %s ', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__range=('10.0.0.1', '10.0.0.10')).query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" BETWEEN %s and %s', (u'10.0.0.1', u'10.0.0.10'))

    >>> InetTestModel.objects.filter(inet__year=1).query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "year"

    >>> InetTestModel.objects.filter(inet__month=1).query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "month"

    >>> InetTestModel.objects.filter(inet__day=1).query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "day"

    >>> InetTestModel.objects.filter(inet__isnull=True).query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" IS NULL', ())

    >>> InetTestModel.objects.filter(inet__isnull=False).query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" IS NOT NULL', ())

    >>> InetTestModel.objects.filter(inet__search='10').query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "search"

    >>> InetTestModel.objects.filter(inet__regex=u'10').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ~* %s ', (u'10',))

    >>> InetTestModel.objects.filter(inet__iregex=u'10').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE HOST("inet"."inet") ~* %s ', (u'10',))

    >>> InetTestModel.objects.filter(inet__net_contains_or_equals='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" >>= %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contained='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" << %s ', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contained_or_equal='10.0.0.1').query.as_sql()
    ('SELECT "inet"."id", "inet"."inet" FROM "inet" WHERE "inet"."inet" <<= %s ', (u'10.0.0.1',))
    '''

    inet = InetAddressField()
    objects = NetManger()

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
    objects = NetManger()

    class Meta:
        db_table = 'nullinet'

class CidrTestModel(models.Model):
    '''
    >>> CidrTestModel.objects.filter(cidr='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" = %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__exact='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" = %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__iexact='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" = %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__net_contains='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" >> %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__in=['10.0.0.1', '10.0.0.2']).query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" IN (%s, %s)', (u'10.0.0.1', u'10.0.0.2'))

    >>> CidrTestModel.objects.filter(cidr__gt='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" > %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__gte='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" >= %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__lt='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" < %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__lte='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" <= %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__startswith='10.').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'10.%',))

    >>> CidrTestModel.objects.filter(cidr__istartswith='10.').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'10.%',))

    >>> CidrTestModel.objects.filter(cidr__endswith='.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'%.1',))

    >>> CidrTestModel.objects.filter(cidr__iendswith='.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ILIKE %s ', (u'%.1',))

    >>> CidrTestModel.objects.filter(cidr__range=('10.0.0.1', '10.0.0.10')).query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" BETWEEN %s and %s', (u'10.0.0.1', u'10.0.0.10'))

    >>> CidrTestModel.objects.filter(cidr__year=1).query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "year"

    >>> CidrTestModel.objects.filter(cidr__month=1).query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "month"

    >>> CidrTestModel.objects.filter(cidr__day=1).query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "day"

    >>> CidrTestModel.objects.filter(cidr__isnull=True).query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" IS NULL', ())

    >>> CidrTestModel.objects.filter(cidr__isnull=False).query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" IS NOT NULL', ())

    >>> CidrTestModel.objects.filter(cidr__search='10').query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "search"

    >>> CidrTestModel.objects.filter(cidr__regex=u'10').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ~* %s ', (u'10',))

    >>> CidrTestModel.objects.filter(cidr__iregex=u'10').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE TEXT("cidr"."cidr") ~* %s ', (u'10',))

    >>> CidrTestModel.objects.filter(cidr__net_contains_or_equals='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" >>= %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__net_contained='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" << %s ', (u'10.0.0.1',))

    >>> CidrTestModel.objects.filter(cidr__net_contained_or_equal='10.0.0.1').query.as_sql()
    ('SELECT "cidr"."id", "cidr"."cidr" FROM "cidr" WHERE "cidr"."cidr" <<= %s ', (u'10.0.0.1',))
    '''

    cidr = CidrAddressField()
    objects = NetManger()

    class Meta:
        db_table = 'cidr'

class MACTestModel(models.Model):
    mac = MACAddressField(null=True)
    objects = NetManger()

    class Meta:
        db_table = 'mac'
