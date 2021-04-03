from django import VERSION

if VERSION[0] < 2:
    from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper
else:
    from django.db.backends.postgresql.base import DatabaseWrapper

if VERSION[0] <= 2:
    from django.utils.six import with_metaclass, text_type
else:
    from six import with_metaclass, text_type
