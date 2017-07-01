from dateutil.parser import parse
from decimal import Decimal

TWOPLACES = Decimal(10) ** -2

class TransactionWriter(object):
  def __init__(self):
    pass

  def instance(t):
    if t == 'csv':
      return CsvTransactionWriter()
    if t == 'qif':
      return QifTransactionWriter()

  instance = staticmethod(instance)

  def begin(self, account_info):
    pass

  def write_record(self, transaction):
    pass

  def end(self):
    pass

class CsvTransactionWriter(TransactionWriter):
  def begin(self, account_info):
    print('Date,Amount,Description')

  def write_record(self, transaction):
    print(transaction['date'],transaction['amount'],transaction['name'])



class QifTransactionWriter(TransactionWriter):
  def begin(self, info):
    print('!Account')
    print('N%s' % info['account-path'])
    print('T%s' % info['account-type'])
    if 'account_description' in info:
      print('D%s' % info['account_description'])
    print('^')
    print('!Type:%s' % info['account-type'])


  def write_record(self, transaction):
    print('C') # cleared status: Values are blank (not cleared), "*" or "c" (cleared) and "X" or "R" (reconciled).
    print('D%s' % self.format_date(transaction['date']))
    print('N%s' % self.format_chknum(transaction))
    print('P%s' % transaction['name'])
    print('T%s' % self.format_amount(transaction['amount']))
    print('^')


  def format_date(self, date):
    d = parse(date)
    return d.strftime('%m/%d/%Y')


  def format_chknum(self, t):
    if(t['payment_meta']['reference_number']):
      return t['payment_meta']['reference_number']
    return 'N/A'


  def format_amount(self,a):
    d = Decimal(a).quantize(TWOPLACES)
    return d
