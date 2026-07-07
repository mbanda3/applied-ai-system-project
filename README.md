# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project is a content-based music recommender: given a small catalog of songs and a listener's stated taste profile, it scores every song against that profile and returns the top matches with a plain-language explanation of why each was picked. There's no listening history or collaborative filtering here — every recommendation is based purely on comparing a song's own attributes (genre, mood, energy, acousticness) to what the user says they want, which is what makes it "content-based." The goal is to make the scoring math fully transparent so it's easy to see exactly why the system ranked one song above another.

---

## How The System Works

### Song features

Each `Song` carries the following fields: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`.

Of these, the scoring rule only uses four: **genre**, **mood**, **energy**, and **acousticness**. The other three (`tempo_bpm`, `valence`, `danceability`) were left out of the scoring math on purpose — in this catalog they correlate heavily with `energy` (fast tempo and high danceability track high energy almost 1:1), so including them would mostly double-count a signal `energy` already captures, without adding much new information.

### UserProfile fields

`UserProfile` stores exactly the four preferences the scoring rule needs:

- `favorite_genre` (str) — the listener's preferred genre, compared against `Song.genre`
- `favorite_mood` (str) — the listener's preferred mood, compared against `Song.mood`
- `target_energy` (float, 0–1) — the energy level the listener wants right now, compared against `Song.energy`
- `likes_acoustic` (bool) — whether the listener prefers acoustic/organic sound over produced/electronic sound, compared against `Song.acousticness`

### How the Recommender scores a song — Algorithm Recipe

Each song is scored with additive points rather than a normalized 0–1 blend, so it's easy to see exactly which factors contributed how much:

- **Genre match: +2.0 points** — awarded if `song.genre == user.favorite_genre`, else 0. Weighted highest because a favorite genre is the most deliberate, explicit signal the user gives.
- **Mood match: +1.0 point** — awarded if `song.mood == user.favorite_mood`, else 0.
- **Energy closeness: up to +1.0 point** — `1 - abs(song.energy - user.target_energy)`. This rewards songs whose energy is *close* to what the user wants, not just songs with high energy — a user who wants `target_energy = 0.3` should get chill songs ranked highest, not the most intense ones.
- **Acousticness match: up to +0.5 point** — `song.acousticness` if `user.likes_acoustic` is `True`, otherwise `1 - song.acousticness`. Smooth, proportional credit instead of a hard yes/no cutoff, kept as a minor tiebreaker rather than a primary signal.

```
score = 2.0 * genre_match       # 0 or 1
      + 1.0 * mood_match        # 0 or 1
      + 1.0 * energy_score      # 0.0 - 1.0
      + 0.5 * acoustic_score    # 0.0 - 1.0
```

Maximum possible score is 4.5 (perfect genre + mood + energy + acousticness match).

#### Known biases in this recipe

- **Genre dominance** — genre alone (+2.0) outweighs mood (+1.0) and energy (up to +1.0) combined-ish, so a song can out-rank a much better mood/energy fit purely by sharing a genre label. A song that's a *perfect* mood and energy match (worth 2.0) still loses to a same-genre song with a mediocre mood/energy fit (2.0 + partial credit). Great songs that match the user's mood and vibe but sit in a different genre bucket can get buried.
- **Exact-string matching is brittle** — `"pop"` and `"indie pop"` are treated as a total mismatch (0 points) even though they're related, which can penalize genre-adjacent songs disproportionately hard given genre's high weight.
- **Small catalog exaggerates weight effects** — with only 18 songs, a couple of point values can flip the entire top-5, so these weights should be re-checked if the catalog grows.

See [Limitations and Risks](#limitations-and-risks) for the broader picture.

### How songs are chosen

Scoring and ranking are kept as two separate steps: `score_song` computes one song's score in isolation, and `recommend_songs` calls it once per song in the catalog, sorts all the results from highest score to lowest, and returns the top `k`. Keeping these separate means the scoring math can be tested independently of the sorting/selection logic.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` using the starter profile (`genre=pop, mood=happy, energy=0.8`):

```
Loaded songs: 18

Top 5 Recommendations for genre=pop, mood=happy, energy=0.8
===========================================================

1. Sunrise City by Neon Echo
   Score:   4.39
   Reasons: genre match (+2.0), mood match (+1.0), energy closeness (+0.98), acousticness match (+0.41)

2. Gym Hero by Max Pulse
   Score:   3.35
   Reasons: genre match (+2.0), energy closeness (+0.87), acousticness match (+0.47)

3. Rooftop Lights by Indigo Parade
   Score:   2.29
   Reasons: mood match (+1.0), energy closeness (+0.96), acousticness match (+0.33)

4. Warehouse Pulse by Deep Circuit
   Score:   1.40
   Reasons: energy closeness (+0.92), acousticness match (+0.47)

5. Carnival Step by Mango Static
   Score:   1.38
   Reasons: energy closeness (+1.00), acousticness match (+0.38)
```

Sunrise City tops the list as a perfect genre + mood + energy match, exactly as expected. Rooftop Lights is a good example of the "genre dominance" bias noted above: it matches mood and energy closely but only ranks #3 because `"indie pop"` doesn't exact-match `"pop"`, costing it the full +2.0 genre bonus.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

**Weight shift: doubled energy (1.0 → 2.0), halved genre (2.0 → 1.0).** Max possible score stayed at 4.5 since the two shifts offset exactly, and `pytest` still passed, so the scoring formula itself remained valid.

The ranking still changed for the starter profile (`genre=pop, mood=happy, energy=0.8`). With the original weights, the top 5 was Sunrise City, **Gym Hero**, **Rooftop Lights**, Warehouse Pulse, Carnival Step. With energy doubled and genre halved, **Rooftop Lights and Gym Hero swapped places** — a song with no genre match but a close energy fit (Rooftop Lights) out-ranked a song with a genre match but no mood match (Gym Hero). This isn't more "accurate" than the original weights — there's no ground truth to compare against — but it does confirm the ranking is genuinely sensitive to these weights rather than always dominated by genre.

The original 2.0/1.0/1.0/0.5 weights were kept for the shipped version; see `model_card.md` for the full discussion.


---
Testing code for each profile and the top 5 results alongside edge cases: Loaded songs: 18

Top 5 Recommendations for genre=pop, mood=happy, energy=0.8
===========================================================

1. Sunrise City by Neon Echo
   Score:   4.39
   Reasons: genre match (+2.0), mood match (+1.0), energy closeness (+0.98), acousticness match (+0.41)

2. Gym Hero by Max Pulse
   Score:   3.35
   Reasons: genre match (+2.0), energy closeness (+0.87), acousticness match (+0.47)

3. Rooftop Lights by Indigo Parade
   Score:   2.29
   Reasons: mood match (+1.0), energy closeness (+0.96), acousticness match (+0.33)

4. Warehouse Pulse by Deep Circuit
   Score:   1.40
   Reasons: energy closeness (+0.92), acousticness match (+0.47)

5. Carnival Step by Mango Static
   Score:   1.38
   Reasons: energy closeness (+1.00), acousticness match (+0.38)

############################################################
# Adversarial / edge case profiles
############################################################

Top 5 Recommendations for genre=metal, mood=peaceful, energy=0.95
=================================================================

1. Iron Cathedral by Grim Anvil
   Score:   3.46
   Reasons: genre match (+2.0), energy closeness (+0.98), acousticness match (+0.48)

2. Gym Hero by Max Pulse
   Score:   1.46
   Reasons: energy closeness (+0.98), acousticness match (+0.47)

3. Storm Runner by Voltline
   Score:   1.41
   Reasons: energy closeness (+0.96), acousticness match (+0.45)

4. Warehouse Pulse by Deep Circuit
   Score:   1.41
   Reasons: energy closeness (+0.93), acousticness match (+0.47)

5. Sunday Porch by Willow Creek
   Score:   1.40
   Reasons: mood match (+1.0), energy closeness (+0.35), acousticness match (+0.05)

Top 5 Recommendations for genre=edm, mood=happy, energy=0.8
===========================================================

1. Sunrise City by Neon Echo
   Score:   2.39
   Reasons: mood match (+1.0), energy closeness (+0.98), acousticness match (+0.41)

2. Rooftop Lights by Indigo Parade
   Score:   2.29
   Reasons: mood match (+1.0), energy closeness (+0.96), acousticness match (+0.33)

3. Warehouse Pulse by Deep Circuit
   Score:   1.40
   Reasons: energy closeness (+0.92), acousticness match (+0.47)

4. Carnival Step by Mango Static
   Score:   1.38
   Reasons: energy closeness (+1.00), acousticness match (+0.38)

5. Gym Hero by Max Pulse
   Score:   1.34
   Reasons: energy closeness (+0.87), acousticness match (+0.47)

Top 5 Recommendations for genre=pop, mood=happy, energy=1.5
===========================================================

1. Sunrise City by Neon Echo
   Score:   3.73
   Reasons: genre match (+2.0), mood match (+1.0), energy closeness (+0.32), acousticness match (+0.41)

2. Gym Hero by Max Pulse
   Score:   2.91
   Reasons: genre match (+2.0), energy closeness (+0.43), acousticness match (+0.47)

3. Rooftop Lights by Indigo Parade
   Score:   1.58
   Reasons: mood match (+1.0), energy closeness (+0.26), acousticness match (+0.33)

4. Iron Cathedral by Grim Anvil
   Score:   0.95
   Reasons: energy closeness (+0.47), acousticness match (+0.48)

5. Storm Runner by Voltline
   Score:   0.86
   Reasons: energy closeness (+0.41), acousticness match (+0.45)

Top 5 Recommendations for genre=lofi, mood=chill, energy=-0.5
=============================================================

1. Midnight Coding by LoRoom
   Score:   3.23
   Reasons: genre match (+2.0), mood match (+1.0), energy closeness (+0.08), acousticness match (+0.15)

2. Library Rain by Paper Lanterns
   Score:   3.22
   Reasons: genre match (+2.0), mood match (+1.0), energy closeness (+0.15), acousticness match (+0.07)

3. Focus Flow by LoRoom
   Score:   2.21
   Reasons: genre match (+2.0), energy closeness (+0.10), acousticness match (+0.11)

4. Spacewalk Thoughts by Orbit Bloom
   Score:   1.26
   Reasons: mood match (+1.0), energy closeness (+0.22), acousticness match (+0.04)

5. Velvet Nights by Sable Moon
   Score:   0.30
   Reasons: energy closeness (+-0.05), acousticness match (+0.35)

Top 5 Recommendations for genre=Pop, mood=Happy, energy=0.8
===========================================================

1. Warehouse Pulse by Deep Circuit
   Score:   1.40
   Reasons: energy closeness (+0.92), acousticness match (+0.47)

2. Sunrise City by Neon Echo
   Score:   1.39
   Reasons: energy closeness (+0.98), acousticness match (+0.41)

3. Carnival Step by Mango Static
   Score:   1.38
   Reasons: energy closeness (+1.00), acousticness match (+0.38)

4. Gym Hero by Max Pulse
   Score:   1.34
   Reasons: energy closeness (+0.87), acousticness match (+0.47)

5. Storm Runner by Voltline
   Score:   1.34
   Reasons: energy closeness (+0.89), acousticness match (+0.45)

Top 5 Recommendations for genre=classical, mood=energetic, energy=0.95, likes_acoustic=True
===========================================================================================

1. Paper Moonlight by Aria Hollis
   Score:   2.77
   Reasons: genre match (+2.0), energy closeness (+0.30), acousticness match (+0.47)

2. Warehouse Pulse by Deep Circuit
   Score:   1.96
   Reasons: mood match (+1.0), energy closeness (+0.93), acousticness match (+0.03)

3. Storm Runner by Voltline
   Score:   1.01
   Reasons: energy closeness (+0.96), acousticness match (+0.05)

4. Gym Hero by Max Pulse
   Score:   1.01
   Reasons: energy closeness (+0.98), acousticness match (+0.03)

5. Iron Cathedral by Grim Anvil
   Score:   0.99
   Reasons: energy closeness (+0.98), acousticness match (+0.01)

Top 5 Recommendations for mood=happy, energy=0.8
================================================
   ERROR: KeyError: 'genre'

Top 5 Recommendations for genre=pop, mood=happy, energy=0.8, vibe=unstoppable, tempo_bpm=200
============================================================================================

1. Sunrise City by Neon Echo
   Score:   4.39
   Reasons: genre match (+2.0), mood match (+1.0), energy closeness (+0.98), acousticness match (+0.41)

2. Gym Hero by Max Pulse
   Score:   3.35
   Reasons: genre match (+2.0), energy closeness (+0.87), acousticness match (+0.47)

3. Rooftop Lights by Indigo Parade
   Score:   2.29
   Reasons: mood match (+1.0), energy closeness (+0.96), acousticness match (+0.33)

4. Warehouse Pulse by Deep Circuit
   Score:   1.40
   Reasons: energy closeness (+0.92), acousticness match (+0.47)

5. Carnival Step by Mango Static
   Score:   1.38
   Reasons: energy closeness (+1.00), acousticness match (+0.38)

Top 5 Recommendations for genre=, mood=, energy=0.5
===================================================

1. Velvet Nights by Sable Moon
   Score:   1.30
   Reasons: energy closeness (+0.95), acousticness match (+0.35)

2. Night Drive Loop by Neon Echo
   Score:   1.14
   Reasons: energy closeness (+0.75), acousticness match (+0.39)

3. Highway Ghosts by Dust & Wire
   Score:   1.12
   Reasons: energy closeness (+0.92), acousticness match (+0.20)

4. Warehouse Pulse by Deep Circuit
   Score:   1.09
   Reasons: energy closeness (+0.62), acousticness match (+0.47)

5. Blue Hour by Marlow Sky
   Score:   1.09
   Reasons: energy closeness (+0.92), acousticness match (+0.17)

---
---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



