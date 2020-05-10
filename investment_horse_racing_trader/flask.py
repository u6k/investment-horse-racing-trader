from flask import Flask
from queue import Queue
import time
import functools

from investment_horse_racing_trader.app_logging import get_logger
from investment_horse_racing_trader import VERSION


logger = get_logger(__name__)


app = Flask(__name__)


singleQueue = Queue(maxsize=1)


def multiple_control(q):
    def _multiple_control(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            q.put(time.time())
            logger.debug("#multiple_control: start: critical zone")
            result = func(*args, **kwargs)
            logger.debug("#multiple_control: end: critical zone")
            q.get()
            q.task_done()
            return result
        return wrapper
    return _multiple_control


@app.route("/api/health")
def health():
    logger.info("#health: start")

    try:
        result = {"version": VERSION}

        return result

    except Exception:
        logger.exception("error")
        return "error", 500
