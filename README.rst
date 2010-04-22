Django PostgreSQL Netfields
===========================

This project is an attempt at making proper Django net related fields for
Django Currently the built in ``IPAddressField`` does not support IPv6 and uses
an inefficient ``HOST()`` cast in all lookups. Hopefully there experience from
this project can lead to a resolution of these issues upstream.

In addition to the basic ``IPAddressField`` replacement a ``CIDR`` and
``MACADDR`` field have been added. Furthermore a customer Manager allows for
access to all of PostgreSQL's INET operators.

Dependencies
------------

Currently this code has only been tested against 1.0.x due to the Django
version used by the related project that initiated this effort. ``IPy`` is used
for the same reasons. ``ipaddr`` is being considered, but the conversion
hinges on the related projects conversion to ``ipaddr``.

Getting started
---------------

Make sure ``netfields`` is in your ``PYTHONPATH``, then simply use the
following::

 from netfields import InetAddressField, NetManager

 class Example(models.Model):
     inet = InetAddressField()
     # ...

     objects = NetManager()

The page also provides ``CidrAddressField`` and a ``MACAddressField``.
``NetManager`` is required for the extra lookups to be available. Lookups for
``INET`` and ``CIDR`` database types will be handled differently than when
running vanilla Django.  All lookups are case-insensitive and text based
lookups are avoided whenever possible. In addition to Django's default lookup
types the following have been added.

* ``__net_contained``
* ``__net_contained_or_equal``
* ``__net_contains``
* ``__net_contains_or_equals``

These correspond with the operators from
http://www.postgresql.org/docs/8.3/interactive/functions-net.html

``netfields`` does not have to be in ``INSTALLED_APPS``.

Related Django bugs
-------------------

* 11442_ - Postgresql backend casts inet types to text, breaks IP operations and IPv6 lookups.
* 811_ - IPv6 address field support.

.. _11442: http://code.djangoproject.com/ticket/11442
.. _811: http://code.djangoproject.com/ticket/811
