from dateutil.parser import parse
from decimal import Decimal

TWOPLACES = Decimal(10) ** -2

class TransactionWriter(object):
  def __init__(self, output):
    if output:
      self.output = output

  def instance(t, output):
    if t == 'csv':
      return CsvTransactionWriter(output)
    if t == 'qif':
      return QifTransactionWriter(output)

  instance = staticmethod(instance)

  def begin(self, account_info):
    pass

  def write_record(self, transaction):
    pass

  def end(self):
    pass

class CsvTransactionWriter(TransactionWriter):
  def begin(self, account_info):
    print('Date,Amount,Description', file=self.output)

  def write_record(self, transaction):
    print(transaction['date'],transaction['amount'],transaction['name'], file=self.output)



class QifTransactionWriter(TransactionWriter):
  def begin(self, account):
    print('!Account', file=self.output)
    print('N%s' % account['path'], file=self.output)
    print('T%s' % account['type'], file=self.output)
    if 'description' in account:
      print('D%s' % account['description'], file=self.output)
    print('^', file=self.output)
    print('!Type:%s' % account['type'], file=self.output)


  def write_record(self, transaction):
    print('C', file=self.output) # cleared status: Values are blank (not cleared), "*" or "c" (cleared) and "X" or "R" (reconciled).
    print('D%s' % self.format_date(transaction['date']), file=self.output)
    print('N%s' % self.format_chknum(transaction), file=self.output)
    print('P%s' % transaction['name'], file=self.output)
    print('T%s' % self.format_amount(transaction['amount']), file=self.output)
    print('^', file=self.output)


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
