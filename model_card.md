# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommendation simulator built for classroom exploration.

---

## 2. Intended Use

VibeFinder is designed to suggest songs from a small catalog that best match a user's stated genre, mood, energy level, and positivity preference. It is meant for educational purposes — to demonstrate how a real music recommender works under the hood — and is **not** intended to be deployed for actual users.

**What it is for:**
- Understanding how audio features map to recommendations.
- Experimenting with scoring weights and bias.
- Classroom demonstration of content-based filtering.

**What it is NOT for:**
- Real music discovery (catalog is only 20 songs).
- Replacing collaborative filtering systems that learn from listening history.
- Making recommendations for users who have not explicitly provided preferences.

---

## 3. How the Model Works

VibeFinder scores every song in its catalog against the user's preferences and returns the top results.

Here is the scoring logic in plain language:

1. **Genre match** earns the most points (+2.0). Genre is the strongest single predictor of enjoyment, so it carries the highest weight.
2. **Mood match** earns the second-most points (+1.0). Whether a song feels happy, sad, chill, or intense matters a lot but slightly less than genre.
3. **Energy similarity** earns up to +1.0. A song with energy 0.82 scores almost perfectly for a user targeting 0.8, while a song at 0.4 scores only 0.6 on this dimension.
4. **Valence similarity** earns up to +0.5. Valence measures how "positive" or "upbeat" a song sounds. It acts as a fine-tuning factor.

Once every song has a total score, the list is sorted from highest to lowest. The top 5 songs are returned, each with a plain-language explanation of why it ranked where it did.

The maximum possible score is 4.5.

---

## 4. Data

- **Catalog size:** 20 songs (10 from the original starter, 10 added to cover new genres).
- **Original features per song:** id, title, artist, genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1).
- **5 new advanced features added (Challenge 1):**
  - `popularity` (0–100) — chart fame of the song
  - `release_decade` (1980/1990/2000/2010/2020) — the era it comes from
  - `mood_tag` (string) — fine-grained emotion label e.g. "euphoric", "nostalgic", "dreamy"
  - `instrumentalness` (0–1) — 0 = fully vocal, 1 = fully instrumental
  - `liveness` (0–1) — 0 = studio-clean, 1 = sounds like a live recording
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, hip-hop, classical, metal, r&b, folk, reggae, edm, indie.
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, energetic, calm, romantic, nostalgic, euphoric, melancholy, sad.
- **Limitations:** The dataset was created manually and reflects a Western, English-language, contemporary music bias. It has no songs from K-pop, Latin, Afrobeats, or Bollywood, for example. The creator's personal taste likely influenced which genres were included.

---

## 5. Strengths

- **Explainability:** Every recommendation comes with a specific reason (e.g., "genre match (+2.0) | mood match (+1.0)"), making it easy to understand why a song was picked.
- **Works without user history:** Unlike Netflix-style collaborative filtering, VibeFinder does not need any prior listening data to produce a result.
- **Clear genre separation:** For very different profiles (pop fan vs. lofi student vs. metal fan), the top-5 lists are completely non-overlapping, which shows the system does meaningfully differentiate between taste types.
- **Fast and transparent:** The algorithm is simple enough to trace by hand, which makes it great for teaching.

---

## 6. Limitations and Bias

- **Genre dominance:** The +2.0 genre bonus is so large that a mediocre genre match will outrank a nearly-perfect match in all other dimensions. This creates a filter bubble where users are always steered toward their stated genre, even if they might enjoy something adjacent.
- **Exact string matching:** "indie pop" and "pop" are treated as completely different genres. A pop fan will score zero genre points on "Rooftop Lights" even though most pop fans would enjoy it.
- **Dataset imbalance:** Pop and lofi have the most songs (3 each). A user who likes jazz or reggae only has 1–2 songs that could ever match perfectly, limiting variety.
- **No learning:** The model never adjusts based on whether the user actually liked the recommendations. Every session starts from scratch.
- **Conflicting preferences are not handled gracefully:** A user who wants high energy (0.9) AND a sad mood will get poor results because few songs combine those features. The system does not warn the user or adjust its strategy.
- **Tempo and danceability are collected but unused:** These features sit in the CSV but are never incorporated into the score, which means two songs can score identically even if one has a much more suitable tempo.

---

## 7. Evaluation

**Profiles tested:**

| Profile | Top Result | Felt Right? |
|---|---|---|
| Happy Pop Lover (genre=pop, mood=happy, energy=0.8) | Sunrise City | Yes — exact pop/happy match, high energy |
| Chill Lofi Student (genre=lofi, mood=chill, energy=0.38) | Library Rain | Yes — two lofi/chill songs tied at the top |
| Intense Rock Fan (genre=rock, mood=intense, energy=0.92) | Storm Runner | Yes — the only rock/intense song in catalog |
| Edge Case — High Energy but Sad (genre=indie, mood=sad, energy=0.9) | Broken Clocks (indie, melancholy, energy=0.48) | Partially — genre matched, but energy was far off |

**What surprised me:** The edge-case profile exposed the genre dominance problem clearly. `Broken Clocks` has energy 0.48, nearly half the user's target of 0.9. Yet it ranked #1 because the genre bonus alone was worth more than the entire energy penalty. In a real system, this would feel like a very wrong recommendation.

**Experiment — Halving the genre weight:** When the genre bonus was reduced from +2.0 to +1.0 and energy similarity was doubled, `Rooftop Lights` (indie pop) climbed from #3 to #2 for the pop profile, beating `Gym Hero`. This confirmed that the genre weight was the primary driver of rankings, not a combination of features.

---

## 8. Future Work

The four optional extensions were already implemented (scoring modes, diversity penalty, advanced features, visual table). The next meaningful improvements would be:

1. **Fuzzy genre matching:** Build a genre similarity map so that "indie pop" scores partial credit under a "pop" preference, and "metal" scores partial credit under "rock." This is the single biggest source of unfairness currently — exact string matching is too rigid.
2. **Use tempo and danceability in scoring:** Both fields are in the CSV but unused by the scorer. A tempo similarity score (rewarding proximity to a target BPM) would differentiate two happy pop songs with very different energetic feelings.
3. **Feedback loop:** Let the user rate each recommendation (thumbs up/down) and slowly shift the mode weights in response. Over time the system would learn that this specific user values mood more than genre, without the user having to manually pick a scoring mode.

---

## 9. Personal Reflection

**Biggest learning moment:** Building VibeFinder made clear how much power a single design decision holds over every outcome. I chose to give genre a +2.0 weight because it felt like the most obvious indicator of taste — and for typical profiles that was true. But the moment I tested the adversarial "High Energy but Sad" profile, the genre weight turned from a strength into a problem: it dragged the system toward a genre match and ignored a massive energy mismatch. A number I picked in 30 seconds shaped every single result the system ever produces.

**How AI tools helped, and when I had to double-check:** AI tools (like Copilot) were most useful for generating boilerplate — the CSV loading logic, the dataclass definitions, the tabulate formatting. They saved a lot of time on mechanical code. Where I had to be careful was the scoring logic itself: the AI's first suggestion scored the highest-energy song the most points, which is the opposite of what a proximity-based recommender should do. I had to redirect it toward `1.0 - abs(song.energy - target_energy)` instead. The AI got the structure right but not the math intent — that required human judgment.

**What surprised me about simple algorithms:** What surprised me most was how a 20-song, 40-line algorithm can still *feel* like a real recommender when the profile fits the data well. The "Chill Lofi Student" output looked genuinely good — two lofi/chill songs at the top, ambient third. It only breaks down at the edges. Real Spotify is probably doing something similarly structural underneath thousands of layers of complexity.

**What I would try next:** The first thing I would add is fuzzy genre matching — a small lookup table that gives "indie pop" partial credit under a "pop" search. That single change would fix the biggest unfairness in the current system without touching any of the scoring math.
