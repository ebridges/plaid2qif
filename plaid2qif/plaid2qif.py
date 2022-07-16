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
from os import environ
from sys import stdout
from pathlib import Path

from docopt import docopt
from pkg_resources import require
from dotenv import load_dotenv

from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid

from plaid2qif import transaction_writer
from plaid2qif import util


def download(account, fromto, output, ignore_pending, limiter=util.Limiter()):

  options = TransactionsGetRequestOptions()
  
  def do_request(options, limiter):
    access_token = read_access_token()
    options.account_ids = [account['id']]
    client = open_client()
    request = TransactionsGetRequest(
      access_token=access_token,
      start_date=fromto['start'],
      end_date=fromto['end'],
      options=options,
    )

    if limiter.time_to_pause():
      limiter.pause()

    return client.transactions_get(request)

  response = do_request(options, limiter)
  txn_batch = len(response['transactions'])
  txn_total = response['total_transactions']
  txn_sofar = txn_batch

  output_to_file = True if output['dir'] else False
  output_file = '%s/%s' % (output['dir'], util.output_filename(account['name'], fromto, output['format']))

  output_handle = output_to_file and open(output_file, 'w') or stdout

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
      response = do_request(options)

      txn_batch = len(response['transactions'])
      txn_total = response['total_transactions']
      txn_sofar = txn_batch+txn_sofar

      debug("txn cnt: %d, txn_sofar: %d, txn total: %d" % (txn_batch, txn_sofar, txn_total))

    w.end()

  finally:
    if output_handle is not stdout:
      output_handle.close()

  info('completed writing %d transactions' % txn_sofar)


def list_accounts():
  client = open_client()
  request = AccountsGetRequest(access_token=read_access_token())
  response = client.accounts_get(request)
  accounts = response['accounts']

  print('Account:Subaccount\tAccountName\tAcctNum\tAcctID')
  for a in accounts:
    print('%s:%s\t%s\t%s\t%s' % (a['type'], a['subtype'], a['name'], a['mask'], a['account_id']))


def read_access_token():
  with open(environ.get('ACCESS_TOKEN_FILE')) as f:
    return f.readline().rstrip()


def open_client():
  envs = {
    'development': plaid.Environment.Development,
    'sandbox': plaid.Environment.Sandbox,
    'production': plaid.Environment.Production,
  }
  plaid_env = environ.get('PLAID_ENV', 'development')
  if plaid_env not in envs.keys():
    raise ValueError(f'PLAID_ENV={plaid_env} is not a valid choice among: {envs.keys()}')

  plaid_client_id = environ.get('PLAID_CLIENT_ID')
  if not plaid_client_id:
    raise ValueError('PLAID_CLIENT_ID not found in environment.')
  
  plaid_secret = environ.get('PLAID_SECRET')
  if not plaid_secret:
    raise ValueError('PLAID_SECRET not found in environment.')
  
  plaid_version = environ.get('PLAID_API_VERSION', '2020-09-14')
  
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

def display_info(args):
  print('Command line arguments:')
  for arg in sorted(args.keys()):
    print(f"\t {arg}: {args[arg]}")
  print('Environment variables:')
  print(f"\tACCESS_TOKEN_FILE: {environ.get('ACCESS_TOKEN_FILE', 'absent')}")
  print(f"\tPLAID_CLIENT_ID: {environ.get('PLAID_CLIENT_ID', 'absent')}")
  print(f"\tPLAID_SECRET: {environ.get('PLAID_SECRET', 'absent')}")
  print(f"\tPLAID_ENV: {environ.get('PLAID_ENV', 'absent')}")
  print(f"\tAPPLICATION_NAME: {environ.get('APPLICATION_NAME', 'absent')}")
  print(f"\tPLAID_SANDBOX_REDIRECT_URI: {environ.get('PLAID_SANDBOX_REDIRECT_URI', 'absent')}")
  print(f"\tPORT_NUMBER: {environ.get('PORT_NUMBER', 'absent')}")
  

def main():
  load_dotenv(dotenv_path=f'{Path.cwd()}/.env')
  version = require("plaid2qif")[0].version
  args = docopt(__doc__, version=version)
  util.configure_logging(args['--verbose'])
  debug(args)
  
  if args['info']:
    display_info(args)
    return

  if args['list-accounts']:
    list_accounts()
    return

  if args['download']:
    account = {
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
    download(account, fromto, output, ignore_pending)
    return

if __name__ == '__main__':
  main()
