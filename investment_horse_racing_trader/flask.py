from flask import Flask, request
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


@app.route("/api/vote/invest", methods=["POST"])
@multiple_control(singleQueue)
def vote_invest():
    logger.info("#vote_invest: start")

    try:
        args = request.get_json()
        logger.debug(f"#vote_invest: args={args}")

        race_id = args.get("race_id", None)
        vote_cost_limit = args.get("vote_cost_limit", 10000)
        dry_run = args.get("dry_run", True)
        logger.debug(f"#vote_invest: race_id={race_id}, vote_cost_limit={vote_cost_limit}, dry_run={dry_run}")  # FIXME

        # FIXME
        result = {
            "bet_type": "win",
            "horse_number": 1,
            "vote_cost": 100,
            "odds": 1.2,
        }
        logger.debug(f"#vote_invest: result={result}")

        return result

    except Exception:
        logger.exception("error")
        return {"result": False}, 500


@app.route("/api/vote/close", methods=["POST"])
@multiple_control(singleQueue)
def vote_close():
    logger.info("#vote_close: start")

    try:
        args = request.get_json()
        logger.debug(f"#vote_close: args={args}")

        race_id = args.get("race_id", None)
        logger.debug(f"#vote_close: race_id={race_id}")  # FIXME

        # FIXME
        result = {
            "result": 1,
            "vote_return": 120,
        }
        logger.debug(f"#vote_close: result={result}")

        return result

    except Exception:
        logger.exception("error")
        return {"result": False}, 500
