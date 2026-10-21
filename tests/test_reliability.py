"""
Reliability tests for the recommendation pipeline's guardrails, confidence
scoring, and logging. See README.md "Reliability Results" for a summary of
running this suite.
"""

import os

from src.recommender import load_songs, recommend_songs, compute_confidence
from src.validation import validate_profile
from src.logger import log_recommendation

SONGS = load_songs("data/songs.csv")


def test_valid_genre_and_mood_pass_validation():
    profile, errors = validate_profile({"genre": "pop", "mood": "happy", "energy": 0.8}, SONGS)
    assert errors == []
    assert profile["genre"] == "pop"
    assert profile["mood"] == "happy"


def test_invalid_genre_is_rejected():
    _, errors = validate_profile({"genre": "dinosaurs", "mood": "happy", "energy": 0.8}, SONGS)
    assert any("genre" in error.lower() for error in errors)


def test_empty_mood_is_rejected():
    _, errors = validate_profile({"genre": "pop", "mood": "", "energy": 0.8}, SONGS)
    assert any("mood" in error.lower() for error in errors)


def test_energy_outside_range_is_rejected():
    _, errors = validate_profile({"genre": "pop", "mood": "happy", "energy": 4.2}, SONGS)
    assert any("energy" in error.lower() for error in errors)


def test_valid_input_returns_a_recommendation():
    profile, errors = validate_profile({"genre": "pop", "mood": "happy", "energy": 0.8}, SONGS)
    assert errors == []

    recommendations = recommend_songs(profile, SONGS, k=5)
    assert len(recommendations) == 5

    top_song, top_score, _ = recommendations[0]
    assert top_song["title"]
    assert 0.0 <= compute_confidence(top_score) <= 1.0


def test_logger_writes_recommendation_to_file(tmp_path):
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"title": "Test Song", "artist": "Test Artist"}

    log_path = log_recommendation(profile, song, 0.91, log_dir=str(tmp_path))

    assert os.path.exists(log_path)
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
    assert "Test Song" in content
    assert "0.91" in content


def test_missing_genre_is_rejected_not_crashed():
    _, errors = validate_profile({"mood": "happy", "energy": 0.8}, SONGS)
    assert "Genre is required." in errors


def test_non_numeric_energy_is_rejected():
    _, errors = validate_profile({"genre": "pop", "mood": "happy", "energy": "loud"}, SONGS)
    assert any("energy" in error.lower() for error in errors)


def test_capitalization_is_normalized():
    profile, errors = validate_profile({"genre": "Pop", "mood": "Happy", "energy": 0.8}, SONGS)
    assert errors == []
    assert (profile["genre"], profile["mood"]) == ("pop", "happy")


def test_confidence_is_clamped_to_unit_interval():
    assert compute_confidence(0.0) == 0.0
    assert compute_confidence(4.5) == 1.0
    assert compute_confidence(99.0) == 1.0
    assert compute_confidence(-3.0) == 0.0


def test_top_recommendation_for_pop_happy_is_sunrise_city():
    profile, _ = validate_profile({"genre": "pop", "mood": "happy", "energy": 0.8}, SONGS)
    top_song, top_score, _ = recommend_songs(profile, SONGS, k=5)[0]
    assert top_song["title"] == "Sunrise City"
    assert compute_confidence(top_score) > 0.9


def test_rejected_input_is_logged_with_reason(tmp_path):
    from src.logger import log_rejected_input

    log_path = log_rejected_input({"genre": "edm"}, ["Invalid genre 'edm'."], log_dir=str(tmp_path))
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
    assert "edm" in content


def test_conflicting_profile_triggers_warning():
    from src.recommender import check_result_quality

    profile, _ = validate_profile({"genre": "metal", "mood": "peaceful", "energy": 0.95}, SONGS)
    top_song, _, _ = recommend_songs(profile, SONGS, k=5)[0]
    warnings = check_result_quality(profile, top_song, SONGS)
    assert any("No song in the catalog" in w for w in warnings)


def test_matching_profile_has_no_warning():
    from src.recommender import check_result_quality

    profile, _ = validate_profile({"genre": "pop", "mood": "happy", "energy": 0.8}, SONGS)
    top_song, _, _ = recommend_songs(profile, SONGS, k=5)[0]
    assert check_result_quality(profile, top_song, SONGS) == []
