import coloredlogs
from verboselogs import VerboseLogger


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def create_logger(name=None):
    this_logger = VerboseLogger(name)
    fmt = '%(asctime)s %(name)s[%(lineno)d] %(levelname)s %(message)s'
    coloredlogs.install(level='DEBUG', logger=this_logger, isatty=True, milliseconds=True, fmt=fmt)
    return this_logger


def print_with_color(message, p_color):
    print(p_color + message + Color.END)
