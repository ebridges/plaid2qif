"""
Plaid 2 QIF.

Download financial transactions from Plaid and convert to QIF files.

Usage:
  plaid2qif download --account=<account-name> --account-type=<type> --account-id=<acct-id> --from=<from-date> --to=<to-date> [--output-format=<format>] [--output-dir=<path>] [--ignore-pending] [--verbose]
  plaid2qif list-accounts [--verbose]
  plaid2qif info
  plaid2qif -h | --help
  plaid2qif --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --account=<account-name>  Complete account name from accounting system that transactions will be imported to.
  --account-type=<type>     Account type [Default: Bank]
  --account-id=<acct-id>    Plaid's account id for this account.
  --from=<from-date>        Beginning of date range.
  --to=<to-date>            End of date range.
  --output-format=<format>  Output format either 'raw', 'csv' or 'qif'. [Default: qif]
  --output-dir=<path>       Location to output file to. (Default: output to stdout)
  --ignore-pending          Ignore pending transactions.
  --verbose                 Verbose logging output.
"""
from datetime import datetime
from logging import debug, info
import os
import sys

from docopt import docopt
from pkg_resources import require
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid

from plaid2qif import transaction_writer
from plaid2qif import util


def download(account, fromto, output, ignore_pending, plaid_credentials):
  client = open_client(plaid_credentials)
  access_token = read_access_token(account['institution'])
  account_name = account['name']
  account_id = account['id']
  options = TransactionsGetRequestOptions()
  options.account_ids = [account_id]

  def req(options):
    request = TransactionsGetRequest(
      access_token=access_token,
      start_date=fromto['start'],
      end_date=fromto['end'],
      options=options,
    )
    return client.transactions_get(request)

  response = req(options)
  txn_batch = len(response['transactions'])
  txn_total = response['total_transactions']
  txn_sofar = txn_batch

  output_to_file = True if output['dir'] else False
  output_file = '%s/%s' % (output['dir'], util.output_filename(account_name, fromto, output['format']))

  output_handle = output_to_file and open(output_file, 'w') or sys.stdout

  try:
    w = transaction_writer.TransactionWriter.instance(output['format'], output_handle)
    w.begin(account)

    debug("txn cnt: %d, txn total: %d" % (txn_batch, txn_total))
    while 0 < txn_batch <= txn_total:
      for t in response['transactions']:
        if ignore_pending and t['pending']:
          info('skipping pending transaction for [%s: %s]' % (t['date'], t['name']))
          continue
        info('writing record for [%s: %s]' % (t['date'], t['name']))
        debug('%s' % t)
        w.write_record(t)

      options.offset = txn_sofar
      response = req(options)

      txn_batch = len(response['transactions'])
      txn_total = response['total_transactions']
      txn_sofar = txn_batch+txn_sofar

      debug("txn cnt: %d, txn_sofar: %d, txn total: %d" % (txn_batch, txn_sofar, txn_total))

    w.end()

  finally:
    if output_handle is not sys.stdout:
      output_handle.close()

  info('completed writing %d transactions' % txn_sofar)


def list_accounts(institution, plaid_credentials):
  client = open_client(plaid_credentials)
  request = AccountsGetRequest(access_token=read_access_token(institution))
  response = client.accounts_get(request)
  accounts = response['accounts']

  for a in accounts:
    print('%s:%s\t%s\t%s\t%s' % (a['type'], a['subtype'], a['name'], a['mask'], a['account_id']))


def save_access_token(institution, public_token, plaid_credentials):
  global CFG_DIR
  client = open_client(plaid_credentials)
  response = client.Item.public_token.exchange(public_token)
  with open('%s/%s.json' % (CFG_DIR, institution), 'w') as outfile:
    data = {
      'access_token' : response['access_token'],
      'item_id' : response['item_id']
    }
    json.dump(data, outfile, sort_keys=True, indent=2, separators=(',', ': '))
def read_access_token():
  with open(os.environ.get('ACCESS_TOKEN_FILE')) as f:
    return f.readline().rstrip()


def open_client():
  envs = {
    'development': plaid.Environment.Development,
    'sandbox': plaid.Environment.Sandbox,
    'production': plaid.Environment.Production,
  }
  plaid_env = os.environ.get('PLAID_ENV', 'development')
  if plaid_env not in envs.keys():
    raise ValueError(f'PLAID_ENV={plaid_env} is not a valid choice among: {envs.keys()}')

  plaid_client_id = os.environ.get('PLAID_CLIENT_ID')
  if not plaid_client_id:
    raise ValueError('PLAID_CLIENT_ID not found in environment.')
  
  plaid_secret = os.environ.get('PLAID_SECRET')
  if not plaid_secret:
    raise ValueError('PLAID_SECRET not found in environment.')
  
  plaid_version = os.environ.get('PLAID_API_VERSION', '2020-09-14')
  
  debug('opening client for %s' % plaid_env)

  configuration = plaid.Configuration(
    host=envs[plaid_env],
    api_key={
      'clientId': plaid_client_id,
      'secret': plaid_secret,
      'plaidVersion': plaid_version,
    }
  )
  api_client = plaid.ApiClient(configuration)
  client = plaid_api.PlaidApi(api_client)
  return client


def main():
  version = require("plaid2qif")[0].version
  args = docopt(__doc__, version=version)
  util.configure_logging(args['--verbose'])
  debug(args)

  if args['save-access-token']:
    save_access_token(args['--institution'], args['--public-token'], args['--credentials'])

  if args['list-accounts']:
    list_accounts(args['--institution'], args['--credentials'])

  if args['download']:
    account = {
      'institution': args['--institution'],
      'id' : args['--account-id'],
      'name': args['--account'],
      'type': args['--account-type'],
    }
    fromto = {
      'start': datetime.strptime(args['--from'], '%Y-%m-%d').date(),
      'end': datetime.strptime(args['--to'], '%Y-%m-%d').date(),
    }
    output = {
      'dir': args['--output-dir'],
      'format': args['--output-format']
    }
    ignore_pending = args['--ignore-pending']
    plaid_credentials = args['--credentials']
    download(account, fromto, output, ignore_pending, plaid_credentials)

if __name__ == '__main__':
  main()
