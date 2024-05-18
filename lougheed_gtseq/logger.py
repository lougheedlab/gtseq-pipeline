import functools
import logging

__all__ = ["logger"]

logging.basicConfig(level=logging.NOTSET)


@functools.cache
def get_logger() -> logging.Logger:
    log = logging.getLogger("lougheed_gtseq")
    log.setLevel(level=logging.INFO)
    return log


logger = get_logger()
