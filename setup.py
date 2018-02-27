__author__ = 'Stefano Tranquillini <stefano@chino.io>'

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
)
# # Always prefer setuptools over distutils
# from setuptools import setup, find_packages
# # To use a consistent encoding
# from codecs import open
# from os import path
# here = path.abspath(path.dirname(__file__))
# # Utility function to read the README file.
# # Used for the long_description.  It's nice, because now 1) we have a top level
# # README file and 2) it's easier to type in the README file than to put a raw
# # string in below ...
# def read(fname):
#     return open(path.join(path.dirname(__file__), fname)).read()
#
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()
# setup(name='chino',
#       version='1.0.10',
#       description='Wrapper for Chino.io API',
#       long_description=long_description,
#       author='Stefano Tranquillini',
#       author_email='stefano@chino.io',
#       url='https://www.chino.io',
#       packages=['chino'],
#       package_data={
#           "chino": [
#               "logging.conf"
#           ]},
#       license = 'CC BY-SA 4.0',
#
#       classifiers=[
#            "Topic :: Software Development",
#            "Development Status :: 5 - Production/Stable",
#            "Programming Language :: Python :: 2",
#            "Programming Language :: Python :: 3",
#           ],
#       )
