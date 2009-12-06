from setuptools import setup, find_packages
import sys, os

version = '0.5'

long_description = open('README.txt').read()
new_in_this_version = open('changes/changes.txt').read()
history = open('changes/history.txt').read()

long_description = "%s\n\nNew in version %s:\n\n%s\n\nHistory:\n\n%s" % (long_description,version,new_in_this_version,history)

setup(name='django-vcexport',
      version=version,
      description="a flexible library for exporting serialized django model instances to a version-controlled repository automatically or manually",
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Django',
        ],
      keywords='',
      author='Ethan Jucovy',
      author_email='ejucovy@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'sven>=0.6',
      ],
      entry_points="""
      """,
      )
