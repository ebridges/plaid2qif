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

"""
public_key --> auth.html --> public_token
public_token (lifetime ~30m)
public_token --> `transaction-downloader auth` --> access_token
access_token (lifetime indefinite)
"""

import json
from docopt import docopt
from pkg_resources import require


# 'sandbox', 'development', and 'production'

def update_credentials(account, public_token, access_token, item_id):
  with open('cfg/%s.json' % account, 'w') as outfile:
    data = {
      'public_token' : public_token,
      'access_token' : access_token,
      'item_id' : item_id
    }
    json.dump(data, outfile)


def read_credentials(account):
  credentials = {}
  
  with open('plaid-credentials.json') as json_data:
      credentials = json.load(json_data)
  
  with open('cfg/%s.json' % account) as json_data:
      account_credentials = json.load(json_data)

  credentials['account'] = {
    'name': account, 
    'credentials': account_credentials
  };

  return credentials


def main():
  version = require("transaction-downloader")[0].version
  args = docopt(__doc__, version=version)
  print(args)

  credentials = read_credentials(args['--account'])

if __name__ == '__main__':
  main()
