#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.0.1'

config = {
    'packages': ['blockies'],
    'scripts': [],
    'version': version,
    'name': 'blockies-py',
    'entry_points': {
        'console_scripts': [
            'blockies=blockies.blockies:main',
        ]
    },
}
setup(**config)
