
from democli.utils.log_util import create_logger

logger = create_logger(__name__)


# quit on error
def quit_on_error(message=None, exception=None):
    if message:
        logger.error(str(message))
    if exception:
        raise exception
    else:
        logger.debug("Exiting with code 1..")
        exit(1)


def encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.

    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


