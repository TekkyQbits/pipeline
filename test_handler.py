import pytest
from handler import detect_anomalies


def test_normal_traffic():
    # Arrange
    events = [{"ip": "1.1.1.1"} for _ in range(5)]

    # Act
    results = detect_anomalies(events)

    # Assert
    assert len(results) == 1
    assert results[0]["status"] == "Normal"
    assert results[0]["count"] == 5


def test_bot_attack_detection():
    # Arrange: Create 25 events from same IP
    events = [{"ip": "6.6.6.6"} for _ in range(25)]

    # Act
    results = detect_anomalies(events)

    # Assert
    assert results[0]["status"] == "Critical - Bot Attack"
    assert results[0]["count"] == 25
