from IPy import IP

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy
from django.db import models, connection
from django.db.models import sql, query

# FIXME decide if we should use custom lookup names instead of overrides.
# FIXME decide if other "standard" lookups should be disabled
# FIXME test "standard" lookups
# FIXME decide if HOST() cast should be ignored

NET_TERMS = {
    'lt': '<',
    'lte': '<=',
    'exact': '=',
    'gte': '>=',
    'gt': '>',
    'contained': '<<',
    'contained_or_equal': '<<=',
    'contains': '>>',
    'contains_or_equals': '>>=',
}

class NetQuery(sql.Query):
    query_terms = sql.Query.query_terms.copy()
    query_terms.update(NET_TERMS)

    def add_filter(self, (filter_string, value), *args, **kwargs):
        # IP(...) == '' fails so make sure to force to string while we can
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

# FIXME formfields etc?
# - regexp field for mac
# - IP try catch for ip and cidr

class _NetAddressField(models.Field):
    # FIXME null and blank handling needs to be done right.
    def to_python(self, value):
        if value is None:
            if self.null:
                return value
            else:
                raise ValidationError(
                    ugettext_lazy("This field cannot be null."))

        try:
            return IP(value)
        except ValueError, e:
            raise ValidationError(e)

    def get_db_prep_value(self, value):
        # FIXME does this need to respect null and blank?
        if value is None:
            return value
        return unicode(self.to_python(value))

    def get_db_prep_lookup(self, lookup_type, value):
        if value is None:
            return value

        value = unicode(value)

        if lookup_type in NET_TERMS:
            return [value]

        return super(_NetAddressField, self).get_db_prep_lookup(lookup_type, value)

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
    description = "PostgreSQL MACADDR field"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    # FIXME does this need proper validation?

    def db_type(self):
        return 'macaddr'

class Foo(models.Model):
    inet = InetAddressField(null=True)
    cidr = CidrAddressField(null=True)
    mac = MACAddressField(null=True)
    text = models.CharField(max_length=10, blank=True, null=True)

    objects = NetManger()