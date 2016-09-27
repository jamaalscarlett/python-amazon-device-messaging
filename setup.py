#!/usr/bin/env python
import io
import os.path

from setuptools import setup

__author__ = 'jscarlett'
__email__ = "jscarlett@gmail.com"
__version__ = "0.0.1"

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.rst'), encoding='utf8') as f:
    README = f.read()

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Framework :: Django",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Networking",
]

setup(
    name="python-amazon-device-messaging",
    author=__author__,
    author_email=__email__,
    classifiers=CLASSIFIERS,
    description="Send push notifications to kindle fire devices using ADM.",
    download_url="",
    long_description=README,
    url="https://www.jamaalscarlett.com",
    version=__version__,
    install_requires=['requests'],
    include_package_data=True,
    packages=['pythonadm']
)
