from django.db.models import Model

from netfields import InetAddressField, CidrAddressField, MACAddressField, \
        NetManager


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


class MACTestModel(Model):
    mac = MACAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'mac'
