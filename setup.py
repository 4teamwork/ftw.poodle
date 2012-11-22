from setuptools import setup, find_packages
import os

version = '1.3'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'plone.app.testing',
    'ftw.testing',
    ]


setup(name='ftw.poodle',
      version=version,
      description="A product to make polls to find out when to have a meeting",
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone'
        'Framework :: Plone :: 4.0'
        'Framework :: Plone :: 4.1',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        ],

      keywords='ftw poodle doodle events plone',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.poodle',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'Products.DataGridField',
        'Products.AutocompleteWidget',
        'plone.principalsource',
        'ftw.notification.email',
        'ftw.notification.base',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
