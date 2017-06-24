#!/usr/bin/env python3
from setuptools import setup

package = {
    'name': 'sbl',
    'version': '0.0.1',
    'description': 'SBL, the stack-based language (working name)',
    'url': 'https://github.com/alekratz/sbl',
    'author': 'Alek Ratzloff',
    'author_email': 'alekratz@gmail.com',
    'license': '(C) 2017 Alek Ratzloff',
    'packages': ['sbl'],
    'entry_points': {
        'console_scripts': ['sbl=sbl.sbl:main']
    }
}

setup(**package)