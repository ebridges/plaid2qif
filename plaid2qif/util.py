from dateutil.parser import parse
from logging import INFO, DEBUG, basicConfig
from time import sleep

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


class Limiter():
    def __init__(self):
        pass

    def time_to_pause(self):
        return False

    def pause(self):
        return


class SleepLimiter(Limiter):
    def __init__(self, limit=30, wait_for=30):
        self.count = 0
        self.limit=limit
        self.wait_for=wait_for

    def time_to_pause(self):
        self.count += 1
        if self.count > self.limit:
            self.count = 0
            return True
        else:
            return False

    def pause(self):
        sleep(self.wait_for)
