from django.core.exceptions import FieldError
from django.db.models import Lookup, Transform, IntegerField
from django.db.models.lookups import BuiltinLookup
from django.db.models.lookups import EndsWith as BaseEndsWith
from django.db.models.lookups import IEndsWith as BaseIEndsWith
from django.db.models.lookups import StartsWith as BaseStartsWith
from django.db.models.lookups import IStartsWith as BaseIStartsWith
from netfields.fields import InetAddressField, CidrAddressField


class InvalidLookup(BuiltinLookup):
    """
    Emulate Django 1.9 error for unsupported lookups
    """
    def as_sql(self, qn, connection):
        raise FieldError("Unsupported lookup '%s'" % self.lookup_name)


class InvalidSearchLookup(BuiltinLookup):
    """
    Emulate Django 1.9 error for unsupported search lookup
    """
    lookup_name = 'search'

    def as_sql(self, qn, connection):
        raise NotImplementedError("Full-text search is not implemented for this database backend")


class NetFieldDecoratorMixin(object):
    def process_lhs(self, qn, connection, lhs=None):
        lhs = lhs or self.lhs
        lhs_string, lhs_params = qn.compile(lhs)
        if isinstance(lhs.source if hasattr(lhs, 'source') else lhs.output_field, InetAddressField):
            lhs_string = 'HOST(%s)' % lhs_string
        elif isinstance(lhs.source if hasattr(lhs, 'source') else lhs.output_field, CidrAddressField):
            lhs_string = 'TEXT(%s)' % lhs_string
        return lhs_string, lhs_params


class EndsWith(NetFieldDecoratorMixin, BaseEndsWith):
    lookup_name = 'endswith'


class IEndsWith(NetFieldDecoratorMixin, BaseIEndsWith):
    lookup_name = 'iendswith'


class StartsWith(NetFieldDecoratorMixin, BaseStartsWith):
    lookup_name = 'startswith'


class IStartsWith(NetFieldDecoratorMixin, BaseIStartsWith):
    lookup_name = 'istartswith'


class Regex(NetFieldDecoratorMixin, BuiltinLookup):
    lookup_name = 'regex'


class IRegex(NetFieldDecoratorMixin, BuiltinLookup):
    lookup_name = 'iregex'


class NetContains(Lookup):
    lookup_name = 'net_contains'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s >> %s' % (lhs, rhs), params


class NetContained(Lookup):
    lookup_name = 'net_contained'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s << %s' % (lhs, rhs), params


class NetContainsOrEquals(Lookup):
    lookup_name = 'net_contains_or_equals'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s >>= %s' % (lhs, rhs), params

class NetContainedOrEqual(Lookup):
    lookup_name = 'net_contained_or_equal'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <<= %s' % (lhs, rhs), params


class Family(Transform):
    lookup_name = 'family'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "family(%s)" % lhs, params

    @property
    def output_field(self):
        return IntegerField()
