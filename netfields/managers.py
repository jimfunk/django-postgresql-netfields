from IPy import IP

from types import StringTypes
from django.db import models, connection
from django.db.models import sql, query
from django.db.models.query_utils import QueryWrapper

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
    def make_atom(self, child, qn , conn):
        if isinstance(child[0] , sql.where.Constraint):
            c = child[0]
            table_alias = c.alias
            name = c.col
            field = c.field
            lookup_type , value_annot , params = child[1:]
        else:
            table_alias, name, db_type, lookup_type, value_annot, params = child

        if field.db_type() not in ['inet', 'cidr']:
            return super(NetWhere, self).make_atom(child, qn , conn)

        if table_alias:
            field_sql = '%s.%s' % (qn(table_alias), qn(name))
        else:
            field_sql = qn(name)

        if NET_OPERATORS.get(lookup_type, '') in NET_TEXT_OPERATORS:
            if field.db_type() == 'inet':
                field_sql  = 'HOST(%s)' % field_sql
            else:
                field_sql  = 'TEXT(%s)' % field_sql

        if isinstance(params, QueryWrapper):
            extra, params = params.data
        else:
            extra = ''

        if type(params) in StringTypes:
            params = (params,)

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


class NetManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        q = NetQuery(self.model, NetWhere)
        return query.QuerySet(self.model, q)
