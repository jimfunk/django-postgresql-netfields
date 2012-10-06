from IPy import IP

from django.db import models, connection
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
from django.db.models import sql, query
from django.db.models.query_utils import QueryWrapper

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

NET_TEXT_OPERATORS = ['ILIKE %s', '~* %s']


class NetQuery(sql.Query):
    query_terms = sql.Query.query_terms.copy()
    query_terms.update(NET_OPERATORS)


class NetWhere(sql.where.WhereNode):
    def make_atom(self, child, qn, conn):
        lvalue, lookup_type, value_annot, params_or_value = child

        if hasattr(lvalue, 'process'):
            try:
                lvalue, params = lvalue.process(lookup_type, params_or_value,
                                                connection)
            except sql.where.EmptyShortCircuit:
                raise query.EmptyResultSet
        else:
            return super(NetWhere, self).make_atom(child, qn, conn)

        table_alias, name, db_type = lvalue

        if db_type not in ['inet', 'cidr']:
            return super(NetWhere, self).make_atom(child, qn, conn)

        if table_alias:
            field_sql = '%s.%s' % (qn(table_alias), qn(name))
        else:
            field_sql = qn(name)

        if NET_OPERATORS.get(lookup_type, '') in NET_TEXT_OPERATORS:
            if db_type == 'inet':
                field_sql = 'HOST(%s)' % field_sql
            else:
                field_sql = 'TEXT(%s)' % field_sql

        if isinstance(params, QueryWrapper):
            extra, params = params.data
        else:
            extra = ''

        if isinstance(params, basestring):
            params = (params,)

        if lookup_type in NET_OPERATORS:
            return (' '.join([field_sql, NET_OPERATORS[lookup_type], extra]),
                    params)
        elif lookup_type == 'in':
            if not value_annot:
                raise sql.datastructures.EmptyResultSet
            if extra:
                return ('%s IN %s' % (field_sql, extra), params)
            return ('%s IN (%s)' % (field_sql, ', '.join(['%s'] *
                    len(params))), params)
        elif lookup_type == 'range':
            return ('%s BETWEEN %%s and %%s' % field_sql, params)
        elif lookup_type == 'isnull':
            return ('%s IS %sNULL' % (field_sql, (not value_annot and 'NOT ' or
                    '')), params)

        raise ValueError('Invalid lookup type "%s"' % lookup_type)


class NetManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        q = NetQuery(self.model, NetWhere)
        return query.QuerySet(self.model, q)
