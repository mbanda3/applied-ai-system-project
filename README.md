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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

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



