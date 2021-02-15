#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='ups-prometheus-exporter',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version'],
    description='Create an prometheus prometheus_exporter '
                'for Eaton UPS measures '
                'scraped from the REST API',
    long_description=long_description,
    author='Mathis Loevenich',
    author_email='m.loevenich@fz-juelich.de',
    packages=find_packages(),
    license='LICENSE',
    python_requires='>=3.7',
    install_requires=[
        "requests>=2.25.1",
        "urllib3==1.26.3"
    ],
    tests_require=[
        'pytest>=6.0.1'
    ],
    entry_points={
        'console_scripts': [
            'ups_multi_exporter=eaton_ups.main:multi_exporter',
            'ups_single_exporter=eaton_ups.main:single_exporter'
        ]
    },
    data_files=[]
)