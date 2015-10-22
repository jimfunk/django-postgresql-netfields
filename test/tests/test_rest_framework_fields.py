from __future__ import absolute_import

from rest_framework import serializers

import unittest2 as unittest
from netfields import rest_framework as fields


class FieldsTestCase(unittest.TestCase):
    def test_validation_inet_field(self):

        class TestSerializer(serializers.Serializer):
            ip = fields.InetAddressField()

        serializer = TestSerializer(data={'ip': '10.0.0.'})
        with self.assertRaises(serializers.ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(e.exception.detail['ip'], ['Invalid IP address.'])

    def test_validation_cidr_field(self):

        class TestSerializer(serializers.Serializer):
            cidr = fields.CidrAddressField()

        serializer = TestSerializer(data={'cidr': '10.0.0.'})
        with self.assertRaises(serializers.ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(e.exception.detail['cidr'], ['Invalid CIDR address.'])

    def test_validation_mac_field(self):

        class TestSerializer(serializers.Serializer):
            mac = fields.MACAddressField()

        serializer = TestSerializer(data={'mac': 'de:'})
        with self.assertRaises(serializers.ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(e.exception.detail['mac'], ['Invalid MAC address.'])

    def test_validation_additional_validators(self):
        def validate(value):
            raise serializers.ValidationError('Invalid.')

        class TestSerializer(serializers.Serializer):
            ip = fields.InetAddressField(validators=[validate])

        serializer = TestSerializer(data={'ip': 'de:'})
        with self.assertRaises(serializers.ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertItemsEqual(e.exception.detail['ip'], ['Invalid IP address.', 'Invalid.'])
