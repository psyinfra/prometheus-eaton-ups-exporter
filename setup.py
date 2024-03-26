#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
  name='prometheus_eaton_ups_exporter',
  version='v1.2.0',
  description='prometheus exporter for eaton ups exporter',
  author='Mathis Lövenich',
  packages=find_packages(),
  license='ISC',
  install_requires=[
    'vcrpy',
    'prometheus_client'
  ],
  python_requires=">=3.11",
  entry_points={
    'console_scripts': [
      'prometheus_eaton_ups_exporter=prometheus_eaton_ups_exporter.main:main'
    ],
  },
)
