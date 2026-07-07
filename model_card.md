# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

It finds songs that match your "vibe" — your genre, mood, and energy level.

---

## 2. Intended Use

VibeFinder suggests songs based on three things you tell it: your favorite genre, your favorite mood, and how much energy you want right now. It also lets you say whether you like acoustic sound or not.

It's a classroom project, not a real product. It has no user accounts, no listening history, and no way to learn from your feedback over time. Every recommendation only looks at the song's own attributes compared to what you typed in.

It assumes you type your genre and mood the exact way the catalog does (lowercase, exact spelling) and that your energy is a number between 0 and 1. It does not assume anything about your age, location, or listening history, because it doesn't collect any of that.

**Not intended for:** real-world use, people who type genres with different capitalization or spelling than the catalog, or anyone who wants their taste to be "learned" over time. It also shouldn't be trusted for someone whose favorite genre and favorite energy level don't naturally go together (see Limitations below).

---

## 3. How the Model Works

Every song gets a score built from four things:

- **Genre match — worth 2 points.** If the song's genre is exactly the same word as your favorite genre, it gets 2 points. If not, 0.
- **Mood match — worth 1 point.** Same idea, but for mood.
- **Energy closeness — worth up to 1 point.** The closer the song's energy is to the energy you asked for, the more points it gets. A perfect match is 1 point.
- **Acousticness match — worth up to 0.5 points.** If you said you like acoustic songs, more acoustic songs score higher. If you didn't, more electronic/produced songs score higher.

Add all four up, and that's the song's score. The app scores every song in the catalog, sorts them highest to lowest, and shows you the top 5, along with a plain-English list of why each one scored what it did.

Genre is worth the most points, so a genre match can beat a much better mood or energy match. I left out tempo, valence, and danceability from the scoring — in this catalog they closely track energy already, so adding them would mostly just count the same signal twice.

I did try one change from the starter logic: doubling the energy weight and halving the genre weight, to see how sensitive the rankings were. It changed the order of the top 5 (see [Experiments You Tried](README.md#experiments-you-tried) in the README), but I kept the original 2.0/1.0/1.0/0.5 weights for the shipped version, since that's what the rest of this model card and my evaluation are based on.

---

## 4. Data

The catalog is `data/songs.csv` — 18 songs, used as-is with nothing added or removed. Each song has: title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.

The genres are spread thin: pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, country, metal, folk, latin, house, blues, and classical. Most genres only have one song — lofi has the most, with three. Moods are similar: happy, chill, intense, moody, focused, romantic, nostalgic, angry, peaceful, playful, energetic, melancholic, dreamy, and relaxed — almost every mood belongs to just one song.

Energy ranges from 0.25 (classical) to 0.97 (metal). Notably, there's no low-energy pop/rock song and no high-energy classical/folk song in the catalog at all.

With only 18 songs and mostly one song per genre or mood, this catalog can't really represent real musical taste. There's no rap, no k-pop, no electronic subgenres, and most niches only get one song to make a good impression.

---

## 5. Strengths

It works best for the "obvious" listener — someone whose favorite genre, mood, and energy actually line up with a real song in the catalog. The starter profile (pop, happy, energy 0.8) is a good example: Sunrise City is a genuinely great match, and it correctly comes out on top.

The energy-closeness math also behaves the way I'd expect — someone who asks for low energy gets chill songs, not the most intense ones in the catalog.

The explanations are honest. They always show exactly which parts of the score came from genre, mood, energy, or acousticness, so I can trace why a song ranked where it did instead of just trusting a black-box number.

---

## 6. Limitations and Bias

**Genre and energy are linked in this catalog, which creates a filter bubble.** High-energy genres (rock, metal, pop, house) are all above 0.75 energy. Low-energy genres (lofi, classical, folk, ambient) are all below 0.45. No song pairs a "typical" genre with an atypical energy level. So if you ask for something like "energetic classical" or "peaceful metal," the system can never give you a real genre match and a real energy match at the same time — it always drops one to satisfy the other. Listeners with unusual combinations of taste get pushed toward generic, energy-matched filler instead of a song that fits everything they asked for. The code doesn't cause this, the small dataset does, but the code also never tells you when it's happening — you just get a top 5 that quietly ignored half of what you asked for.

Two smaller issues showed up during testing too:

- **Genre dominance.** The +2.0 genre weight is so big that a song with the wrong mood and a mediocre energy fit can still outrank a song with a great mood and energy fit but a different genre label.
- **Exact-string matching is brittle.** "pop" and "Pop" are treated as two completely unrelated genres, and so are "pop" and "indie pop." A tiny typo or capitalization difference can knock a song's score down by 2 to 3 points.

---

## 7. Evaluation

### Profiles Tested

I ran `python -m src.main` with 10 profiles: the starter "Happy Pop" profile, plus 9 profiles designed to try to break the scoring. These tested a genre/mood/energy conflict, a genre that doesn't exist in the catalog, energy above 1 and below 0, the same real preferences typed with different capitalization, a second conflicting profile that also wanted acoustic sound, a profile missing the genre field, a profile with extra unrelated fields, and a profile with empty genre and mood.

### What Surprised Me

Genre matching is weighted so heavily that it wins the top spot even when the mood is completely wrong. Capitalization alone ("Pop" vs "pop") was enough to totally change the top 5. And when I pushed energy below the valid range, one song's energy score actually went negative — the math has no floor built in.

### Comparing Profiles

- **pop/happy vs. Pop/Happy** — same real preferences, different capitalization. The capitalized version loses every genre and mood point, so the #1 song completely changes. This is also why "Gym Hero" shows up for "Happy Pop" listeners even though its real mood is "intense" — it still gets full genre credit and a decent energy score.
- **metal/peaceful vs. classical/energetic** — both ask for a genre/mood combo that doesn't exist together in the catalog. In both cases, the genre match still wins #1 and the mood is completely ignored.
- **edm (fake genre) vs. empty genre/mood** — removing genre still leaves mood to guide the results somewhere reasonable. Removing genre *and* mood leaves the system with nothing personal to go on, so the results turn into generic energy-matched filler.
- **energy=1.5 vs. energy=-0.5** — pushing energy out of range in either direction still lets genre and mood carry the top songs, but at -0.5 one song's energy score actually goes negative.
- **missing genre key vs. extra unrelated keys** — the missing key crashes the whole program with an error. The extra keys are silently ignored and change nothing.

---

## 8. Future Work

- Let genre partially match related genres (like "pop" and "indie pop") instead of an all-or-nothing exact match.
- Clamp the energy input to 0–1 so the score can never go negative.
- Warn the user when their stated preferences conflict with each other (like "peaceful metal"), instead of silently picking a winner and hiding the tradeoff.

---

## 9. Personal Reflection

My biggest learning moment was realizing how much a single weight — the +2.0 genre bonus — can control the entire outcome. I assumed a "recommendation" needed something more complicated than addition, but a handful of weighted if-statements already feels surprisingly personal.

AI tools helped me the most with generating adversarial test profiles I wouldn't have thought of myself, like out-of-range energy values and missing keys. I still had to double-check the actual math by running the code myself — for example, I expected `energy=1.5` to break the scoring by going negative, but the dataset's highest energy song (0.97) meant the gap never got big enough for that to actually happen. I only caught that by running it, not by trusting the prediction.

What surprised me most is how "smart" this simple system can feel even though it's just addition and string comparison. Sunrise City topping the list for a Happy Pop fan feels like a real recommendation, even though under the hood it's just four numbers added together.

If I kept extending this, I'd try fuzzy genre matching, add a way to flag conflicting preferences instead of silently resolving them, and let a user rate the results so the weights could adjust over time instead of staying fixed forever.
