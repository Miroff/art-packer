#!/usr/bin/env python

from setuptools import setup

setup(name='artpacker',
      version='1.0.1',
      description='Image resources packer to sprite sheets',
      author='Maksim Gurtovenko',
      author_email='maksim@gurtovenko.name',
      url='https://github.com/Miroff/art-packer',
      packages=['artpacker', 'artpacker.metadata', 'artpacker.packer', 'artpacker.saver'],
      scripts=['bin/art-packer'],
      install_requires=[
      	'PIL',
      ],
    )
