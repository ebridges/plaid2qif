from dateutil.parser import parse
from logging import INFO, DEBUG, basicConfig


def output_filename(account_path, fromto, file_ext):
  account = account_path.split(':')[-1]
  return '%s--%s-%s.%s' % (fromto['start'], fromto['end'], account, file_ext)


def configure_logging(level):
    if not level:
        level = INFO
    else:
        level = DEBUG
    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level)
