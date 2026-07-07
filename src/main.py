"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# Adversarial / edge case profiles designed to stress the scoring logic:
# conflicting signals, out-of-range values, case mismatches, missing/extra
# keys, and empty strings. See README/model_card.md for the rationale
# behind each one.
EDGE_CASE_PROFILES = [
    {"genre": "metal", "mood": "peaceful", "energy": 0.95},
    {"genre": "edm", "mood": "happy", "energy": 0.8},
    {"genre": "pop", "mood": "happy", "energy": 1.5},
    {"genre": "lofi", "mood": "chill", "energy": -0.5},
    {"genre": "Pop", "mood": "Happy", "energy": 0.8},
    {"genre": "classical", "mood": "energetic", "energy": 0.95, "likes_acoustic": True},
    {"mood": "happy", "energy": 0.8},
    {"genre": "pop", "mood": "happy", "energy": 0.8, "vibe": "unstoppable", "tempo_bpm": 200},
    {"genre": "", "mood": "", "energy": 0.5},
]


def print_recommendations(user_prefs, songs, k=5) -> None:
    profile_desc = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    header = f"Top {k} Recommendations for {profile_desc}"
    print(f"\n{header}")
    print("=" * len(header))

    try:
        recommendations = recommend_songs(user_prefs, songs, k=k)
    except Exception as exc:
        print(f"   ERROR: {type(exc).__name__}: {exc}")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Score:   {score:.2f}")
        print(f"   Reasons: {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    print_recommendations(user_prefs, songs, k=5)

    print("\n" + "#" * 60)
    print("# Adversarial / edge case profiles")
    print("#" * 60)

    for profile in EDGE_CASE_PROFILES:
        print_recommendations(profile, songs, k=5)


if __name__ == "__main__":
    main()
