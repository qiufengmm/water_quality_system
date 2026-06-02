"""Unit tests for the alert engine module."""

import csv
from pathlib import Path

import pandas as pd
import pytest

from src.alerting.alert_engine import AlertEngine, AlertRecord, AlertRule


@pytest.fixture
def isolated_engine(tmp_path):
    """Create an AlertEngine with history path isolated to a temp file."""
    engine = AlertEngine()
    engine._history_path = tmp_path / "alert_history.csv"
    return engine


class TestAlertRule:
    """Tests for the AlertRule dataclass."""

    def test_create_alert_rule(self):
        """All fields set correctly via constructor."""
        rule = AlertRule("ph", "<", 6.0, "critical", "pH", True)
        assert rule.indicator == "ph"
        assert rule.operator == "<"
        assert rule.threshold == 6.0
        assert rule.severity == "critical"
        assert rule.label == "pH"
        assert rule.enabled is True

    def test_default_label(self):
        """label defaults to empty string."""
        rule = AlertRule("ph", "<", 6.0, "critical")
        assert rule.label == ""

    def test_default_enabled(self):
        """enabled defaults to True."""
        rule = AlertRule("ph", "<", 6.0, "critical")
        assert rule.enabled is True

    def test_severity_values(self):
        """All three severity levels are accepted."""
        for sev in ("info", "warning", "critical"):
            rule = AlertRule("ph", "<", 6.0, sev)
            assert rule.severity == sev

    def test_operator_values(self):
        """Both operators are accepted."""
        for op in (">", "<"):
            rule = AlertRule("ph", op, 6.0, "critical")
            assert rule.operator == op


class TestAlertRecord:
    """Tests for the AlertRecord dataclass."""

    def test_create_alert_record(self):
        """All fields set correctly via constructor."""
        rec = AlertRecord("ST001", "ph", 5.5, "pH < 6.0", "critical", "2026-05-01T08:00:00")
        assert rec.station_id == "ST001"
        assert rec.indicator == "ph"
        assert rec.value == 5.5
        assert rec.rule == "pH < 6.0"
        assert rec.severity == "critical"
        assert rec.timestamp == "2026-05-01T08:00:00"
        assert rec.status == "active"

    def test_default_status(self):
        """status defaults to 'active'."""
        rec = AlertRecord("ST001", "ph", 5.5, "pH < 6.0", "critical", "ts")
        assert rec.status == "active"


class TestAlertEngineInit:
    """Tests for AlertEngine initialization."""

    def test_default_rules_loaded(self):
        """12 default rules from GB 3838-2002 loaded."""
        engine = AlertEngine()
        rules = engine.get_rules()
        assert len(rules) == 12

    def test_custom_rules_override(self):
        """Passing custom list[AlertRule] replaces defaults."""
        custom = [AlertRule("ph", "<", 5.0, "critical", "pH")]
        engine = AlertEngine(custom)
        assert len(engine.get_rules()) == 1
        assert engine.get_rules()[0]["threshold"] == 5.0

    def test_custom_rules_as_alertrule(self):
        """Passing list[AlertRule] sets rules directly."""
        rules = [AlertRule("ph", "<", 5.0, "critical", "pH")]
        engine = AlertEngine(rules)
        assert len(engine.get_rules()) == 1
        assert engine.rules[0].indicator == "ph"
        assert engine.rules[0].threshold == 5.0

    def test_history_path_uses_data_dir(self):
        """_history_path is under settings.data_dir."""
        engine = AlertEngine()
        assert "alert_history.csv" in str(engine._history_path)


class TestAlertEngineCheckDataFrame:
    """Tests for check_dataframe method."""

    def test_no_alerts_for_normal_data(self, sample_df):
        """Normal data triggers zero alerts."""
        engine = AlertEngine([AlertRule("ph", "<", 6.0, "critical")])
        alerts = engine.check_dataframe(sample_df)
        assert len(alerts) == 0

    def test_alerts_for_out_of_range_data(self, sample_df_with_alerts):
        """Out-of-range data triggers alerts."""
        engine = AlertEngine()
        alerts = engine.check_dataframe(sample_df_with_alerts)
        assert len(alerts) > 0

    def test_correct_severity_levels(self):
        """Correct severity assigned per threshold."""
        df = pd.DataFrame({
            "station_id": ["ST001"],
            "ph": [5.5],
            "do": [1.5],
            "turbidity": [12.0],
        })
        engine = AlertEngine()
        alerts = engine.check_dataframe(df)
        severities = {a.severity for a in alerts}
        assert "critical" in severities  # ph < 6.0, do < 2.0
        assert "warning" in severities   # turbidity > 10.0

    def test_station_id_in_records(self, sample_df_with_alerts):
        """AlertRecords carry the originating station_id."""
        engine = AlertEngine()
        alerts = engine.check_dataframe(sample_df_with_alerts)
        for a in alerts:
            assert a.station_id in ("ST001", "ST002")

    def test_missing_indicator_column_skipped(self, sample_df):
        """Column not in df is silently skipped (no KeyError)."""
        engine = AlertEngine([AlertRule("nonexistent", ">", 10, "warning")])
        alerts = engine.check_dataframe(sample_df)
        assert len(alerts) == 0

    def test_disabled_rule_not_checked(self, sample_df_with_alerts):
        """Disabling a rule prevents it from firing."""
        engine = AlertEngine([AlertRule("ph", "<", 6.0, "critical", enabled=False)])
        alerts = engine.check_dataframe(sample_df_with_alerts)
        assert len(alerts) == 0

    def test_all_disabled_returns_empty(self, sample_df_with_alerts):
        """All rules disabled returns empty list."""
        rules = [AlertRule("ph", "<", 6.0, "critical", enabled=False)]
        engine = AlertEngine(rules)
        alerts = engine.check_dataframe(sample_df_with_alerts)
        assert len(alerts) == 0

    def test_empty_dataframe(self):
        """Empty DataFrame returns empty alerts."""
        df = pd.DataFrame({"station_id": [], "ph": []})
        engine = AlertEngine()
        alerts = engine.check_dataframe(df)
        assert len(alerts) == 0


class TestAlertEngineCheckAndSave:
    """Tests for check_and_save method."""

    def test_saves_to_csv(self, sample_df_with_alerts, isolated_engine):
        """After check_and_save, history CSV exists with records."""
        alerts = isolated_engine.check_and_save(sample_df_with_alerts)
        assert len(alerts) > 0
        assert isolated_engine._history_path.exists()

        with open(isolated_engine._history_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == len(alerts)

    def test_no_alerts_no_save(self, sample_df, tmp_path):
        """No alerts triggered -> CSV not created."""
        engine = AlertEngine([AlertRule("ph", "<", 0, "critical")])
        engine._history_path = tmp_path / "alert_history.csv"
        alerts = engine.check_and_save(sample_df)
        assert len(alerts) == 0
        assert not engine._history_path.exists()

    def test_csv_structure(self, sample_df_with_alerts, isolated_engine):
        """CSV headers match AlertRecord fields."""
        isolated_engine.check_and_save(sample_df_with_alerts)

        with open(isolated_engine._history_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

        expected = ["station_id", "indicator", "value", "rule", "severity", "timestamp", "status"]
        assert headers == expected


class TestAlertEngineGetHistory:
    """Tests for get_history method."""

    def test_empty_history(self, isolated_engine):
        """No CSV exists -> total=0, records=[]."""
        result = isolated_engine.get_history()
        assert result["total"] == 0
        assert result["records"] == []

    def test_pagination_defaults(self, sample_df_with_alerts, isolated_engine):
        """Default page=1, page_size=20."""
        isolated_engine.check_and_save(sample_df_with_alerts)
        result = isolated_engine.get_history()
        assert result["page"] == 1
        assert result["page_size"] == 20

    def test_pagination_second_page(self, sample_df_with_alerts, isolated_engine):
        """Enough records to test page 2."""
        isolated_engine.check_and_save(sample_df_with_alerts)
        result_p1 = isolated_engine.get_history(page=1, page_size=2)
        result_p2 = isolated_engine.get_history(page=2, page_size=2)
        assert len(result_p1["records"]) == 2
        assert len(result_p2["records"]) > 0
        # Records should differ between pages
        ids_p1 = {r["timestamp"] for r in result_p1["records"]}
        ids_p2 = {r["timestamp"] for r in result_p2["records"]}
        assert ids_p1 & ids_p2 == set() or result_p1["records"][0]["indicator"] != result_p2["records"][0]["indicator"]

    def test_filter_by_severity(self, sample_df_with_alerts, isolated_engine):
        """Filter by severity returns only matching records."""
        isolated_engine.check_and_save(sample_df_with_alerts)

        critical = isolated_engine.get_history(severity="critical")
        warning = isolated_engine.get_history(severity="warning")
        info = isolated_engine.get_history(severity="info")

        if critical["total"] > 0:
            for r in critical["records"]:
                assert r["severity"] == "critical"
        if warning["total"] > 0:
            for r in warning["records"]:
                assert r["severity"] == "warning"
        if info["total"] > 0:
            for r in info["records"]:
                assert r["severity"] == "info"

        # Combined severity counts should equal total
        total = critical["total"] + warning["total"] + info["total"]
        assert total == isolated_engine.get_history()["total"]

    def test_filter_non_matching_severity(self, isolated_engine):
        """Non-matching severity filter -> empty results."""
        isolated_engine.check_and_save(pd.DataFrame({
            "station_id": ["ST001"], "ph": [5.5],
            "do": [6.0], "nh3n": [0.1],
            "turbidity": [1.0], "cod": [5.0],
            "total_phosphorus": [0.05],
        }))
        result = isolated_engine.get_history(severity="nonexistent")
        assert result["total"] == 0
        assert result["records"] == []


class TestAlertEngineClearHistory:
    """Tests for clear_history method."""

    def test_clear_existing_history(self, sample_df_with_alerts, isolated_engine):
        """Deletes the CSV file."""
        isolated_engine.check_and_save(sample_df_with_alerts)
        assert isolated_engine._history_path.exists()

        isolated_engine.clear_history()
        assert not isolated_engine._history_path.exists()

    def test_clear_empty_history(self, isolated_engine):
        """No error when no CSV exists."""
        isolated_engine.clear_history()  # Should not raise


class TestAlertEngineRules:
    """Tests for rule management methods."""

    def test_get_rules_returns_dicts(self):
        """get_rules() returns list[dict]."""
        engine = AlertEngine()
        rules = engine.get_rules()
        assert isinstance(rules, list)
        assert isinstance(rules[0], dict)

    def test_get_rules_contains_keys(self):
        """Dicts contain all AlertRule fields."""
        engine = AlertEngine()
        rule = engine.get_rules()[0]
        for key in ("indicator", "operator", "threshold", "severity", "label", "enabled"):
            assert key in rule

    def test_update_rules(self):
        """Replacement rules take effect immediately."""
        engine = AlertEngine()
        new_rules = [
            {"indicator": "ph", "operator": "<", "threshold": 5.0, "severity": "critical"},
            {"indicator": "do", "operator": "<", "threshold": 3.0, "severity": "warning"},
        ]
        engine.update_rules(new_rules)
        assert len(engine.get_rules()) == 2
        assert engine.get_rules()[0]["threshold"] == 5.0

    def test_update_rules_missing_fields(self):
        """Missing fields get safe defaults."""
        engine = AlertEngine()
        engine.update_rules([{"indicator": "ph", "operator": "<"}])
        rule = engine.get_rules()[0]
        assert rule["threshold"] == 0  # default
        assert rule["severity"] == "warning"  # default
        assert rule["enabled"] is True  # default
