import json

from investment_horse_racing_trader import flask, VERSION


class TestFlask:
    def setUp(self):
        self.app = flask.app.test_client()

        with flask.get_db_without_flask() as db_conn:
            with db_conn.cursor() as db_cursor:
                db_cursor.execute("delete from vote_record")

                db_conn.commit()

    def test_health(self):
        # Execute
        result = self.app.get("/api/health")

        # Check
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert result_data["version"] == VERSION

    def test_vote_invest(self):
        # Setup
        request_data = {"race_id": "2003010711", "dry_run": True}

        # Execute
        result = self.app.post("/api/vote/invest", json=request_data)

        # Check
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert type(result_data["vote_record_id"]) == str
        assert result_data["race_id"] == request_data["race_id"]
        assert result_data["bet_type"] == "win"
        assert type(result_data["horse_number"]) == int
        assert type(result_data["odds"]) == float
        assert result_data["odds"] >= 1.0
        assert type(result_data["vote_cost"]) == int
        assert result_data["vote_cost"] >= 0

    def test_vote_close(self):
        # Setup
        request_data = {"asset": 1000000}
        self.app.post("/api/asset/reset", json=request_data)

        request_data = {"race_id": "1906050211", "dry_run": True}
        self.app.post("/api/vote/invest", json=request_data)

        request_data = {"race_id": "1906050211"}

        # Execute
        result = self.app.post("/api/vote/close", json=request_data)

        # Check
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert type(result_data["vote_record_id"]) == str
        assert result_data["race_id"] == request_data["race_id"]
        assert type(result_data["horse_number"]) == int
        assert result_data["horse_number"] >= 1
        assert type(result_data["vote_cost"]) == int
        assert result_data["vote_cost"] >= 0
        assert type(result_data["result"]) == int
        assert result_data["result"] > 1
        assert type(result_data["result_odds"]) == float
        assert result_data["result_odds"] >= 1.0
        assert type(result_data["vote_return"]) == int
        assert result_data["vote_return"] >= 0

    def test_get_asset(self):
        # Execute
        result = self.app.get("/api/asset")

        # Check
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert result_data["asset"] == 0

    def test_reset_asset(self):
        # Before check
        result = self.app.get("/api/asset")
        result_data = json.loads(result.get_data(as_text=True))
        assert result_data["asset"] == 0

        # Execute (1)
        request_data = {"asset": 10000}
        result = self.app.post("/api/asset/reset", json=request_data)

        # Check (1)
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert type(result_data["vote_record_id"]) == str
        assert result_data["before_asset"] == 0
        assert result_data["asset"] == 10000

        # Execute (2)
        request_data = {"asset": 1234}
        result = self.app.post("/api/asset/reset", json=request_data)

        # Check (2)
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert type(result_data["vote_record_id"]) == str
        assert result_data["before_asset"] == 10000
        assert result_data["asset"] == 1234

        # After check
        result = self.app.get("/api/asset")
        result_data = json.loads(result.get_data(as_text=True))
        assert result_data["asset"] == 1234
