import os
from distutils.core import setup
from setuptools import setup, find_packages

with open('requirements.txt') as f:
  REQUIRED = [line.rstrip('\n') for line in f]

__version__ = None
with open('plaid2qif/__init__.py') as f:
  for line in f:
    if(line.startswith('VERSION')):
      __version__ = str(line.strip().split('=')[1])
      __version__ = __version__.replace("'", '') # !!!
      print ("version is: [%s]" % __version__)
      break


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name = "plaid2qif",
    version = __version__,
    author = "Edward Bridges",
    author_email = "ebridges@roja.cc",
    description = "Download financial transactions from Plaid as QIF files.",
    license = "MIT",
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=REQUIRED,
    entry_points={
       'console_scripts': [
           'plaid2qif = plaid2qif.plaid2qif:main',
       ]
    },
)
