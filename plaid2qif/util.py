from dateutil.parser import parse
from logging import INFO, DEBUG, basicConfig


def output_filename(account_path, fromto, file_ext):
  def format_date(date):
    d = parse(date)
    return d.strftime('%Y-%m-%d')
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
