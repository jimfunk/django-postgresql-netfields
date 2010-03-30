from django.db.backends.postgresql_psycopg2.base import *
from django.db.backends.postgresql_psycopg2.base import DatabaseFeatures as PostgresqlDatabaseFeatures
from django.db.backends.postgresql_psycopg2.base import DatabaseOperations as PostgresqlDatabaseOperations
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as PostgresqlDatabaseWrapper       
            
class DatabaseFeatures(PostgresqlDatabaseFeatures):
    uses_custom_query_class = True                                                                         

class DatabaseOperations(PostgresqlDatabaseOperations):                                                    
    def field_cast_sql(self, db_type):
        return '%s'

    def query_class(self, DefaultQueryClass):
        from django.db.models.sql.where import WhereNode
        from django.db.models.sql.constants import QUERY_TERMS

        INET_TERMS = {}
        INET_TERMS['inet_lt'] = '<'
        INET_TERMS['inet_lte'] = '<='
        INET_TERMS['inet_exact'] = '='
        INET_TERMS['inet_gte'] = '>='
        INET_TERMS['inet_gt'] = '>'
        INET_TERMS['inet_not'] = '<>'
        INET_TERMS['inet_is_contained'] = '<<'
        INET_TERMS['inet_is_contained_or_equal'] = '<<='
        INET_TERMS['inet_contains'] = '>>'
        INET_TERMS['inet_contains'] = '>>='

        ALL_TERMS = QUERY_TERMS.copy()
        ALL_TERMS.update(INET_TERMS)

        class InetAwareWhereNode(WhereNode):
            def make_atom(self, child, qn):
                table_alias, name, db_type, lookup_type, value_annot, params = child

                if db_type != 'inet':
                    return super(InetAwareWhereNode, self).make_atom(child, qn)

                if lookup_type in INET_TERMS:
                    return ('%s.%s %s inet %%s' % (table_alias, name, INET_TERMS[lookup_type]), params)

                return super(InetAwareWhereNode, self).make_atom(child, qn)

        class InetAwareQueryClass(DefaultQueryClass):
            query_terms = ALL_TERMS

            def __init__(self, model, connection, where=InetAwareWhereNode):
                super(InetAwareQueryClass, self).__init__(model, connection, where)

        return InetAwareQueryClass

class DatabaseWrapper(PostgresqlDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
