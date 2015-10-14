import os

from setuptools import setup

__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='chino',
      version='beta',
      description='Wrapper for Chino.io API',
      author='Stefano Tranquillini',
      author_email='stefano@chino.io',
      url='https://www.chino.io',
      packages=['chino'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Software Development",
      ],
      )
