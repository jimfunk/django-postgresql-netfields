from IPy import IP

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy
from django.db import models, connection
from django.db.models import sql, query

NET_TERMS = {
    'lt': '%s < %%s',
    'lte': '%s <= %%s',
    'exact': '%s = %%s',
    'gte': '%s >= %%s',
    'gt': '%s > %%s',
    'net_contained': '%s << %%s',
    'net_contained_or_equal': '%s <<= %%s',
    'net_contains': '%s >> %%s',
    'net_contains_or_equals': '%s >>= %%s',
}

NET_TERMS_MAPPING = {
    'iexact': 'exact',
    'icontains': 'contains',
    'istartswith': 'startswith',
    'iendswith': 'endswith',
    'iregex': 'regex',
}

class NetQuery(sql.Query):
    query_terms = sql.Query.query_terms.copy()
    query_terms.update(NET_TERMS)

    def add_filter(self, (filter_string, value), *args, **kwargs):
        # IP(...) == '' fails so make sure to force to string while we can
        if isinstance(value, IP):
            value = unicode(value)
        return super(NetQuery, self).add_filter(
            (filter_string, value), *args, **kwargs)

class NetWhere(sql.where.WhereNode):
    def make_atom(self, child, qn):
        table_alias, name, db_type, lookup_type, value_annot, params = child
        field_sql = '%s.%s' % (qn(table_alias), qn(name))

        if db_type not in ['inet', 'cidr']:
            return super(NetWhere, self).make_atom(child, qn)
        elif lookup_type in NET_TERMS_MAPPING:
            lookup_type = NET_TERMS_MAPPING[lookup_type]
            child = (table_alias, name, db_type, lookup_type, value_annot, params)
            return self.make_atom(child, qn)
        elif lookup_type in NET_TERMS:
            return (NET_TERMS[lookup_type] % field_sql, params)
        elif lookup_type == 'in':
            return ('%s IN (%s)' % (field_sql, ', '.join(['%s'] * len(params))), params)
        elif lookup_type == 'range':
            return ('%s BETWEEN %%s and %%s' % (field_sql), params)
        elif lookup_type == 'isnull':
            return ('%s IS %sNULL' % (field_sql, (not value_annot and 'NOT ' or '')), params)
        else:
            return super(NetWhere, self).make_atom(child, qn)

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

        if lookup_type in ['year', 'month', 'day']:
            raise ValueError('Invalid lookup type "%s"' % lookup_type)

        if lookup_type in NET_TERMS_MAPPING:
            return self.get_db_prep_lookup(
                NET_TERMS_MAPPING[lookup_type], value)

        if lookup_type in NET_TERMS:
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
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet")::text LIKE %s ', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__istartswith='10.').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet")::text LIKE %s ', (u'10.%',))

    >>> InetTestModel.objects.filter(inet__endswith='.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet")::text LIKE %s ', (u'%.1',))

    >>> InetTestModel.objects.filter(inet__iendswith='.1').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet")::text LIKE %s ', (u'%.1',))

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
    NotImplementedError: Full-text search is not implemented for this database backend

    >>> InetTestModel.objects.filter(inet__regex=u'10').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ~ %s ', (u'10',))

    >>> InetTestModel.objects.filter(inet__iregex=u'10').query.as_sql()
    ('SELECT "foo_inettestmodel"."id", "foo_inettestmodel"."inet" FROM "foo_inettestmodel" WHERE HOST("foo_inettestmodel"."inet") ~ %s ', (u'10',))

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
