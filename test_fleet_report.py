# test_fleet_report.py
from fleet_report import fleet_summary
from km_wachter import wear_percent

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_does_not_crash_on_missing_reading():
    # A car with no last_service_km must not crash the report and must not be counted as due.
    fleet = [
        {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
        {"id": "VOS-7788", "odometer": 92000},          # no last_service_km
    ]
    result = fleet_summary(fleet)
    assert "average_wear" in result, "fleet_summary must return an average_wear key"
    assert result["due"] == 1, "only VOS-4471 should be due; VOS-7788 has no reading"


def test_wear_percent_accuracy():
    # 14,900 km into a 15,000 km window is 99.33...%, well above the 80% threshold.
    pct = wear_percent(14900, 15000)
    assert 99.0 < pct < 100.0, f"expected ~99.3%, got {pct:.2f}%"

    # 3,400 km into a 15,000 km window is 22.6%, well below the threshold.
    pct_low = wear_percent(3400, 15000)
    assert 22.0 < pct_low < 23.0, f"expected ~22.7%, got {pct_low:.2f}%"


def test_average_wear_is_not_floored():
    # 99.33% + 20% = 119.33% → average 59.67%.  Floor division would give 59 or less.
    fleet = [
        {"id": "A", "odometer": 14900, "last_service_km": 0},
        {"id": "B", "odometer": 3000,  "last_service_km": 0},
    ]
    avg = fleet_summary(fleet)["average_wear"]
    assert abs(avg - 59.67) < 1.0, f"average wear should be ~59.67%, got {avg:.2f}%"
