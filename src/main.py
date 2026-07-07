"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    k = 5
    recommendations = recommend_songs(user_prefs, songs, k=k)

    profile_desc = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    header = f"Top {k} Recommendations for {profile_desc}"
    print(f"\n{header}")
    print("=" * len(header))

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Score:   {score:.2f}")
        print(f"   Reasons: {explanation}")


if __name__ == "__main__":
    main()
