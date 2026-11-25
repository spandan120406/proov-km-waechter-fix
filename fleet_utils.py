# fleet_utils.py
# Helpers for Vossberg Mobility fleet reporting. Modernized 2026.
# Dead code removed: is_due, parse_service_date, chunk_list, mean (all unreferenced).

KM_PER_MILE: float = 1.609          # 1 mile = 1.609 km (corrected: was used backwards)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles for the UK partner report."""
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a float as a whole-number percentage string."""
    return f"{int(value)}%"
