from IPy import IP

from django.db import models, connection, DEFAULT_DB_ALIAS

from netfields import *

class InetTestModel(models.Model):
    field = InetAddressField()
    objects = NetManager()

    class Meta:
        db_table = 'inet'

class NullInetTestModel(models.Model):
    field = InetAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'nullinet'

class CidrTestModel(models.Model):
    field = CidrAddressField()
    objects = NetManager()

    class Meta:
        db_table = 'cidr'

class NullCidrTestModel(models.Model):
    field = CidrAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'nullcidr'

class MACTestModel(models.Model):
    mac = MACAddressField(null=True)
    objects = NetManager()

    class Meta:
        db_table = 'mac'

