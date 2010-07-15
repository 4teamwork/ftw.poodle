# -*- coding: utf-8 -*-
"""
This module contains the tool of ftw.poodle
"""
from setuptools import setup, find_packages

def read(*rnames):
    return open('/'.join(rnames)).read()

version = open('ftw/poodle/version.txt').read().strip()
maintainer = 'Mathias Leimgruber'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'HISTORY.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('ftw', 'poodle', 'README.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

tests_require=['zope.testing']

setup(name='ftw.poodle',
      version=version,
      description="A product to make polls to find out when to have a meeting (Maintainer: %s)" % maintainer,
      long_description=long_description,
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='http://psc.4teamwork.ch/4teamwork/ftw/ftw.poodle/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Products.DataGridField',
                        'Products.AutocompleteWidget',  
                        'plone.principalsource'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'ftw.poodle.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
