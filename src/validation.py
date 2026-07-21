"""
Input validation ("guardrails") for the recommendation pipeline.

Every raw user profile passes through validate_profile() before it ever
reaches the scoring logic in recommender.py. Valid genres/moods are derived
from the actual song catalog (rather than a hardcoded list) so validation
always stays in sync with whatever data the app is loaded with. Bad input
(unknown genre, out-of-range energy, missing fields) produces a clear,
human-readable error instead of a KeyError/ValueError crash or a silently
wrong recommendation.
"""

from typing import Dict, List, Set, Tuple


def get_valid_genres(songs: List[Dict]) -> Set[str]:
    """Return the set of genres actually present in the catalog, lowercased."""
    return {song["genre"].strip().lower() for song in songs}


def get_valid_moods(songs: List[Dict]) -> Set[str]:
    """Return the set of moods actually present in the catalog, lowercased."""
    return {song["mood"].strip().lower() for song in songs}


def validate_profile(raw_profile: Dict, songs: List[Dict]) -> Tuple[Dict, List[str]]:
    """
    Validate and normalize a raw user profile against the song catalog.

    Returns (normalized_profile, errors). When errors is non-empty,
    normalized_profile is incomplete and must not be passed to the scorer.
    """
    errors: List[str] = []
    valid_genres = get_valid_genres(songs)
    valid_moods = get_valid_moods(songs)
    normalized: Dict = {}

    raw_genre = raw_profile.get("genre", "")
    genre = raw_genre.strip().lower() if isinstance(raw_genre, str) else ""
    if not genre:
        errors.append("Genre is required.")
    elif genre not in valid_genres:
        errors.append(f"Invalid genre '{raw_genre}'. Choose one of: {', '.join(sorted(valid_genres))}")
    else:
        normalized["genre"] = genre

    raw_mood = raw_profile.get("mood", "")
    mood = raw_mood.strip().lower() if isinstance(raw_mood, str) else ""
    if not mood:
        errors.append("Mood is required.")
    elif mood not in valid_moods:
        errors.append(f"Invalid mood '{raw_mood}'. Choose one of: {', '.join(sorted(valid_moods))}")
    else:
        normalized["mood"] = mood

    raw_energy = raw_profile.get("energy", None)
    if raw_energy is None:
        errors.append("Energy is required.")
    else:
        try:
            energy = float(raw_energy)
        except (TypeError, ValueError):
            errors.append(f"Energy must be a number, got {raw_energy!r}.")
        else:
            if not (0.0 <= energy <= 1.0):
                errors.append(f"Energy must be between 0 and 1, got {energy}.")
            else:
                normalized["energy"] = energy

    normalized["likes_acoustic"] = bool(raw_profile.get("likes_acoustic", False))

    return normalized, errors
