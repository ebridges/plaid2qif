"""
Plaid 2 QIF.

Download financial transactions from Plaid and convert to QIF files.

Usage:
  plaid2qif auth --account=<account-name> [--verbose]
  plaid2qif download --account=<account-name> --account-type=<type> --from=<from-date> --to=<to-date> [--output-format=<format>] [--output-dir=<path>] [--verbose]
  plaid2qif -h | --help
  plaid2qif --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --account=<account-name>  Account to work with.
  --account-type=<type>     Account type [Default: Bank]
  --from=<from-date>        Beginning of date range.
  --to=<to-date>            End of date range.
  --output-format=<format>  Output format either 'csv' or 'qif'. [Default: qif]
  --output-dir=<path>       Location to output file to. (Default: output to stdout)
  --verbose                 Verbose logging output.
"""

"""
public_key --> auth.html --> public_token
public_token (lifetime ~30m)
public_token --> `plaid2qif auth` --> access_token
access_token (lifetime indefinite)
"""

import os
import sys
import plaid
import json
from docopt import docopt
from logging import *
from pkg_resources import require
from plaid2qif import transaction_writer
from plaid2qif import date_range

# PLAID_ENV == 'sandbox', 'development', or 'production'

# account-type == 'Bank', 'CCard', etc.

def download(credentials, fromto, output_format, output_dir):
  client = open_client(credentials)
  access_token = credentials['account']['credentials']['access_token']
  account_name = credentials['account']['name']

  response = client.Transactions.get(access_token, fromto.start, fromto.end)
  txn_batch = len(response['transactions'])
  txn_total = response['total_transactions']
  txn_sofar = txn_batch


  output_handle = output_dir and open('%s/%s' % (output_dir, fromto.as_filename(account_name, output_format)), 'w') or sys.stdout
  try:
    w = transaction_writer.TransactionWriter.instance(output_format, output_handle)
    w.begin({'account-path': credentials['account']['account_path'], 
      'account-type': credentials['account']['account_type']})

    debug("txn cnt: %d, txn total: %d" % (txn_batch, txn_total))
    while  txn_batch > 0 and txn_batch <= txn_total:
      for t in response['transactions']:
        info('writing record for [%s: %s]' % (t['date'], t['name']))
        debug('%s' % t)
        w.write_record(t)
      response = client.Transactions.get(access_token, start_date=fromto.start, end_date=fromto.end, offset=txn_sofar )
      txn_batch = len(response['transactions'])
      txn_total = response['total_transactions']
      txn_sofar = txn_batch+txn_sofar
      debug("txn cnt: %d, txn_sofar: %d, txn total: %d" % (txn_batch, txn_sofar, txn_total))

    w.end()
  finally:
    if output_handle is not sys.stdout:
      output_handle.close()

  info('completed writing %d transactions' % txn_sofar)


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
  debug('opening client for %s' % os.environ['PLAID_ENV'])
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


def read_credentials(account_type, account_path):
  credentials = {}
  
  info('reading credentials from plaid-credentials.json')
  with open('plaid-credentials.json') as json_data:
      credentials = json.load(json_data)
  
  account_name = account_path.split(':')[-1]
  account_credentials_file = 'cfg/%s.json' % account_name
  info('reading credentials from %s' % account_credentials_file)
  with open(account_credentials_file) as json_data:
      account_credentials = json.load(json_data)

  credentials['account'] = {
    'name': account_name, 
    'account_path': account_path,
    'account_type': account_type,
    'credentials': account_credentials
  };

  return credentials


def configure_logging(level):
    if not level:
        level = INFO
    else:
        level = DEBUG
    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level)


def main():
  version = require("plaid2qif")[0].version
  args = docopt(__doc__, version=version)
  configure_logging(args['--verbose'])
  debug(args)

  credentials = read_credentials(args['--account-type'], args['--account'])

  fromto = date_range.DateRange(args['--from'], args['--to'])

  if args['auth']:
    auth(credentials)

  if args['download']:
    download(credentials, fromto, args['--output-format'], args['--output-dir'])

if __name__ == '__main__':
  main()