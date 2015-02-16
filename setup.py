#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
"""
Setup file.

Specify dependencies, package name and version,
and other meta data.

This file is part of buildtimetrend/python-lib
<https://github.com/buildtimetrend/python-lib>
"""
from setuptools import setup, find_packages


setup(
    name="buildtimetrend",
    version="0.2",
    packages=find_packages(),
    install_requires=['keen>=0.3.9', 'lxml', 'pyyaml', 'python-dateutil'],
    tests_require=['nose', 'coveralls'],
    extras_require={
        'native': ['lxml', 'matplotlib>=1.2.0']
    },

    # metadata
    author="Dieter Adriaenssens",
    author_email="ruleant@users.sourceforge.net",
    description="Visualise what's trending in your build process",
    url="https://buildtimetrend.github.io/",
    license="AGPLv3+",
    keywords=["trends", "charts", "build", "ci", "timing data"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Affero General Public License v3" \
        " or later (AGPLv3+)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance"
    ]
)
