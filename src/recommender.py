import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Maximum possible additive score: 2.0 (genre) + 1.0 (mood) + 1.0 (energy) + 0.5 (acousticness)
MAX_POSSIBLE_SCORE = 4.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": int(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user_prefs using the Algorithm Recipe (+2.0 genre, +1.0 mood, +1.0 energy closeness, +0.5 acousticness) and return (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"].strip().lower() == str(user_prefs["genre"]).strip().lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song["mood"].strip().lower() == str(user_prefs["mood"]).strip().lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    energy_diff = abs(song["energy"] - user_prefs["energy"])
    energy_points = 1.0 * (1 - energy_diff)
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
    acoustic_points = 0.5 * acoustic_fit
    score += acoustic_points
    reasons.append(f"acousticness match (+{acoustic_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song against user_prefs and return the top k as (song, score, explanation), highest first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]

def compute_confidence(score: float, max_score: float = MAX_POSSIBLE_SCORE) -> float:
    """Normalize a raw additive score into a 0.0-1.0 confidence value the user can read at a glance."""
    return max(0.0, min(score / max_score, 1.0))

def explain_recommendation(user_prefs: Dict, song: Dict) -> List[str]:
    """Build a human-readable, bulleted explanation of why a song matches (or doesn't match) user_prefs."""
    lines = []

    if song["genre"].strip().lower() == str(user_prefs["genre"]).strip().lower():
        lines.append(f"✓ Genre matches {song['genre'].title()}")
    else:
        lines.append(f"✗ Genre is {song['genre'].title()}, not {str(user_prefs['genre']).title()}")

    if song["mood"].strip().lower() == str(user_prefs["mood"]).strip().lower():
        lines.append(f"✓ Mood matches {song['mood'].title()}")
    else:
        lines.append(f"✗ Mood is {song['mood'].title()}, not {str(user_prefs['mood']).title()}")

    energy_diff = abs(song["energy"] - user_prefs["energy"])
    if energy_diff <= 0.05:
        lines.append(f"✓ Energy is very similar ({song['energy']:.2f} vs {user_prefs['energy']:.2f})")
    elif energy_diff <= 0.2:
        lines.append(f"✓ Energy is fairly close ({song['energy']:.2f} vs {user_prefs['energy']:.2f})")
    else:
        lines.append(f"✗ Energy differs noticeably ({song['energy']:.2f} vs {user_prefs['energy']:.2f})")

    if user_prefs.get("likes_acoustic"):
        if song["acousticness"] >= 0.6:
            lines.append(f"✓ Acoustic sound matches your preference ({song['acousticness']:.2f})")
        else:
            lines.append(f"✗ Not very acoustic ({song['acousticness']:.2f})")

    return lines
