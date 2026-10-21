# 🎵 VibeFinder — Music Recommender Simulation

A small, fully-transparent content-based recommender with input guardrails, confidence scoring, human-readable explanations, and an automated reliability test suite.

---

## Original Project

**Music Recommender Simulation ("VibeFinder"),** built in Modules 1–3 of this course. The original goal was to represent songs and a listener's "taste profile" as plain data, design a transparent scoring rule that turns that data into ranked recommendations, and evaluate where the resulting system gets things right versus where it's biased. It shipped as a content-based recommender: given a small 18-song catalog and a user-stated profile (genre, mood, energy, and an acoustic preference), it scored every song against that profile and returned the top matches with a plain-language breakdown of the score — no listening history or collaborative filtering, just direct attribute comparison.

This repo extends that project with a **Reliability & Testing System**: input validation, confidence scoring, explanation generation, logging, error handling, and an automated test suite, all wired directly into the recommendation pipeline rather than bolted on as a side script.

---

## Summary

VibeFinder takes a genre/mood/energy profile and returns a ranked list of songs, each with a **confidence percentage** and a **plain-language explanation** of why it was picked — instead of a raw, uninterpretable score. Bad input (a genre not in the catalog, an energy value outside 0–1, a missing field) is caught by validation guardrails and rejected with a specific, actionable message rather than crashing the program or silently producing a nonsense ranking. Every request — accepted or rejected — is logged to disk, and a 14-test reliability suite (16 tests total with the original scoring tests) verifies the guardrails, scoring, and logging all behave correctly.

Why this matters: any AI system that ranks or recommends things needs a way to (1) reject input it can't handle safely, (2) communicate how confident it is, (3) explain its reasoning, and (4) leave an audit trail. This project is a small, inspectable example of all four, built on top of a scoring rule simple enough that every part of the pipeline can be reasoned about by hand.

---

## The AI Feature: Reliability & Testing System

The project's required AI feature is a **Reliability or Testing System**, and it is part of the main pipeline, not a side script. It changes what the app does:

- **Guardrails** decide whether a request reaches the scorer at all.
- **Confidence scores** and **explanations** are attached to every recommendation shown.
- A **self-check** (`check_result_quality()`) inspects the finished ranking and prints a warning when the top song drops part of what the user asked for (for example, no catalog song is both `metal` and `peaceful`).
- **Logging** records every accepted request (with any warnings) and every rejected one.
- The **pytest suite** and a documented human evaluation measure all of the above.

---

## Architecture Overview

The system is a straight `input → process → output` pipeline, with validation gating entry and a human/testing layer checking the result on both ends. Source of truth: [`diagrams/architecture.mmd`](diagrams/architecture.mmd).

```mermaid
flowchart TD
    U["User Input<br/>genre, mood, energy<br/>(demo profiles or python -m src.main --interactive)"]

    U --> V{"Input Validation / Guardrails<br/>src/validation.py"}

    CAT[("Song Catalog<br/>data/songs.csv")]

    V -->|"invalid"| REJ["Rejection Message<br/>+ specific reasons<br/>(bad genre/mood, energy out of range,<br/>non-numeric energy, missing fields)"]
    V -->|"valid (normalized)"| SC["Recommender / Scorer<br/>src/recommender.py<br/>score_song + recommend_songs"]

    CAT --> SC

    SC --> CHK["Self-Check<br/>check_result_quality()<br/>warns if top result drops genre/mood"]
    SC --> CONF["Confidence Scoring<br/>compute_confidence()<br/>score / 4.5 -> 0-100%"]
    SC --> EXP["Explanation Generator<br/>explain_recommendation()<br/>plain-language checkmarks"]

    CHK --> OUT
    CONF --> OUT["Console Output<br/>ranked songs, confidence %, reasons, warnings"]
    EXP --> OUT
    REJ --> OUT

    OUT --> LOG["Logger<br/>src/logger.py<br/>logs/recommendation_log.txt<br/>(accepted AND rejected requests)"]

    OUT --> HUMAN["Human Review<br/>reads console output + log file,<br/>sanity-checks rankings/explanations"]

    subgraph TEST["Reliability Testing (tests/, run via pytest)"]
        T1["test_reliability.py<br/>guardrails, confidence, logging"]
        T2["test_recommender.py<br/>core scoring logic"]
    end

    T1 -. "verifies" .-> V
    T1 -. "verifies" .-> LOG
    T1 -. "verifies" .-> CHK
    T2 -. "verifies" .-> SC
    HUMAN -. "flags bugs / bad rankings" .-> TEST
```

**Components:**

- **Self-Check** (`check_result_quality()` in `src/recommender.py`) — after ranking, verifies the top result honors the requested genre and mood, and warns (and logs the warning) when it doesn't.
- **Validator** (`src/validation.py`) — the guardrail. Derives valid genres/moods directly from `data/songs.csv` (so it can never drift out of sync with the data) and checks energy is a real number in `0.0–1.0`. Bad input never reaches the scorer.
- **Recommender / Scorer** (`src/recommender.py`) — the original additive scoring rule (genre + mood + energy + acousticness), unchanged in its core logic.
- **Confidence Scoring** (`compute_confidence()`) — normalizes the raw score into a 0–100% figure a non-technical user can read.
- **Explanation Generator** (`explain_recommendation()`) — turns the scoring breakdown into ✓/✗ plain-language bullets.
- **Logger** (`src/logger.py`) — append-only audit trail of every accepted recommendation and every rejected input.
- **Reliability Testing** (`tests/`) — `pytest` suite that verifies the validator, scorer, and logger independently of any single run.
- **Human Review** — the console output and log file are designed to be human-readable at a glance, so a person (not just a test) can sanity-check any given recommendation.

---

## How the Recommender Scores a Song

Each song is scored against a user profile with additive points, so it's always possible to see exactly which factor contributed how much:

```
score = 2.0 * genre_match       # 1 if song.genre == user.genre, else 0
      + 1.0 * mood_match        # 1 if song.mood == user.mood, else 0
      + 1.0 * energy_score      # 1 - abs(song.energy - user.energy), 0.0-1.0
      + 0.5 * acoustic_score    # song.acousticness, or 1 - it if user dislikes acoustic
```

Maximum possible score is **4.5** (perfect genre + mood + energy + acousticness match) — this is the denominator `compute_confidence()` divides by to get a percentage. Genre is weighted highest because a stated favorite genre is the most deliberate, explicit signal a user gives; acousticness is weighted lowest and acts more as a tiebreaker.

---

## Setup Instructions

1. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app** (Python 3.10+; `pytest` is the only package the code needs):

   ```bash
   python -m src.main
   ```

   This runs a starter profile plus a set of adversarial/edge-case profiles that exercise the guardrails, and writes every recommendation/rejection to `logs/recommendation_log.txt` (created automatically — no setup needed).

4. **Or run it interactively**, entering your own genre/mood/energy:

   ```bash
   python -m src.main --interactive
   ```

5. **Run the tests** (expect `16 passed`):

   ```bash
   pytest
   ```

---

## Sample Interactions

**1. Valid input — high-confidence match**

Input: `genre=pop, mood=happy, energy=0.8`

```
1. Sunrise City by Neon Echo
   Confidence: 98%
   Why this recommendation?
     ✓ Genre matches Pop
     ✓ Mood matches Happy
     ✓ Energy is very similar (0.82 vs 0.80)

Recommendation logged successfully.
```

**2. Invalid genre — rejected by the guardrail**

Input: `genre=edm, mood=happy, energy=0.8`

```
Input rejected:
  - Invalid genre 'edm'. Choose one of: ambient, blues, classical, country, folk, house, indie pop, jazz, latin, lofi, metal, pop, r&b, rock, synthwave
```

**3. Energy out of range — rejected instead of silently mis-scored**

Input: `genre=pop, mood=happy, energy=1.5`

```
Input rejected:
  - Energy must be between 0 and 1, got 1.5.
```

**4. Case mismatch — now normalized instead of silently failing**

Input: `genre=Pop, mood=Happy, energy=0.8` (same real preferences as example 1, different capitalization)

```
1. Sunrise City by Neon Echo
   Confidence: 98%
   Why this recommendation?
     ✓ Genre matches Pop
     ✓ Mood matches Happy
     ✓ Energy is very similar (0.82 vs 0.80)
```

Before validation was added, this exact input returned a completely different (and wrong) top result, because genre/mood comparisons were case-sensitive — see [Testing Summary](#testing-summary).

**5. Conflicting preferences — self-check warns**

Input: `genre=metal, mood=peaceful, energy=0.95`

```
   WARNING: No song in the catalog is both metal and peaceful; the top result trades one preference away.

   WARNING: Top result mood is 'angry', not 'peaceful'.
```

---

## Design Decisions

- **Additive scoring over a normalized blend.** Each factor (genre +2.0, mood +1.0, energy up to +1.0, acousticness up to +0.5) contributes independently, so anyone reading the explanation can see exactly which factors drove a song's rank. The trade-off is that genre dominates the total (a genre match alone outweighs a perfect mood + energy match), which is a real, acknowledged bias rather than a hidden one — see [Limitations](#limitations).
- **Guardrails derived from the catalog, not a hardcoded list.** `validate_profile()` reads valid genres/moods from `data/songs.csv` at load time instead of a fixed set like `{"pop", "rock", "hip-hop", ...}`. The trade-off is one extra dependency (validation now needs the loaded catalog as an argument), but it means validation can never silently reject a genre that's actually in the data, or accept one that isn't.
- **Confidence as `score / max_possible_score`, clamped to [0, 1].** Simple and directly traceable back to the scoring recipe, at the cost of not being a calibrated probability — a 74% confidence doesn't mean "74% likely to be liked," only "74% of the maximum possible score."
- **Log both successes and failures.** `logs/recommendation_log.txt` records rejected input as well as accepted recommendations. This costs a bit of log verbosity, but means the log is also useful for debugging guardrail behavior later, not just for auditing what was recommended.
- **Kept exact-string matching for genre/mood** (fixing only case-sensitivity, not fuzzy matching). A more forgiving matcher (e.g., treating `"indie pop"` as partially matching `"pop"`) would soften the genre-dominance bias, but it would also make the scoring harder to explain in one line — I chose transparency over recall here, and documented the resulting brittleness instead of hiding it.
- **Self-check warns instead of re-ranking.** When preferences conflict, the system flags it rather than silently changing the scoring rule, which keeps the score explainable; the trade-off is that the user still gets the imperfect ranking.
- **Validation and logging as separate modules** (`validation.py`, `logger.py`) rather than folded into `recommender.py` or `main.py`. Keeps each concern independently testable and means the core scoring logic wasn't touched to add reliability features.
- **Verified the weights weren't arbitrary by perturbing them.** As an experiment, I doubled the energy weight (1.0 → 2.0) and halved the genre weight (2.0 → 1.0) — the max score stayed 4.5 and `pytest` still passed, but the actual top-5 ranking for the starter profile changed (two songs swapped places). That confirmed the ranking is genuinely sensitive to these weights, not always dominated by genre regardless of their values, before committing to the original 2.0/1.0/1.0/0.5 split.

---

## Testing Summary

**Headline:** 16 of 16 automated tests pass (`pytest`, 0.09s). Confidence on the top result averaged **0.89** across 5 well-matched profiles and **0.83** across 7 profiles including 2 deliberately conflicting ones. The system struggles where the catalog can't satisfy a conflicting request (e.g. "peaceful metal"): confidence stays high (0.77) even though the mood is wrong, so confidence is a weak signal of true quality there. Adding validation fixed 3 real bugs (below), and the new self-check now surfaces the conflicting-profile failures as warnings instead of hiding them.

Reliability is measured four ways: automated tests, confidence scoring, logging/error handling, and a human evaluation of outputs.

### 1. Automated tests (`pytest`)

| Test | What it checks | Result |
|---|---|---|
| test_valid_genre_and_mood_pass_validation | Valid input yields no errors | Pass |
| test_invalid_genre_is_rejected | Unknown genre rejected with reason | Pass |
| test_empty_mood_is_rejected | Empty mood rejected | Pass |
| test_energy_outside_range_is_rejected | Energy 4.2 rejected | Pass |
| test_missing_genre_is_rejected_not_crashed | Missing key gives error, not KeyError | Pass |
| test_non_numeric_energy_is_rejected | Energy "loud" rejected | Pass |
| test_capitalization_is_normalized | "Pop"/"Happy" normalized to lowercase | Pass |
| test_confidence_is_clamped_to_unit_interval | Confidence always within 0-1 | Pass |
| test_valid_input_returns_a_recommendation | End-to-end returns 5 ranked songs | Pass |
| test_top_recommendation_for_pop_happy_is_sunrise_city | Known-good ranking regression check | Pass |
| test_logger_writes_recommendation_to_file | Accepted request is logged | Pass |
| test_rejected_input_is_logged_with_reason | Rejected request is logged with reason | Pass |
| test_conflicting_profile_triggers_warning | metal/peaceful triggers self-check warning | Pass |
| test_matching_profile_has_no_warning | pop/happy triggers no warning | Pass |
| 2 original tests in test_recommender.py | Core scoring/ranking and explanation | Pass |

### 2. Confidence scoring

Confidence = score / 4.5, clamped to 0-1, shown with every recommendation. It is *not* a calibrated probability (see [model_card.md](model_card.md)).

### 3. Logging and error handling

Every accepted and rejected request is appended to `logs/recommendation_log.txt`. Invalid input returns a specific message instead of crashing.

### 4. Human evaluation (author review of console output)

Top-1 result judged on whether a listener with that profile would plausibly accept it.

| Test Input | Evaluation Criteria | Top Result (confidence) | Result |
|---|---|---|---|
| pop / happy / 0.8 | Sensible pop, happy song | Sunrise City (0.98) | Pass |
| lofi / chill / 0.4 | Sensible lofi, chill song | Midnight Coding (0.92) | Pass |
| rock / intense / 0.9 | Sensible rock, intense song | Storm Runner (0.99) | Pass |
| jazz / relaxed / 0.35 | Sensible jazz, relaxed song | Coffee Shop Stories (0.90) | Pass |
| classical / peaceful / 0.25 | Matches genre and mood | Paper Moonlight, mood dreamy (0.67) | Partial - mood differs, but close in feel |
| metal / peaceful / 0.95 | Handles conflicting preferences honestly | Iron Cathedral, mood angry (0.77) | Fail on ranking, but self-check now warns "No song in the catalog is both metal and peaceful" |
| classical / energetic / 0.9 | Handles conflicting preferences honestly | Warehouse Pulse, house (0.55) | Fail on ranking, but self-check now warns the catalog has no classical + energetic song |
| genre=edm | Rejects unknown genre gracefully | Rejection with valid options listed | Pass |
| energy=1.5 / -0.5 / "loud" | Rejects bad energy gracefully | Rejected with reason | Pass |
| missing genre key | Handles gracefully | Rejected, "Genre is required." | Pass |
| genre="Pop" (capitalized) | Same result as "pop" | Sunrise City (0.98) | Pass |

Human evaluation: 8 Pass, 1 Partial, 2 Fail out of 11 inputs. Both failures are conflicting-preference profiles the catalog cannot satisfy; they are now flagged to the user rather than silent.

### What worked, what didn't

**Worked:** All guardrails reject bad input cleanly; none of the adversarial profiles crashed the program.

**Didn't work initially:** Before guardrails, a missing `genre` key crashed with `KeyError`; energy `-0.5` produced a negative internal score; and `Pop`/`Happy` lost all genre and mood points because matching was case-sensitive. All three only appeared when probing with adversarial input.

**Learned:** A system can look correct on the profiles you happen to try and still be silently wrong elsewhere. Accuracy on conflicting profiles is still unfixed; the next step would be warning the user when top results ignore a stated preference.

---

## Limitations

- Only 18 songs in the catalog, most genres/moods represented by a single song — rankings can flip based on very small scoring differences.
- Genre and energy are correlated in this dataset (high-energy genres are all rock/metal/pop/house; low-energy genres are all lofi/classical/folk/ambient), so a profile like "peaceful metal" can never get a real genre match and a real energy match at the same time.
- Genre/mood matching is still exact-string (case-insensitive now, but `"pop"` and `"indie pop"` are still unrelated to the scorer).
- The self-check only warns; it does not re-rank or ask the user to resolve the conflict.
- No personalization or learning — every recommendation is stateless and based only on the stated profile, never on past feedback.

A deeper bias analysis, plus the graded responsible-AI reflection (how AI tools were used during development, one helpful and one flawed AI suggestion, and a fuller discussion of system limitations), is in [`model_card.md`](model_card.md).

---

## Reflection

Building the reliability layer changed how I think about what makes a "simple" system trustworthy. The scoring rule itself is just weighted addition, but wrapping it in guardrails, confidence scoring, explanations, and logging is what actually makes it usable by someone other than the person who wrote it — and, as it turned out, is also what exposed a real bug (case-sensitive matching) that pure scoring-logic testing had missed. The biggest takeaway: correctness and reliability are different properties. A scoring formula can be mathematically correct and still be an unreliable system if nothing checks its inputs, explains its outputs, or records what it did.

The full responsible-AI reflection — limitations and biases, potential misuse, reliability surprises, and how I collaborated with AI (one suggestion accepted, one changed) — is in [`model_card.md`](model_card.md).
