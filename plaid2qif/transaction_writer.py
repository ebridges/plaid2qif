from dateutil.parser import parse
from decimal import Decimal
from logging import info
from json import dumps
import unicodedata

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
    if t == 'raw':
      return JsonTransactionWriter(output)

  instance = staticmethod(instance)

  def begin(self, account_info):
    pass

  def write_record(self, transaction):
    pass

  def end(self):
    pass


class JsonTransactionWriter(TransactionWriter):
  def begin(self, account_info):
    print( dumps(account_info, sort_keys=True), file=self.output)

  def write_record(self, transaction):
    print( dumps(transaction, sort_keys=True), file=self.output)


class CsvTransactionWriter(TransactionWriter):
  def begin(self, account_info):
    print('Date,Amount,Description,Category,CategoryID,TransactionID,TransactionType', file=self.output)

  def write_record(self, transaction):
    print("{},{},{},{},{},{},{}".format(transaction['date'], transaction['amount'], '"' + unicodedata.normalize('NFKD', transaction['name'].replace('"', '\'')) + '"',
      '"' + '|'.join([sub.replace('"', '\'') for sub in transaction['category']]) + '"', transaction['category_id'], transaction['transaction_id'], transaction['transaction_type']), file=self.output)

class QifTransactionWriter(TransactionWriter):
  def begin(self, account):
    print('!Account', file=self.output)
    print('N%s' % account['name'], file=self.output)
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

    # if there's a location key for the transaction 
    # and all of its values are non-empty, then record
    # the address in the metadata of the QIF record
    if 'location' in transaction and self.check_location(transaction['location']):
      print('A%s' % transaction['location']['address'], file=self.output)
      print('A%s, %s %s' % (transaction['location']['city'], transaction['location']['state'], transaction['location']['zip']), file=self.output)

    # ditto for lon/lat
    if 'location' in transaction and (transaction['location']['lon'] and transaction['location']['lat']):
      print('ALon:%s,Lat:%s' % (transaction['location']['lon'], transaction['location']['lat']), file=self.output)

    print('^', file=self.output)


  def format_date(self, date):
    d = parse(date)
    return d.strftime('%m/%d/%Y')


  def format_chknum(self, t):
    if(t['payment_meta']['reference_number']):
      return t['payment_meta']['reference_number']
    return 'N/A'


  def format_amount(self,a):
    d = Decimal(a).quantize(TWOPLACES).copy_negate()
    info("formatted amount a [%s] as [%s]" % (a, str(d)))
    return d


  def check_location(self,loc):
    if ('address' in loc and loc['address']) and ('city' in loc and loc['city']) and ('state' in loc and loc['state']) and ('zip' in loc and loc['zip']):
      return True
    else:
      return False
