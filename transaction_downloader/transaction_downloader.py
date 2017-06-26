"""Transaction Downloader.

Usage:
  transaction-downloader auth --public-token=<token>
  transaction-downloader -h | --help
  transaction-downloader --version

Options:
  -h --help               Show this screen.
  --version               Show version.
  --public-token=<token>  Public token.
"""
from docopt import docopt
from pkg_resources import require

def main():
  version = require("transaction-downloader")[0].version
  arguments = docopt(__doc__, version=version)
  print(arguments)

if __name__ == '__main__':
  main()
