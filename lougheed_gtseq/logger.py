import functools
import logging

__all__ = ["logger"]

logging.basicConfig(level=logging.NOTSET)

logging.getLogger("matplotlib").setLevel(logging.INFO)
logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
logging.getLogger("matplotlib.pyplot").setLevel(logging.INFO)


@functools.cache
def get_logger() -> logging.Logger:
    log = logging.getLogger("lougheed_gtseq")
    log.setLevel(level=logging.INFO)
    return log


logger = get_logger()
