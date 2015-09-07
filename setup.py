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
import buildtimetrend


setup(
    name=buildtimetrend.NAME,
    version=buildtimetrend.VERSION,
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
    long_description="Buildtime Trend generates and gathers timing data of " \
    "build processes. The aggregated data is used to create charts to " \
    "visualise trends of the build process.\n" \
    "These trends can help you gain insight in your build process : " \
    "which stages take most time? Which stages are stable or have a " \
    "fluctuating duration? Is there a decrease or increase in average " \
    "build duration over time?\n" \
    "With these insights you can improve the stability of your build " \
    "process and make it more efficient.\n\n" \
    "The generation of timing data is done with either a client or using " \
    "Buildtime Trend as a Service.\n"
    "The Python based client generates custom timing tags for any shell " \
    "based build process and can easily be integrated. A script processes " \
    "the generated timing tags when the build is finished, and stores " \
    "the results.\n" \
    "Buildtime Trend as a Service gets timing and build related data by " \
    "parsing the logfiles of a buildprocess. Currently, Travis CI is " \
    "supported. Simply trigger the service at the end of a Travis CI build " \
    "and the parsing, aggregating and storing of" \
    "the data is done automatically.",
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
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance"
    ]
)
