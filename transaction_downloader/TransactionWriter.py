
class TransactionWriter(object):
  def __init__(self):
    pass

  def instance(t):
    if t == 'csv':
      return CsvTransactionWriter()
    if t == 'qif':
      return QifTransactionWriter()

  instance = staticmethod(instance)

  def begin(self):
    pass

  def write_record(self, transaction):
    pass

  def end(self):
    pass

class CsvTransactionWriter(TransactionWriter):
  def begin(self):
    print('Date,Amount,Description')

  def write_record(self, transaction):
    print(transaction['date'],transaction['amount'],transaction['name'])

o = TransactionWriter.instance("csv")
o.begin()
