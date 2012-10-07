#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

import os

def get_long_description():
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    with open(path) as f:
        return f.read()

setup(
    name='django-netfields',
    version='0.1',
    license='BSD',
    description='Django PostgreSQL netfields implementation',
    long_description=get_long_description(),
    url='https://github.com/adamcik/django-postgresql-netfields',

    author=u'Thomas Admacik',
    author_email='adamcik@samfundet.no',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'IPy',
        'django>=1.3',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
