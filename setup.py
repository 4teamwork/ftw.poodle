from setuptools import setup, find_packages
import os

version = '1.6.1.dev0'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'plone.app.testing',
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    ]


setup(name='ftw.poodle',
      version=version,
      description="A product to make polls to find out when to have a meeting",
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw poodle doodle events plone',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.poodle',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'Products.AutocompleteWidget',
        'Products.DataGridField>=1.9.0',
        'ftw.notification.base',
        'ftw.notification.email',
        'ftw.upgrade',
        'plone.api',
        'plone.principalsource',
        'setuptools',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
