import json

from investment_horse_racing_trader import flask, VERSION


class TestFlask:
    def setUp(self):
        self.app = flask.app.test_client()

    def test_health(self):
        # Execute
        result = self.app.get("/api/health")

        # Check
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert result_data["version"] == VERSION

    def test_vote_invest(self):
        # Setup
        request_data = {
            "race_id": "2003010711",
            "dry_run": True,
        }

        # Execute
        result = self.app.post("/api/vote/invest",
                               data=json.dumps(request_data),
                               content_type="application/json")

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
        request_data = {
            "race_id": "xxx"
        }

        # Execute
        result = self.app.post("/api/vote/close",
                               data=json.dumps(request_data),
                               content_type="application/json")

        # Check
        assert result.status_code == 200

        result_data = json.loads(result.get_data(as_text=True))
        assert result_data["result"] == 1
        assert result_data["vote_return"] == 120
