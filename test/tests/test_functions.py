from __future__ import unicode_literals
from django import VERSION
from ipaddress import ip_interface, ip_network
from netaddr import EUI

from django.db.models import Case, F, When
from django.test import TestCase
from unittest import skipIf

from netfields.functions import (
    Abbrev,
    Broadcast,
    Family,
    Host,
    Hostmask,
    Masklen,
    Netmask,
    Network,
    SetMasklen,
    AsText,
    IsSameFamily,
    Merge,
    Trunc
)

from test.models import (
    AggregateTestChildModel,
    AggregateTestModel,
    CidrTestModel,
    InetTestModel,
    MACTestModel
)


class TestInetFieldFunctions(TestCase):
    def setUp(self):
        InetTestModel.objects.create(field='10.1.0.1/16')
        InetTestModel.objects.create(field='2001:4f8:3:ba::1/64')

    def test_abbreviate(self):
        qs = InetTestModel.objects.annotate(abbrv=Abbrev(F('field')))
        self.assertEqual(qs[0].abbrv, '10.1.0.1/16')
        self.assertEqual(qs[1].abbrv, '2001:4f8:3:ba::1/64')

    def test_broadcast(self):
        qs = InetTestModel.objects.annotate(broadcast=Broadcast(F('field')))
        self.assertEqual(qs[0].broadcast, ip_interface('10.1.255.255/16'))
        self.assertEqual(qs[1].broadcast, ip_interface('2001:4f8:3:ba:ffff:ffff:ffff:ffff/64'))

    def test_family(self):
        qs = InetTestModel.objects.annotate(family=Family(F('field')))
        self.assertEqual(qs[0].family, 4)
        self.assertEqual(qs[1].family, 6)

    def test_host(self):
        qs = InetTestModel.objects.annotate(host=Host(F('field')))
        self.assertEqual(qs[0].host, '10.1.0.1')
        self.assertEqual(qs[1].host, '2001:4f8:3:ba::1')

    def test_hostmask(self):
        qs = InetTestModel.objects.annotate(hostmask=Hostmask(F('field')))
        self.assertEqual(qs[0].hostmask, ip_interface('0.0.255.255'))
        self.assertEqual(qs[1].hostmask, ip_interface('::ffff:ffff:ffff:ffff'))

    def test_masklen(self):
        qs = InetTestModel.objects.annotate(masklen=Masklen(F('field')))
        self.assertEqual(qs[0].masklen, 16)
        self.assertEqual(qs[1].masklen, 64)

    def test_netmask(self):
        qs = InetTestModel.objects.annotate(netmask=Netmask(F('field')))
        self.assertEqual(qs[0].netmask, ip_interface('255.255.0.0'))
        self.assertEqual(qs[1].netmask, ip_interface('ffff:ffff:ffff:ffff::'))

    def test_network(self):
        qs = InetTestModel.objects.annotate(network=Network(F('field')))
        self.assertEqual(qs[0].network, ip_network('10.1.0.0/16'))
        self.assertEqual(qs[1].network, ip_network('2001:4f8:3:ba::/64'))

    def test_set_masklen(self):
        (
            InetTestModel.objects
            .annotate(family=Family(F('field')))
            .update(
                field=Case(
                    When(family=4, then=SetMasklen(F('field'), 24)),
                    When(family=6, then=SetMasklen(F('field'), 120))
                )
            )
        )
        qs = InetTestModel.objects.all()
        self.assertEqual(qs[0].field, ip_interface('10.1.0.1/24'))
        self.assertEqual(qs[1].field, ip_interface('2001:4f8:3:ba::1/120'))
 
    def test_as_text(self):
        qs = InetTestModel.objects.annotate(text=AsText(F('field')))
        self.assertEqual(qs[0].text, '10.1.0.1/16')
        self.assertEqual(qs[1].text, '2001:4f8:3:ba::1/64')

    def test_is_same_family(self):
        parent = AggregateTestModel.objects.create(inet='0.0.0.0/0')
        AggregateTestChildModel.objects.create(
            parent=parent, inet='10.1.0.1/16', network='10.1.0.0/16'
        )
        AggregateTestChildModel.objects.create(
            parent=parent, inet='2001:4f8:3:ba::1/64', network='2001:4f8:3:ba::/64'
        )

        qs = (
            AggregateTestChildModel.objects.annotate(
                is_same_family=IsSameFamily(F('inet'), F('parent__inet'))
            )
            .order_by('id')
        )
        self.assertEqual(qs[0].is_same_family, True)
        self.assertEqual(qs[1].is_same_family, False)

    def test_merge(self):
        parent = AggregateTestModel.objects.create(inet='10.0.0.0/24')
        AggregateTestChildModel.objects.create(
            parent=parent, inet='10.0.1.0/24', network='10.0.0.0/23'
        )

        parent = AggregateTestModel.objects.create(inet='2001:4f8:3:ba::/64')
        AggregateTestChildModel.objects.create(
            parent=parent, inet='2001:4f8:3:bb::/64', network='2001:4f8:3:ba::/63'
        )

        qs = (
            AggregateTestChildModel.objects.annotate(
                merged=Merge(F('inet'), F('parent__inet'))
            )
        )
        self.assertEqual(qs[0].merged, qs[0].network)
        self.assertEqual(qs[1].merged, qs[1].network)


class TestCidrFieldFunctions(TestCase):
    def setUp(self):
        CidrTestModel.objects.create(field='10.1.0.0/16')
        CidrTestModel.objects.create(field='2001:4f8:3:ba::/64')

    def test_abbreviate(self):
        qs = CidrTestModel.objects.annotate(abbrv=Abbrev(F('field')))
        self.assertEqual(qs[0].abbrv, '10.1/16')
        self.assertEqual(qs[1].abbrv, '2001:4f8:3:ba/64')

    def test_broadcast(self):
        qs = CidrTestModel.objects.annotate(broadcast=Broadcast(F('field')))
        self.assertEqual(qs[0].broadcast, ip_interface('10.1.255.255/16'))
        self.assertEqual(qs[1].broadcast, ip_interface('2001:4f8:3:ba:ffff:ffff:ffff:ffff/64'))

    def test_family(self):
        qs = CidrTestModel.objects.annotate(family=Family(F('field')))
        self.assertEqual(qs[0].family, 4)
        self.assertEqual(qs[1].family, 6)

    def test_host(self):
        qs = CidrTestModel.objects.annotate(host=Host(F('field')))
        self.assertEqual(qs[0].host, '10.1.0.0')
        self.assertEqual(qs[1].host, '2001:4f8:3:ba::')

    def test_hostmask(self):
        qs = CidrTestModel.objects.annotate(hostmask=Hostmask(F('field')))
        self.assertEqual(qs[0].hostmask, ip_interface('0.0.255.255'))
        self.assertEqual(qs[1].hostmask, ip_interface('::ffff:ffff:ffff:ffff'))

    def test_masklen(self):
        qs = CidrTestModel.objects.annotate(masklen=Masklen(F('field')))
        self.assertEqual(qs[0].masklen, 16)
        self.assertEqual(qs[1].masklen, 64)

    def test_netmask(self):
        qs = CidrTestModel.objects.annotate(netmask=Netmask(F('field')))
        self.assertEqual(qs[0].netmask, ip_interface('255.255.0.0'))
        self.assertEqual(qs[1].netmask, ip_interface('ffff:ffff:ffff:ffff::'))

    def test_network(self):
        qs = CidrTestModel.objects.annotate(network=Network(F('field')))
        self.assertEqual(qs[0].network, ip_network('10.1.0.0/16'))
        self.assertEqual(qs[1].network, ip_network('2001:4f8:3:ba::/64'))

    def test_set_masklen(self):
        (
            CidrTestModel.objects
            .annotate(family=Family(F('field')))
            .update(
                field=Case(
                    When(family=4, then=SetMasklen(F('field'), 24)),
                    When(family=6, then=SetMasklen(F('field'), 120))
                )
            )
        )
        qs = CidrTestModel.objects.all()
        self.assertEqual(qs[0].field, ip_network('10.1.0.0/24'))
        self.assertEqual(qs[1].field, ip_network('2001:4f8:3:ba::/120'))

    def test_as_text(self):
        qs = CidrTestModel.objects.annotate(text=AsText(F('field')))
        self.assertEqual(qs[0].text, '10.1.0.0/16')
        self.assertEqual(qs[1].text, '2001:4f8:3:ba::/64')

    def test_is_same_family(self):
        parent = AggregateTestModel.objects.create(network='0.0.0.0/0')
        AggregateTestChildModel.objects.create(
            parent=parent, inet= '10.1.0.1/16', network='10.1.0.0/16'
        )
        AggregateTestChildModel.objects.create(
            parent=parent, inet='2001:4f8:3:ba::1/64', network='2001:4f8:3:ba::/64'
        )

        qs = (
            AggregateTestChildModel.objects.annotate(
                is_same_family=IsSameFamily(F('network'), F('parent__network'))
            )
            .order_by('id')
        )
        self.assertEqual(qs[0].is_same_family, True)
        self.assertEqual(qs[1].is_same_family, False)

    def test_merge(self):
        parent = AggregateTestModel.objects.create(network='10.0.0.0/24')
        AggregateTestChildModel.objects.create(
            parent=parent, inet='10.0.1.0/24', network='10.0.0.0/23'
        )

        parent = AggregateTestModel.objects.create(network='2001:4f8:3:ba::/64')
        AggregateTestChildModel.objects.create(
            parent=parent, inet='2001:4f8:3:bb::/64', network='2001:4f8:3:ba::/63'
        )

        qs = (
            AggregateTestChildModel.objects.annotate(
                merged=Merge(F('network'), F('parent__network'))
            )
        )
        self.assertEqual(qs[0].merged, qs[0].network)
        self.assertEqual(qs[1].merged, qs[1].network)

    @skipIf(VERSION < (2, 0), 'Django unable to resolve type of num_ips to be IntegerField until 2.0.')
    def test_read_me_example(self):
        qs = (
            CidrTestModel.objects.annotate(
                family=Family(F('field')),
                num_ips=2 ** (32 - Masklen(F('field'))),
            )
            .filter(family=4)
        )
        self.assertEqual(qs[0].num_ips, 65536)


class TestMacFieldFunctions(TestCase):
    def setUp(self):
        MACTestModel.objects.create(field='aa:bb:cc:dd:ee:ff')

    def test_trunc(self):
        qs = MACTestModel.objects.annotate(trunc=Trunc(F('field')))
        self.assertEqual(qs[0].trunc, EUI('aa:bb:cc:00:00:00'))
