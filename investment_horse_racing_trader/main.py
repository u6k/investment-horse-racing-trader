import os
import requests
from requests.auth import HTTPBasicAuth
from uuid import uuid4
from datetime import datetime

from investment_horse_racing_trader import flask
from investment_horse_racing_trader.app_logging import get_logger


logger = get_logger(__name__)


def vote_invest(race_id, vote_cost_limit, dry_run):
    logger.info(f"#vote_invest: start: race_id={race_id}, vote_cost_limit={vote_cost_limit}, dry_run={dry_run}")

    # 現在資金を取得する
    asset = get_latest_asset()

    # 予測する
    predict_result = _predict(race_id, asset, vote_cost_limit)

    # 投票する
    vote_result = _vote_win(predict_result)

    return vote_result


def get_latest_asset():
    logger.info("#get_latest_asset: start")

    with flask.get_db().cursor() as db_cursor:
        db_cursor.execute("select sum(vote_cost) as total_vote_cost, sum(vote_return) as total_vote_return from vote_record")
        (total_vote_cost, total_vote_return, ) = db_cursor.fetchone()

    if total_vote_cost is not None and total_vote_return is not None:
        asset = total_vote_return - total_vote_cost
    else:
        asset = 0
    logger.debug(f"#get_latest_asset: total_vote_cost={total_vote_cost}, total_vote_return={total_vote_return}, asset={asset}")

    return asset


def reset_asset(asset):
    logger.info(f"#reset_asset: start: asset={asset}")

    with flask.get_db() as db_conn:
        with db_conn.cursor() as db_cursor:
            reset_result = {
                "vote_record_id": str(uuid4()),
                "before_asset": get_latest_asset(),
                "asset": asset,
            }
            db_cursor.execute("""insert into vote_record (
                vote_record_id,
                race_id,
                bet_type,
                horse_number_1,
                odds,
                vote_cost,
                result,
                result_odds,
                vote_return,
                vote_parameter,
                create_timestamp
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                reset_result["vote_record_id"],
                "reset_asset",
                "reset_asset",
                0,
                0,
                reset_result["before_asset"],
                0,
                0,
                reset_result["asset"],
                "reset_asset",
                datetime.now()
            ))

            db_conn.commit()

    logger.debug(f"#reset_asset: result={reset_result}")

    return reset_result


def _predict(race_id, asset, vote_cost_limit):
    logger.info(f"#_predict: start: race_id={race_id}, asset={asset}, vote_cost_limit={vote_cost_limit}")

    url = os.getenv("API_PREDICT_URL")
    headers = {
        "Content-Type": "application/json",
    }
    auth = HTTPBasicAuth(os.getenv("API_PREDICT_AUTH_USER"), os.getenv("API_PREDICT_AUTH_PASSWORD"))
    params = {
        "race_id": race_id,
        "asset": asset,
        "vote_cost_limit": vote_cost_limit,
    }
    logger.debug(f"#_predict: url={url}, params={params}")

    resp = requests.post(url=url, headers=headers, auth=auth, json=params)
    logger.debug(f"#_predict: status_code={resp.status_code}, body={resp.text}")

    if resp.status_code != 200:
        raise RuntimeError(f"Predict API status_code is {resp.status_code}")

    return resp.json()


def _vote_win(predict_result):
    logger.info("#_vote_win: start")

    with flask.get_db() as db_conn:
        with db_conn.cursor() as db_cursor:
            vote_result = {
                "vote_record_id": str(uuid4()),
                "race_id": predict_result["race_id"],
                "bet_type": "win",
                "horse_number": predict_result["win"]["horse_number"],
                "odds": predict_result["win"]["odds"],
                "vote_cost": predict_result["win"]["vote_cost"],
            }
            create_timestamp = datetime.now()

            db_cursor.execute("""insert into vote_record (
                vote_record_id,
                race_id,
                bet_type,
                horse_number_1,
                odds,
                vote_cost,
                vote_parameter,
                create_timestamp
            ) values (%s, %s, %s, %s, %s, %s, %s, %s)""", (
                vote_result["vote_record_id"],
                vote_result["race_id"],
                vote_result["bet_type"],
                vote_result["horse_number"],
                vote_result["odds"],
                vote_result["vote_cost"],
                predict_result.__str__(),
                create_timestamp
            ))

            db_conn.commit()

    logger.debug(f"#_vote_win: stored: vote_result={vote_result}")

    return vote_result
