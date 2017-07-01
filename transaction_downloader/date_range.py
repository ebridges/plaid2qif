from dateutil.parser import parse

class DateRange(object):
  def __init__(self, start, end):
    self.start = start
    self.end = end

  @staticmethod
  def format_date(date):
    d = parse(date)
    return d.strftime('%Y-%m-%d')

  def start(self):
    return self.start

  def end(self):
    return self.end

  def as_filename(self, account, fmt):
    fmt_start = format_date(self.start)
    fmt_end = format_date(self.end)
    return '%s--%s-%s.%s' % (fmt_start, fmt_end, account, fmt)
