from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='svndjango',
      version=version,
      description="automatic backup of django model instances to a subversion repository",
      long_description="""\
""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Django',
        ],
      keywords='',
      author='Columbia Center for New Media Teaching and Learning',
      author_email='ejucovy@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      """,
      )
