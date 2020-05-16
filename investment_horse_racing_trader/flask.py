from flask import Flask, request, g
from queue import Queue
import time
import functools
import psycopg2
from psycopg2.extras import DictCursor
import os

from investment_horse_racing_trader.app_logging import get_logger
from investment_horse_racing_trader import VERSION, main


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

        vote_result = main.vote_invest(race_id, vote_cost_limit, dry_run)
        logger.debug(f"#vote_invest: vote_result={vote_result}")

        return vote_result

    except Exception:
        logger.exception("error")
        return {"result": False}, 500


@app.route("/api/asset")
@multiple_control(singleQueue)
def get_asset():
    logger.info("#get_asset: start")
    try:

        result = {
            "asset": main.get_latest_asset(),
        }
        logger.debug(f"#get_asset: result={result}")

        return result

    except Exception:
        logger.exception("error")
        return {"result": False}, 500


@app.route("/api/asset/reset", methods=["POST"])
@multiple_control(singleQueue)
def reset_asset():
    logger.info("#reset_asset: start")
    try:
        args = request.get_json()
        logger.debug(f"#reset_asset: args={args}")

        asset = args.get("asset")

        result = main.reset_asset(asset)
        logger.debug(f"#reset_asset: result={result}")

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


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD")
        )
        g.db.autocommit = False
        g.db.set_client_encoding("utf-8")
        g.db.cursor_factory = DictCursor

    return g.db


@app.teardown_appcontext
def _teardown_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()
