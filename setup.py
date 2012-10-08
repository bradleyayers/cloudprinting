#!/usr/bin/env python
from os.path import join
import re
from setuptools import setup

# dynamically pull the version from cloudprinting/__init__.py
with open(join('cloudprinting', '__init__.py'), 'r') as f:
    version = re.search('^__version__ = "(.+?)"$', f.read(), re.MULTILINE).group(1)

setup(
    name='cloudprinting',
    version=version,
    description='Simple API for Google Cloud Print',
    author='Bradley Ayers',
    author_email='bradley.ayers@gmail.com',
    url='http://pypi.python.org/pypi/cloudprinting/',

    packages=['cloudprinting'],
    include_package_data=True,  # declarations in MANIFEST.in

    install_requires=['requests'],

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
    ],
)
