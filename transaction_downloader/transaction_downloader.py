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

def main():
  arguments = docopt(__doc__, version='Transaction Downloader 1.0')
  print(arguments)

if __name__ == '__main__':
  main()
