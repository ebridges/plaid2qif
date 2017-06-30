"""Transaction Downloader.

Usage:
  transaction-downloader auth --account=<account-name>
  transaction-downloader download --account=<account-name> --from=<from-date> --to=<to-date> --output=<output>
  transaction-downloader -h | --help
  transaction-downloader --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --account=<account-name>  Account to work with.
  --from=<from-date>        Beginning of date range.
  --to=<to-date>            End of date range.
  --out=<output>            Output format either 'csv' or 'qif'. [Default: csv]
"""

"""
public_key --> auth.html --> public_token
public_token (lifetime ~30m)
public_token --> `transaction-downloader auth` --> access_token
access_token (lifetime indefinite)
"""

import os
import plaid
import json
from docopt import docopt
from pkg_resources import require
from transaction_downloader import TransactionWriter

# 'sandbox', 'development', and 'production'

def download(credentials, start_date, end_date, output):
  client = open_client(credentials)
  access_token = credentials['account']['credentials']['access_token']

  response = client.Transactions.get(access_token, start_date, end_date)
  w = TransactionWriter.TransactionWriter.instance(output)
  w.begin()
  for t in response['transactions']:
    w.write_record(t)
  w.end()


def auth(credentials):
  client = open_client(credentials)
  public_token = credentials['account']['credentials']['public_token']
  response = client.Item.public_token.exchange(public_token)

  update_credentials(
    credentials['account']['name'],
    public_token,
    response['access_token'],
    response['item_id']
  )


def open_client(credentials):
  return plaid.Client(credentials['client_id'],
                      credentials['secret'],
                      credentials['public_key'],
                      os.environ['PLAID_ENV'])  


def update_credentials(account, public_token, access_token, item_id):
  with open('cfg/%s.json' % account, 'w') as outfile:
    data = {
      'public_token' : public_token,
      'access_token' : access_token,
      'item_id' : item_id
    }
    json.dump(data, outfile, sort_keys=True, indent=2, separators=(',', ': '))


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

  if args['auth']:
    auth(credentials)

  if args['download']:
    download(credentials, args['--from'], args['--to'], args['--output'])

if __name__ == '__main__':
  main()
