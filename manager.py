from IPy import IP

from django.core.exceptions import ValidationError
from django.db import models, connection
from django.db.models import sql, query

NET_TERMS = {
    'inet_lt': '<',
    'inet_lte': '<=',
    'inet_exact': '=',
    'inet_gte': '>=',
    'inet_gt': '>',
    'inet_not': '<>',
    'inet_is_contained': '<<',
    'inet_is_contained_or_equal': '<<=',
    'inet_contains': '>>',
    'inet_contains': '>>=',
}

class NetQuery(sql.Query):
    query_terms = sql.Query.query_terms.copy()
    query_terms.update(NET_TERMS)

    def add_filter(self, (filter_string, value), *args, **kwargs):
        if isinstance(value, IP):
            value = unicode(value)
        return super(NetQuery, self).add_filter((filter_string, value), *args, **kwargs)

class NetWhere(sql.where.WhereNode):
    def make_atom(self, child, qn):
        table_alias, name, db_type, lookup_type, value_annot, params = child

        if db_type in ['cidr', 'inet'] and lookup_type in NET_TERMS:
            return ('%s.%s %s inet %%s' % (table_alias, name, NET_TERMS[lookup_type]), params)

        return super(NetWhere, self).make_atom(child, qn)

class NetManger(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        q = NetQuery(self.model, connection, NetWhere)
        return query.QuerySet(self.model, q)

class _NetAddressField(models.Field):
    def to_python(self, value):
        if not value:
            return None

        try:
            return IP(value)
        except ValueError, e:
            raise ValidationError(e)

    def get_db_prep_value(self, value):
        return unicode(self.to_python(value))

    def get_db_prep_lookup(self, lookup_type, value):
        value = unicode(value)

        if lookup_type in INET_TERMS:
            return [value]

        return super(_NetAddressField, self).get_db_prep_lookup(lookup_type, value)

class InetAddressField(_NetAddressField):
    description = "Postgresql inet field"
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'inet'

class CidrAddressField(_NetAddressField):
    description = "Postgresql cidr field"
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return 'cidr'

class MACAddressField(models.Field):
    description = "Postgresql macaddr field"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'macaddr'

class Foo(models.Model):
    inet = InetAddressField()
    test = CidrAddressField()
    mac = MACAddressField()

    objects = NetManger()