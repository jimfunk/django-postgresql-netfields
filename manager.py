from IPy import IP

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy
from django.db import models, connection
from django.db.models import sql, query

NET_OPERATORS = {
    'lt': '<',
    'lte': '<=',
    'exact': '=',
    'iexact': '=',
    'gte': '>=',
    'gt': '>',
    'contains': "ILIKE",
    'startswith': "ILIKE",
    'endswith': "ILIKE",
    'regex': '~*',
    'icontains': "ILIKE",
    'istartswith': "ILIKE",
    'iendswith': "ILIKE",
    'iregex': '~*',
    'net_contained': '<<',
    'net_contained_or_equal': '<<=',
    'net_contains': '>>',
    'net_contains_or_equals': '>>=',
}

NET_TEXT_LOOKUPS = set([
    'contains',
    'startswith',
    'endswith',
    'regex',
    'icontains',
    'istartswith',
    'iendswith',
    'iregex',
])

# FIXME test with .extra() and QueryWrapper

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
        if table_alias:
            field_sql = '%s.%s' % (qn(table_alias), qn(name))
        else:
            field_sql = qn(name)

        if db_type not in ['inet', 'cidr']:
            return super(NetWhere, self).make_atom(child, qn)

        if lookup_type in NET_TEXT_LOOKUPS:
            field_sql  = 'HOST(%s)' % field_sql

        if lookup_type in NET_OPERATORS:
            return ('%s %s %%s' % (field_sql, NET_OPERATORS[lookup_type]), params)
        elif lookup_type == 'in':
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

# FIXME formfields etc?
# - regexp field for mac
# - IP try catch for ip and cidr

class _NetAddressField(models.Field):
    # FIXME init empty object
    # FIXME null and blank handling needs to be done right.
    def to_python(self, value):
        if value is None:
            return value

        try:
            return IP(value)
        except ValueError, e:
            raise ValidationError(e)

    def get_db_prep_value(self, value):
        # FIXME does this need to respect null and blank?
        # FIXME does not handle __in
        if value is None:
            return value

        return unicode(self.to_python(value))

    def get_db_prep_lookup(self, lookup_type, value):
        if value is None:
            return value

        if lookup_type in NET_OPERATORS and lookup_type not in NET_TEXT_LOOKUPS:
            return [self.get_db_prep_value(value)]

        return super(_NetAddressField, self).get_db_prep_lookup(
            lookup_type, value)

class InetAddressField(_NetAddressField):
    description = "PostgreSQL INET field"
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'inet'

class CidrAddressField(_NetAddressField):
    description = "PostgreSQL CIDR field"
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'cidr'

class MACAddressField(models.Field):
    # FIXME does this need proper validation?
    description = "PostgreSQL MACADDR field"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'macaddr'

class InetTestModel(models.Model):
    '''
    >>> InetTestModel.objects.filter(inet='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" = %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__exact='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" = %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__iexact='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" = %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contains='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" >> %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__in=['10.0.0.1', '10.0.0.2']).query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" IN (%s, %s)', (u'10.0.0.1', u'10.0.0.2'))

    >>> InetTestModel.objects.filter(inet__gt='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" > %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__gte='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" >= %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__lt='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" < %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__lte='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" <= %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__startswith='10.').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ILIKE %s', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__istartswith='10.').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ILIKE %s', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__endswith='.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ILIKE %s', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__iendswith='.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ILIKE %s', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__range=('10.0.0.1', '10.0.0.10')).query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" BETWEEN %s and %s', (u'10.0.0.1', u'10.0.0.10'))

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
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" IS NULL', ())

    >>> InetTestModel.objects.filter(inet__isnull=False).query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" IS NOT NULL', ())

    >>> InetTestModel.objects.filter(inet__search='10').query.as_sql()
    Traceback (most recent call last):
        ...
    ValueError: Invalid lookup type "search"

    >>> InetTestModel.objects.filter(inet__regex=u'10').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ~* %s', (u'10',))

    >>> InetTestModel.objects.filter(inet__iregex=u'10').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ~* %s', (u'10',))

    >>> InetTestModel.objects.filter(inet__net_contains_or_equals='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" >>= %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contained='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" << %s', (u'10.0.0.1',))

    >>> InetTestModel.objects.filter(inet__net_contained_or_equal='10.0.0.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE "foo_inettestmodel"."inet" <<= %s', (u'10.0.0.1',))
    '''

    inet = InetAddressField()
    objects = NetManger()

class CidrTestModel(models.Model):
    '''
    >>> CidrTestModel.objects.filter(cidr='10.0.0.1').query.as_sql()
    ('SELECT "foo_cidrtestmodel"."id", "foo_cidrtestmodel"."cidr" FROM "foo_cidrtestmodel" WHERE "foo_cidrtestmodel"."cidr" = %s', (u'10.0.0.1',))
    '''

    cidr = CidrAddressField()
    objects = NetManger()

class MACTestModel(models.Model):
    mac = MACAddressField(null=True)
    objects = NetManger()
