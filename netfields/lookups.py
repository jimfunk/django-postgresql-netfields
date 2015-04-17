from django.db.models import Lookup
from django.db.models.lookups import BuiltinLookup
from netfields.fields import InetAddressField, CidrAddressField


class InvalidLookup(BuiltinLookup):
    def as_sql(self, qn, connection):
        raise ValueError('Invalid lookup type "%s"' % self.lookup_name)


class NetFieldDecoratorMixin(object):
    def process_lhs(self, qn, connection, lhs=None):
        lhs = lhs or self.lhs
        lhs_string, lhs_params = qn.compile(lhs)
        if isinstance(lhs.source if hasattr(lhs, 'source') else lhs.output_field, InetAddressField):
            lhs_string = 'HOST(%s)' % lhs_string
        elif isinstance(lhs.source if hasattr(lhs, 'source') else lhs.output_field, CidrAddressField):
            lhs_string = 'TEXT(%s)' % lhs_string
        return lhs_string, lhs_params


class EndsWith(NetFieldDecoratorMixin, BuiltinLookup):
    lookup_name = 'endswith'


class IEndsWith(NetFieldDecoratorMixin, BuiltinLookup):
    lookup_name = 'iendswith'


class StartsWith(NetFieldDecoratorMixin, BuiltinLookup):
    lookup_name = 'startswith'


class IStartsWith(NetFieldDecoratorMixin, BuiltinLookup):
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
