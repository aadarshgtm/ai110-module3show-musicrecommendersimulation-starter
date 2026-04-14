# Reflection: Profile Comparison Notes

This file compares how VibeFinder 1.0 behaved across different user profiles and what those differences reveal about the algorithm.

---

## Profile 1 vs Profile 2: Happy Pop Lover vs Chill Lofi Student

**Happy Pop Lover** (genre=pop, mood=happy, energy=0.8):
- Top result: *Sunrise City* — pop, happy, energy 0.82. Near-perfect match on all three main features.
- Second result: *Gym Hero* — pop, intense, energy 0.93. Genre matched but mood did not. Still ranked #2 because the genre bonus (+2.0) is large enough to carry it even without a mood match.

**Chill Lofi Student** (genre=lofi, mood=chill, energy=0.38):
- Top result: *Library Rain* — lofi, chill, energy 0.35. Near-perfect.
- Second result: *Midnight Coding* — lofi, chill, energy 0.42. Almost identical score to #1, just slightly further from the energy target.

**What changed and why:** These two profiles produced completely non-overlapping top-5 lists. That makes sense — pop and lofi are stylistically opposite, and the genre weight ensures the catalog is effectively split into separate "pools." This is the algorithm working as intended.

**Takeaway:** For profiles where the genre is well-represented in the catalog (pop has 2 songs, lofi has 3), the system works well and the rankings feel accurate.

---

## Profile 2 vs Profile 3: Chill Lofi Student vs Intense Rock Fan

**Chill Lofi Student** top-5 energy range: 0.28 – 0.58 (all low-energy songs)
**Intense Rock Fan** top-5 energy range: 0.75 – 0.97 (all high-energy songs)

The energy field alone caused a complete reversal of which songs appear. A song like *Spacewalk Thoughts* (ambient, chill, energy 0.28) ranks #4 for the lofi profile because its mood matches, but would score near the bottom for the rock profile because its energy is 0.64 lower than the target.

**Takeaway:** Energy is the strongest *differentiator* between profiles that already share no genre. Genre determines the top, energy orders the middle and bottom of the list.

---

## Profile 3 vs Profile 4: Intense Rock Fan vs Edge Case (High Energy but Sad)

**Intense Rock Fan** (genre=rock, mood=intense, energy=0.92):
- Top result: *Storm Runner* — rock, intense, energy 0.91. Perfect.
- The rock catalog has only 1 song, so #2 onward falls to other high-energy genres (metal, pop).

**Edge Case — High Energy but Sad** (genre=indie, mood=sad, energy=0.9):
- Top result: *Broken Clocks* — indie, melancholy, energy 0.48.
- This is the interesting failure: the user wants high-energy SAD music, but that combination barely exists in the catalog. *Broken Clocks* won because the genre bonus (+2.0) is so powerful that it outweighed the energy mismatch penalty of 0.42 points.

**What changed:** Switching from a consistent profile (intense rock: genre, mood, and energy all point in the same direction) to a conflicting profile (high energy + sad: rare in music generally) broke the algorithm's output quality. The top result technically has the right genre but the wrong energy — the opposite of what the user wanted most.

**Takeaway for non-programmers:** Imagine telling a DJ "play something indie and sad but really high-energy." That's a confusing request because most sad indie songs are slow and mellow. The DJ (the algorithm) defaulted to "indie" as the most certain thing you said and gave you the closest indie song — even though it did not actually fit the high-energy part. This is why "Gym Hero" (a high-energy pop song) might keep showing up for "Happy Pop" users even when they want something more relaxed: the genre match is so strong that it overrides smaller differences in energy or mood.

---

## Overall Observations

1. **Genre dominance is real.** In every profile, the genre match was the deciding factor for the #1 slot. No other feature could overcome a missing genre match.
2. **Mood is a useful tiebreaker.** When two songs share the same genre, the one with the matching mood reliably ranked higher. This felt correct.
3. **Conflicting preferences expose the algorithm's limits.** The system has no way to tell the user "your preferences are uncommon — here's why the results may feel off." A real system would flag this.
4. **Dataset size matters enormously.** Genres with only one song (rock, metal, reggae, country) produced a predictable #1 result every time, then fell back to unrelated genres for positions #2–5. Expanding the catalog is the single most impactful improvement possible.

---

## Extension Findings (Optional Challenges)

### Challenge 1 — Advanced Song Features

Five new attributes were added to every song:

| Attribute | Range | What it captures |
|---|---|---|
| `popularity` | 0–100 | How chart-famous the song is |
| `release_decade` | 1980–2020 | The era the song comes from |
| `mood_tag` | string | Fine-grained emotion label (e.g. "euphoric", "nostalgic") |
| `instrumentalness` | 0–1 | 0 = fully vocal, 1 = fully instrumental |
| `liveness` | 0–1 | 0 = studio-clean, 1 = sounds like a live recording |

**What changed:** The "Nostalgic Jazz Lover" profile (which set `preferred_decade=2000`, `preferred_mood_tag=nostalgic`, `likes_instrumental=True`) correctly surfaced *Coffee Shop Stories* and *Moonlight Sonata Remix* — both nostalgic, instrumental, 2000s tracks — over other jazz songs that only matched genre and mood. Without these attributes, those two songs were indistinguishable from each other by the core algorithm.

**Key insight:** The new attributes only affect rankings when the user explicitly sets them. This means existing profiles work exactly as before. The new features act as opt-in refinements.

---

### Challenge 2 — Multiple Scoring Modes

Four modes were added, each shifting the weight distribution:

| Mode | Genre | Mood | Energy | Valence | Effect |
|---|---|---|---|---|---|
| `balanced` | 2.0 | 1.0 | 1.0 | 0.5 | Default — steady |
| `genre_first` | 4.0 | 0.5 | 0.5 | 0.25 | Genre almost entirely decides the ranking |
| `mood_first` | 0.75 | 3.5 | 0.5 | 0.5 | Emotional vibe overrides genre labels |
| `energy_focused` | 1.0 | 0.5 | 2.5 | 0.5 | Physical intensity drives everything |

**What changed for the "Happy Pop Lover" profile:**

- `genre_first`: *Sunrise City* and *Gym Hero* (both pop) still dominate #1 and #2, but the gap between them and everything else is even wider. Genre is now almost a wall.
- `mood_first`: *Rooftop Lights* (indie pop, happy) and *Golden Afternoon* (jazz, happy) climb into the top 2 because mood=happy now gives +3.5 points — more than a genre match. The algorithm stops caring as much about genre labels and responds to feelings.
- `energy_focused`: *Sunrise City* stays #1 (energy 0.82, very close to target 0.8), but *Gym Hero* drops to #3 because its energy 0.93 is farther from 0.8 than *Rooftop Lights* (energy 0.76). Pure proximity to the target energy determines the order.

**Key insight:** The same user profile can produce meaningfully different playlists just by changing the mode. This mirrors real platforms where users can switch between "mood radio," "artist radio," and "energy radio" — they're all the same underlying algorithm with different weight configurations.

---

### Challenge 3 — Diversity Penalty

**The problem it solves:** Without a diversity rule, the raw top-5 for "Happy Pop Lover" contained two pop songs and two songs by the same artist (*Neon Echo*). In a real app, users quickly notice when recommendations feel repetitive.

**How the reranker works:**
1. Score all 20 songs as normal (no cap).
2. Walk through the ranked list from best to worst.
3. Accept a song only if its genre hasn't appeared 2+ times and its artist hasn't appeared 1+ times.
4. Songs that breach the cap get their score multiplied by 0.6 (a 40% penalty) and are moved to the back.

**What changed:** In the diverse top-5, *Neon Frequency* (hip-hop, different artist) replaced the second *Neon Echo* song. The list now covers pop, indie pop, jazz, and hip-hop instead of two pop entries. The recommendations feel more varied without straying from the user's general taste area.

**Key insight:** Diversity constraints don't improve relevance — they trade some relevance for variety. Whether that tradeoff is worth it depends on the use case. A "Discover Weekly" playlist benefits from diversity; a "More of this exact song" feature does not.

---

### Challenge 4 — Visual Summary Table

All output now uses `tabulate` with the `fancy_grid` format, displaying columns: Rank, Title, Artist, Genre/Mood, Energy, Score, Top Reason. A plain-text fallback activates when `tabulate` isn't installed.

**Why this matters:** Before, each recommendation was 3 lines of loose text. With the table, a user can scan all 5 recommendations in one visual sweep and immediately compare scores. The "Top Reason" column makes the explanation visible without cluttering the row. This is a real UX difference — the information is the same, but the cognitive load of reading it drops significantly.
