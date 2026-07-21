"""
Recommendation logging.

Every recommendation the pipeline makes (and every input it rejects) is
appended to logs/recommendation_log.txt, so there's a durable, human-readable
audit trail of what the system suggested, how confident it was, and what
input it refused to act on.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "recommendation_log.txt"


def _log_path(log_dir: str, log_file: str) -> str:
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, log_file)


def log_recommendation(
    user_prefs: Dict,
    song: Dict,
    confidence: float,
    log_dir: str = DEFAULT_LOG_DIR,
    log_file: str = DEFAULT_LOG_FILE,
    timestamp: Optional[str] = None,
) -> str:
    """Append one recommendation entry to the log file. Returns the path written to."""
    path = _log_path(log_dir, log_file)
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"Timestamp: {ts}\n")
        f.write(f"Genre: {user_prefs.get('genre', '')}\n")
        f.write(f"Mood: {user_prefs.get('mood', '')}\n")
        f.write(f"Energy: {user_prefs.get('energy', '')}\n")
        f.write(f"Recommendation: {song['title']} by {song['artist']}\n")
        f.write(f"Confidence: {confidence:.2f}\n\n")

    return path


def log_rejected_input(
    raw_profile: Dict,
    errors: List[str],
    log_dir: str = DEFAULT_LOG_DIR,
    log_file: str = DEFAULT_LOG_FILE,
    timestamp: Optional[str] = None,
) -> str:
    """Append a record of a rejected (invalid) input, so failures are auditable too."""
    path = _log_path(log_dir, log_file)
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"Timestamp: {ts}\n")
        f.write(f"Rejected input: {raw_profile}\n")
        f.write(f"Reasons: {'; '.join(errors)}\n\n")

    return path
