from dateutil.parser import parse

class DateRange(object):
  def __init__(self, start, end):
    self.start = start
    self.end = end

  def format_date(self, date):
    d = parse(date)
    return d.strftime('%Y-%m-%d')

  def as_filename(self, account, fmt):
    fmt_start = self.format_date(self.start)
    fmt_end = self.format_date(self.end)
    return '%s--%s-%s.%s' % (fmt_start, fmt_end, account, fmt)
