from django.contrib.postgres.fields import ArrayField
from django.db.models import Model, ForeignKey, CASCADE

from netfields import InetAddressField, CidrAddressField, MACAddressField, \
        NetManager
from netfields.address_families import IPV4_FAMILY, IPV6_FAMILY


class InetTestModel(Model):
    field = InetAddressField()
    objects = NetManager()

    class Meta:
        db_table = 'inet'


class NullInetTestModel(Model):
    field = InetAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'nullinet'


class UniqueInetTestModel(Model):
    field = InetAddressField(unique=True)
    objects = NetManager()

    class Meta:
        db_table = 'uniqueinet'


class NoPrefixInetTestModel(Model):
    field = InetAddressField(store_prefix_length=False)
    objects = NetManager()

    class Meta:
        db_table = 'noprefixinet'


class IPv4InetTestModel(Model):
    field = InetAddressField(address_family=IPV4_FAMILY)
    objects = NetManager()

    class Meta:
        db_table = 'ipv4inet'


class IPv6InetTestModel(Model):
    field = InetAddressField(address_family=IPV6_FAMILY)
    objects = NetManager()

    class Meta:
        db_table = 'ipv6inet'


class CidrTestModel(Model):
    field = CidrAddressField()
    objects = NetManager()

    class Meta:
        db_table = 'cidr'


class NullCidrTestModel(Model):
    field = CidrAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'nullcidr'


class UniqueCidrTestModel(Model):
    field = CidrAddressField(unique=True)
    objects = NetManager()

    class Meta:
        db_table = 'uniquecidr'


class IPv4CidrTestModel(Model):
    field = CidrAddressField(address_family=IPV4_FAMILY)
    objects = NetManager()

    class Meta:
        db_table = 'ipv4cidr'


class IPv6CidrTestModel(Model):
    field = CidrAddressField(address_family=IPV6_FAMILY)
    objects = NetManager()

    class Meta:
        db_table = 'ipv6cidr'


class MACTestModel(Model):
    field = MACAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'mac'


class InetArrayTestModel(Model):
    field = ArrayField(InetAddressField(), blank=True, null=True)

    class Meta:
        db_table = 'inetarray'


class CidrArrayTestModel(Model):
    field = ArrayField(CidrAddressField(), blank=True, null=True)

    class Meta:
        db_table = 'cidrarray'


class MACArrayTestModel(Model):
    field = ArrayField(MACAddressField(), blank=True, null=True)

    class Meta:
        db_table = 'macarray'


class AggregateTestModel(Model):
    network = CidrAddressField(blank=True, null=True, default=None)
    inet = InetAddressField(blank=True, null=True, default=None)


class AggregateTestChildModel(Model):
    parent = ForeignKey(
        'AggregateTestModel',
        related_name='children',
        on_delete=CASCADE,
    )
    network = CidrAddressField()
    inet = InetAddressField()
