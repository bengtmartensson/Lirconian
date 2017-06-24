'''Pure Python implementation of the an irsend like program.'''

from lirconian import VERSION
from setuptools import setup

setup(
    name = 'lirconian',
    version = VERSION,
    author = "Bengt Martensson",
    author_email = "barf@bengt-martensson.de",
    url = "https://github.com/bengtmartensson/Lirconian",
    description = "Pure Python implementation of the Lirc irsend program.",
    keywords = "lirc irsend API",
    long_description = open('README.rst', encoding='utf-8').read(),
    license = "GPLv2+",
    packages = ['lirconian'],
#    scripts=['bin/lirconian'],
    include_package_data = True,
    entry_points = {'console_scripts': ['lirconian=lirconian:main']},
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware'
    ]
)
