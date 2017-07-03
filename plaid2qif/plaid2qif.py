"""
Plaid 2 QIF.

Download financial transactions from Plaid and convert to QIF files.

Usage:
  plaid2qif save-access-token --institution=<name> --public-token=<token> [--verbose]
  plaid2qif list-accounts --institution=<name> [--verbose]
  plaid2qif download --institution=<name> --account=<account-name> --account-type=<type> --account-id=<acct-id> --from=<from-date> --to=<to-date> [--output-format=<format>] [--output-dir=<path>] [--verbose]
  plaid2qif -h | --help
  plaid2qif --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --institution=<name>      Institution to get an access token from.
  --public-token=<token>.   Transient auth token to exchange for an access token.
  --account=<account-name>  Complete account name from accounting system that transactions will be imported to.
  --account-type=<type>     Account type [Default: Bank]
  --account-id=<acct-id>    Plaid's account id for this account.
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
from dateutil.parser import parse

CFG_DIR='./cfg'

# PLAID_ENV == 'sandbox', 'development', or 'production'

# account-type == 'Bank', 'CCard', etc.

def download(account, fromto, output):
  client = open_client()
  access_token = read_access_token(account['institution'])
  account_name = account['name']
  account_id = account['id']

  response = client.Transactions.get(access_token, 
    fromto['start'], fromto['end'], 
    account_ids=[account_id])

  txn_batch = len(response['transactions'])
  txn_total = response['total_transactions']
  txn_sofar = txn_batch

  output_to_file = True if output['dir'] else False
  output_file = '%s/%s' % (output['dir'], output_filename(account_name, fromto, output['format']))

  output_handle = output_to_file and open(output_file, 'w') or sys.stdout
  
  try:
    w = transaction_writer.TransactionWriter.instance(output['format'], output_handle)
    w.begin(account)

    debug("txn cnt: %d, txn total: %d" % (txn_batch, txn_total))
    while  txn_batch > 0 and txn_batch <= txn_total:
      
      for t in response['transactions']:
        info('writing record for [%s: %s]' % (t['date'], t['name']))
        debug('%s' % t)
        w.write_record(t)

      response = client.Transactions.get(access_token, 
        start_date=fromto['start'], end_date=fromto['end'], 
        offset=txn_sofar, account_ids=[account_id] )

      txn_batch = len(response['transactions'])
      txn_total = response['total_transactions']
      txn_sofar = txn_batch+txn_sofar

      debug("txn cnt: %d, txn_sofar: %d, txn total: %d" % (txn_batch, txn_sofar, txn_total))

    w.end()

  finally:
    if output_handle is not sys.stdout:
      output_handle.close()

  info('completed writing %d transactions' % txn_sofar)


def list_accounts(institution):
  client = open_client()
  access_token = read_access_token(institution)
  response = client.Accounts.get(access_token)
  accounts = response['accounts']

  for a in accounts:
    print('%s:%s\t%s\t%s\t%s' % (a['type'], a['subtype'], a['name'], a['mask'], a['account_id']))


def save_access_token(institution, public_token):
  global CFG_DIR
  client = open_client()
  response = client.Item.public_token.exchange(public_token)
  with open('%s/%s.json' % (CFG_DIR, institution), 'w') as outfile:
    data = {
      'access_token' : response['access_token'],
      'item_id' : response['item_id']
    }
    json.dump(data, outfile, sort_keys=True, indent=2, separators=(',', ': '))


def read_access_token(institution):
  global CFG_DIR
  with open('%s/%s.json' % (CFG_DIR, institution)) as infile:
    cfg = json.load(infile)
    return cfg['access_token']


def open_client():
  debug('opening client for %s' % os.environ['PLAID_ENV'])
  credentials = {}
  
  info('reading credentials from plaid-credentials.json')
  with open('plaid-credentials.json') as json_data:
      credentials = json.load(json_data)

  return plaid.Client(credentials['client_id'],
                      credentials['secret'],
                      credentials['public_key'],
                      os.environ['PLAID_ENV'])  


def format_date(date):
  d = parse(date)
  return d.strftime('%Y-%m-%d')


def output_filename(account_path, fromto, file_ext):
  fmt_start = format_date(fromto['start'])
  fmt_end = format_date(fromto['end'])
  account = account_path.split(':')[-1]
  return '%s--%s-%s.%s' % (fmt_start, fmt_end, account, file_ext)


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

  if args['save-access-token']:
    save_access_token(args['--institution'], args['--public-token'], args['--save-to'])

  if args['list-accounts']:
    list_accounts(args['--institution'])

  if args['download']:
    account = {
      'institution': args['--institution'],
      'id' : args['--account-id'],
      'name': args['--account'],
      'type': args['--account-type'],
    }
    fromto = {
      'start': args['--from'],
      'end': args['--to']
    }
    output = {
      'dir': args['--output-dir'],
      'format': args['--output-format']
    }
    download(account, fromto, output)

if __name__ == '__main__':
  main()
