#!/usr/bin/env python3
from setuptools import setup

package = {
    'name': 'sbl',
    'version': '0.1.0',
    'description': 'SBL, the stack-based language (working name)',
    'url': 'https://github.com/alekratz/sbl',
    'author': 'Alek Ratzloff',
    'author_email': 'alekratz@gmail.com',
    'license': 'Apache 2',
    'packages': ['sbl'],
    'entry_points': {
        'console_scripts': ['sbl=sbl.sbl:main']
    },
    'test_suite': 'nose.collector',
    'tests_require': 'nose',
}

setup(**package)
