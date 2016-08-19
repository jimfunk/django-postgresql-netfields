import datetime
from ipaddress import _BaseNetwork

from django import VERSION
from django.db import models
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
from django.db.models import sql, query
from django.db.models.fields import DateTimeField

NET_OPERATORS = DatabaseWrapper.operators.copy()

for operator in ['contains', 'startswith', 'endswith']:
    NET_OPERATORS[operator] = 'ILIKE %s'
    NET_OPERATORS['i%s' % operator] = 'ILIKE %s'

NET_OPERATORS['iexact'] = NET_OPERATORS['exact']
NET_OPERATORS['regex'] = NET_OPERATORS['iregex']
NET_OPERATORS['net_contained'] = '<< %s'
NET_OPERATORS['net_contained_or_equal'] = '<<= %s'
NET_OPERATORS['net_contains'] = '>> %s'
NET_OPERATORS['net_contains_or_equals'] = '>>= %s'
NET_OPERATORS['net_overlaps'] = '&& %s'
NET_OPERATORS['max_prefixlen'] = '%s'
NET_OPERATORS['min_prefixlen'] = '%s'

NET_TEXT_OPERATORS = ['ILIKE %s', '~* %s']


class NetQuery(sql.Query):
    query_terms = sql.Query.query_terms.copy()
    query_terms.update(NET_OPERATORS)


if VERSION < (1, 9):
    # _prepare_data has been removed / deprecated in
    # https://github.com/django/django/commit/5008a4db440c8f7d108a6979b959025ffb5789ba
    class NetWhere(sql.where.WhereNode):
        def _prepare_data(self, data):
            """
            Special form of WhereNode._prepare_data() that does not automatically consume the
            __iter__ method of _BaseNetwork objects.  This is used in Django >= 1.6
            """
            if not isinstance(data, (list, tuple)):
                return data
            obj, lookup_type, value = data
            if not isinstance(value, _BaseNetwork) and hasattr(value, '__iter__') and hasattr(value, 'next'):
                # Consume any generators immediately, so that we can determine
                # emptiness and transform any non-empty values correctly.
                value = list(value)

            # The "value_annotation" parameter is used to pass auxilliary information
            # about the value(s) to the query construction. Specifically, datetime
            # and empty values need special handling. Other types could be used
            # here in the future (using Python types is suggested for consistency).
            if (isinstance(value, datetime.datetime)
                or (isinstance(obj.field, DateTimeField) and lookup_type != 'isnull')):
                value_annotation = datetime.datetime
            elif hasattr(value, 'value_annotation'):
                value_annotation = value.value_annotation
            else:
                value_annotation = bool(value)

            if hasattr(obj, "prepare"):
                value = obj.prepare(lookup_type, value)
            return (obj, lookup_type, value_annotation, value)
else:
    NetWhere = sql.where.WhereNode


class NetManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        q = NetQuery(self.model, NetWhere)
        return query.QuerySet(self.model, q)

    def filter(self, *args, **kwargs):
        for key, val in kwargs.items():
            if isinstance(val, _BaseNetwork):
                # Django will attempt to consume the _BaseNetwork iterator, which
                # will convert it to a list of every address in the network
                kwargs[key] = str(val)
        return super(NetManager, self).filter(*args, **kwargs)
