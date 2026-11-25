# log_util.py
# Homemade logger. Modernized 2026.

import time

LOG_LINES: list[str] = []       # module-level buffer; flushed to disk by flush_log()
DEBUG: bool = False             # set to True at startup to enable debug output


def log(message: str) -> None:
    """Append a timestamped *message* to the in-memory log and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a DEBUG-prefixed message when DEBUG is True."""
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Append all buffered log lines to *path* and clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
