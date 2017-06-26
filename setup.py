import os
from distutils.core import setup
from setuptools import setup, find_packages

with open('requirements.txt') as f:
  REQUIRED = [line.rstrip('\n') for line in f]

__version__ = None
with open('transaction_downloader/__init__.py') as f:
  for line in f:
    if(line.startswith('VERSION')):
      __version__ = line.strip().split('=')[1]
      break


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "transaction-downloader",
    version = __version__,
    author = "Edward Bridges",
    author_email = "ebridges@roja.cc",
    description = "Download financial transactions from financial institutions as QIF files.",
    license = "BSD",
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.md'),
    install_requires=REQUIRED,
    entry_points={
       'console_scripts': [
           'transaction-downloader = transaction_downloader.transaction_downloader:main',
       ]
    },
)
