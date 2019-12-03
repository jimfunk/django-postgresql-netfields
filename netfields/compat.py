from django import VERSION

if VERSION[0] <= 2:
    from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
    from django.utils.six import with_metaclass, text_type
else:
    from django.db.backends.postgresql.base import DatabaseWrapper
    from six import with_metaclass, text_type
