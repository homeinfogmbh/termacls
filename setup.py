#! /usr/bin/env python3

from setuptools import setup

setup(
    name="termacls",
    use_scm_version={"local_scheme": "node-and-timestamp"},
    setup_requires=["setuptools_scm"],
    install_requires=["his", "hwdb", "peewee", "peeweeplus"],
    author="HOMEINFO - Digitale Informationssysteme GmbH",
    author_email="info@homeinfo.de",
    maintainer="Richard Neumann",
    maintainer_email="r.neumann@homeinfo.de",
    packages=["termacls"],
    description="HOMEINFO's terminal ACL libary.",
)
