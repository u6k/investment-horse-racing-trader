from investment_horse_racing_trader import flask, VERSION


class TestFlask:
    def test_health(self):
        result = flask.health()

        assert result["version"] == VERSION
