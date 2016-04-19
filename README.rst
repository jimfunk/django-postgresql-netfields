Django PostgreSQL Netfields
===========================

.. image:: https://secure.travis-ci.org/jimfunk/django-postgresql-netfields.png

This project is an attempt at making proper PostgreSQL net related fields for
Django. In Django pre 1.4 the built in ``IPAddressField`` does not support IPv6
and uses an inefficient ``HOST()`` cast in all lookups. As of 1.4 you can use
``GenericIPAddressField`` for IPv6, but the casting problem remains.

In addition to the basic ``IPAddressField`` replacement a ``CIDR`` and
a ``MACADDR`` field have been added. This library also provides a manager that
allows for advanced IP based lookup directly in the ORM.

In Python, the values of the IP address fields are represented as types from
the ipaddress_ module. In Python 2.x, a backport_ is used. The MAC address
field is represented as an EUI type from the netaddr_ module.

.. _ipaddress: https://docs.python.org/3/library/ipaddress.html
.. _backport: https://pypi.python.org/pypi/ipaddress/
.. _netaddr: http://pythonhosted.org/netaddr/

Dependencies
------------

Current version of code is targeting Django >= 1.8 support, as this relies
heavily on ORM internals and supporting multiple versions is especially tricky.

Getting started
---------------

Make sure ``netfields`` is in your ``PYTHONPATH`` and in ``INSTALLED_APPS``.

``InetAddressField`` will store values in PostgreSQL as type ``INET``. In
Python, the value will be represented as an ``ipaddress.ip_interface`` object
representing an IP address and netmask/prefix length pair unless the
``store_prefix_length`` argument is set to `False``, in which case the value
will be represented as an ``ipaddress.ip_address`` object.

 from netfields import InetAddressField, NetManager

 class Example(models.Model):
     inet = InetAddressField()
     # ...

     objects = NetManager()

``CidrAddressField`` will store values in PostgreSQL as type ``CIDR``. In
Python, the value will be represented as an ``ipaddress.ip_network`` object.

 from netfields import CidrAddressField, NetManager

 class Example(models.Model):
     inet = CidrAddressField()
     # ...

     objects = NetManager()

``MACAddressField`` will store values in PostgreSQL as type ``MACADDR``. In
Python, the value will be represented as a ``netaddr.EUI`` object. Note that
the default text representation of EUI objects is not the same as that of the
``netaddr`` module. It is represented in a format that is more commonly used
in network utilities and by network administrators (``00:11:22:aa:bb:cc``).

 from netfields import MACAddressField, NetManager

 class Example(models.Model):
     inet = MACAddressField()
     # ...

For ``InetAddressField`` and ``CidrAddressField``, ``NetManager`` is required
for the extra lookups to be available. Lookups for ``INET`` and ``CIDR``
database types will be handled differently than when running vanilla Django.
All lookups are case-insensitive and text based lookups are avoided whenever
possible. In addition to Django's default lookup types the following have been
added:

``__net_contained``
    is contained within the given network

``__net_contained_or_equal``
    is contained within or equal to the given network

``__net_contains``
    contains the given address

``__net_contains_or_equals``
    contains or is equal to the given address/network

``__net_overlaps``
    contains or contained by the given address

``__family``
    matches the given address family

These correspond with the operators and functions from
http://www.postgresql.org/docs/9.4/interactive/functions-net.html

``CidrAddressField`` includes two extra lookups:

``__max_prefixlen``
    Maximum value (inclusive) for ``CIDR`` prefix, does not distinguish between IPv4 and IPv6

``__min_prefixlen``
    Minimum value (inclusive) for ``CIDR`` prefix, does not distinguish between IPv4 and IPv6

Related Django bugs
-------------------

* 11442_ - Postgresql backend casts inet types to text, breaks IP operations and IPv6 lookups.
* 811_ - IPv6 address field support.

https://docs.djangoproject.com/en/dev/releases/1.4/#extended-ipv6-support is also relevant

.. _11442: http://code.djangoproject.com/ticket/11442
.. _811: http://code.djangoproject.com/ticket/811


Similar projects
----------------

https://bitbucket.org/onelson/django-ipyfield tries to solve some of the same
issues as this library. However, instead of supporting just postgres via the proper
fields types the ipyfield currently uses a ``VARCHAR(39)`` as a fake unsigned 64 bit
number in its implementation.

History
-------

Main repo was originaly kept https://github.com/adamcik/django-postgresql-netfields
Late April 2013 the project was moved to https://github.com/jimfunk/django-postgresql-netfields
to pass the torch on to someone who actually uses this code actively :-)
