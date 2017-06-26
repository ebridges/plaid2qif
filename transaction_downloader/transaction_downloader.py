"""Transaction Downloader.

Usage:
  transaction-downloader auth --account=<account-name>
  transaction-downloader -h | --help
  transaction-downloader --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --account=<account-name>  Account to work with.
"""
import json
from docopt import docopt
from pkg_resources import require

def read_credentials(account):
  credentials = {}
  
  with open('plaid-credentials.json') as json_data:
      credentials = json.load(json_data)
  
  with open('cfg/%s.json'%account) as json_data:
      credentials["account"] = {};
      credentials["account"]["name"] = account
      credentials["account"]["credentials"] = json.load(json_data)

  return credentials

def main():
  version = require("transaction-downloader")[0].version
  args = docopt(__doc__, version=version)
  print(args)

  credentials = read_credentials(args['--account'])

if __name__ == '__main__':
  main()
