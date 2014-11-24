#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:

from setuptools import setup, find_packages


setup(
    name="Buildtime Trend library",
    version="0.2-dev",
    packages=find_packages(),
    install_requires=['keen', 'lxml', 'pyyaml', 'python-dateutil'],
    tests_require=['nose'],
    extras_require={
        'native trends': ['matplotlib>=1.2.0']
    },

    # metadata
    author="Dieter Adriaenssens",
    author_email="ruleant@users.sourceforge.net",
    description="Visualise what's trending in your build process",
    license="GPLv3",
    keywords=["trends", "charts", "build", "ci", "timing data"],
    url="http://ruleant.github.io/buildtime-trend/"
)
