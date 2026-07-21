"""
Command line runner for the Music Recommender Simulation.

The recommendation pipeline is: validate the raw user profile (guardrails),
score and rank songs, attach a confidence score and a plain-language
explanation to each result, and log every recommendation (or rejection)
to logs/recommendation_log.txt. Invalid input is rejected with a clear
message instead of crashing the program.
"""

import sys

from src.recommender import load_songs, recommend_songs, compute_confidence, explain_recommendation
from src.validation import validate_profile
from src.logger import log_recommendation, log_rejected_input

# Windows terminals often default to cp1252, which can't encode the ✓/✗
# characters used in explanations below. Force UTF-8 so output never crashes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# Adversarial / edge case profiles designed to stress the guardrails:
# unknown genre/mood, out-of-range energy, missing fields, case mismatches,
# and extra/empty values. Each one is now caught by validate_profile()
# instead of crashing or silently scoring wrong.
EDGE_CASE_PROFILES = [
    {"genre": "metal", "mood": "peaceful", "energy": 0.95},
    {"genre": "edm", "mood": "happy", "energy": 0.8},                              # unknown genre
    {"genre": "pop", "mood": "happy", "energy": 1.5},                              # energy out of range
    {"genre": "lofi", "mood": "chill", "energy": -0.5},                            # energy out of range
    {"genre": "Pop", "mood": "Happy", "energy": 0.8},                              # case mismatch, now normalized
    {"genre": "classical", "mood": "energetic", "energy": 0.95, "likes_acoustic": True},
    {"mood": "happy", "energy": 0.8},                                              # missing genre
    {"genre": "pop", "mood": "happy", "energy": 0.8, "vibe": "unstoppable", "tempo_bpm": 200},  # extra keys, ignored
    {"genre": "", "mood": "", "energy": 0.5},                                      # empty genre/mood
    {"genre": "pop", "mood": "happy", "energy": "loud"},                           # non-numeric energy
]


def run_recommendation_pipeline(raw_profile: dict, songs: list, k: int = 5) -> None:
    """
    Validate raw_profile, generate up to k recommendations, and print each
    with a confidence score and an explanation. Rejected input and the top
    recommendation are both logged to logs/recommendation_log.txt.
    """
    profile_desc = ", ".join(f"{key}={value}" for key, value in raw_profile.items())
    header = f"Recommendations for {profile_desc}"
    print(f"\n{header}")
    print("=" * len(header))

    user_prefs, errors = validate_profile(raw_profile, songs)
    if errors:
        print("Input rejected:")
        for error in errors:
            print(f"  - {error}")
        log_rejected_input(raw_profile, errors)
        return

    try:
        recommendations = recommend_songs(user_prefs, songs, k=k)
    except Exception as exc:
        print(f"   ERROR: {type(exc).__name__}: {exc}")
        return

    if not recommendations:
        print("No recommendations could be generated.")
        return

    for rank, (song, score, _reasons) in enumerate(recommendations, start=1):
        confidence = compute_confidence(score)
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Confidence: {confidence:.0%}")
        print("   Why this recommendation?")
        for line in explain_recommendation(user_prefs, song):
            print(f"     {line}")

    top_song, top_score, _ = recommendations[0]
    log_recommendation(user_prefs, top_song, compute_confidence(top_score))
    print("\nRecommendation logged successfully.")


def prompt_profile_interactively() -> dict:
    """Prompt the user for genre/mood/energy on the command line, tolerating bad input."""
    genre = input("Genre: ").strip()
    mood = input("Mood: ").strip()
    try:
        energy = float(input("Energy (0-1): "))
    except ValueError:
        print("Energy must be a number.")
        energy = None
    return {"genre": genre, "mood": mood, "energy": energy}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    if "--interactive" in sys.argv:
        run_recommendation_pipeline(prompt_profile_interactively(), songs, k=5)
        return

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    run_recommendation_pipeline(user_prefs, songs, k=5)

    print("\n" + "#" * 60)
    print("# Adversarial / edge case profiles (guardrails in action)")
    print("#" * 60)

    for profile in EDGE_CASE_PROFILES:
        run_recommendation_pipeline(profile, songs, k=5)


if __name__ == "__main__":
    main()
