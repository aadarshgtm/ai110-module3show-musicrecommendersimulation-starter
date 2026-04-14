"""
Command-line runner for the Music Recommender Simulation.
Demonstrates all four optional extensions.

Run with:
    python -m src.main
"""

try:
    from recommender import (
        load_songs, recommend_songs, diversity_rerank,
        SCORING_MODES, MODE_DESCRIPTIONS,
    )
except ModuleNotFoundError:
    from src.recommender import (
        load_songs, recommend_songs, diversity_rerank,
        SCORING_MODES, MODE_DESCRIPTIONS,
    )

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# ---------------------------------------------------------------------------
# User profiles  (standard — used throughout all sections)
# ---------------------------------------------------------------------------
PROFILES = {
    "Happy Pop Lover": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.85,
    },
    "Chill Lofi Student": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
    },
    "Intense Rock Fan": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "valence": 0.40,
    },
    "Edge Case — High Energy but Sad": {
        "genre": "indie",
        "mood": "sad",
        "energy": 0.90,
        "valence": 0.25,
    },
}

# Challenge 1: extended profiles that also specify the 5 new preference fields
EXTENDED_PROFILES = {
    "Nostalgic Jazz Lover": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.40,
        "valence": 0.70,
        # --- new fields ---
        "target_popularity": 50,       # prefers mid-popularity (not mainstream)
        "preferred_decade": 2000,      # loves early-2000s releases
        "preferred_mood_tag": "nostalgic",
        "likes_instrumental": True,    # wants instrumental tracks
        "target_liveness": 0.40,       # likes a slight live feel
    },
    "Mainstream EDM Fan": {
        "genre": "edm",
        "mood": "euphoric",
        "energy": 0.95,
        "valence": 0.80,
        # --- new fields ---
        "target_popularity": 90,       # only wants chart-toppers
        "preferred_decade": 2020,
        "preferred_mood_tag": "euphoric",
        "likes_instrumental": True,    # EDM is mostly instrumental
        "target_liveness": 0.08,       # prefers clean studio sound
    },
}


# ---------------------------------------------------------------------------
# Output helpers  (Challenge 4: tabulate table)
# ---------------------------------------------------------------------------

def sep(char: str = "─", width: int = 70) -> None:
    print(char * width)


def print_table(recommendations: list) -> None:
    """Challenge 4 — print results as a formatted table using tabulate."""
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        top_reason = explanation.split(" | ")[0]          # first reason only
        rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{song['energy']:.2f}",
            f"{score:.2f}",
            top_reason,
        ])
    headers = ["Rank", "Title", "Artist", "Genre / Mood", "Energy", "Score", "Top Reason"]
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    else:
        # Fallback plain-text table when tabulate is not installed
        col_w = [5, 26, 18, 22, 8, 7, 32]
        header_row = "  ".join(h.ljust(w) for h, w in zip(headers, col_w))
        print(header_row)
        print("-" * len(header_row))
        for row in rows:
            print("  ".join(str(c).ljust(w) for c, w in zip(row, col_w)))
    print()


def print_section_header(number: int, title: str, subtitle: str = "") -> None:
    sep("═")
    print(f"  SECTION {number}: {title}")
    if subtitle:
        print(f"  {subtitle}")
    sep("═")
    print()


def print_profile_header(name: str, prefs: dict, mode: str = "balanced") -> None:
    sep()
    print(f"  Profile : {name}")
    print(f"  Mode    : {mode}  —  {MODE_DESCRIPTIONS[mode]}")
    g = prefs.get("genre", "-")
    m = prefs.get("mood", "-")
    e = prefs.get("energy", "-")
    extra = ""
    if prefs.get("preferred_decade"):
        extra += f"  decade={prefs['preferred_decade']}"
    if prefs.get("preferred_mood_tag"):
        extra += f"  tag={prefs['preferred_mood_tag']}"
    if prefs.get("target_popularity") is not None:
        extra += f"  popularity~{prefs['target_popularity']}"
    print(f"  Prefs   : genre={g}, mood={m}, energy={e}{extra}")
    sep()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs.\n")

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Standard profiles, balanced mode
    # ════════════════════════════════════════════════════════════════════════
    print_section_header(
        1, "Standard Profiles (balanced mode)",
        "Four user profiles scored with default weights: genre=2.0, mood=1.0, energy=1.0, valence=0.5"
    )
    for name, prefs in PROFILES.items():
        print_profile_header(name, prefs, mode="balanced")
        results = recommend_songs(prefs, songs, k=5, mode="balanced")
        print_table(results)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Challenge 1: Extended profiles with 5 new features
    #
    # The 5 new attributes added to songs.csv:
    #   popularity      (0–100)   — chart fame of the song
    #   release_decade  (decade)  — era the song was released in
    #   mood_tag        (string)  — fine-grained mood label (e.g. "euphoric")
    #   instrumentalness(0–1)     — 0=fully vocal, 1=fully instrumental
    #   liveness        (0–1)     — 0=studio-clean, 1=sounds live
    #
    # These earn bonus points only when the user_prefs dict includes them.
    # A "Nostalgic Jazz Lover" who likes instrumentals and 2000s releases will
    # score songs like "Coffee Shop Stories" (jazz, 2000, nostalgic, instrumental)
    # much higher than a plain genre+mood match would.
    # ════════════════════════════════════════════════════════════════════════
    print_section_header(
        2, "Challenge 1 — Advanced Song Features",
        "New scoring: popularity match (+0–0.5) | decade match (+0.5) | "
        "mood-tag match (+0.5) | instrumental pref (+0–0.3) | liveness match (+0–0.3)"
    )
    for name, prefs in EXTENDED_PROFILES.items():
        print_profile_header(name, prefs, mode="balanced")
        results = recommend_songs(prefs, songs, k=5, mode="balanced")
        print_table(results)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Challenge 2: Scoring mode comparison
    #
    # All four modes run on the same "Happy Pop Lover" profile so you can
    # directly compare how changing the weights shifts the rankings.
    #
    #  balanced      — genre=2.0  mood=1.0  energy=1.0  valence=0.5
    #  genre_first   — genre=4.0  mood=0.5  energy=0.5  valence=0.25
    #  mood_first    — genre=0.75 mood=3.5  energy=0.5  valence=0.5
    #  energy_focused— genre=1.0  mood=0.5  energy=2.5  valence=0.5
    # ════════════════════════════════════════════════════════════════════════
    print_section_header(
        3, "Challenge 2 — Scoring Mode Comparison",
        "Same profile (Happy Pop Lover) run through all 4 modes — watch how the rankings shift"
    )
    pop_prefs = PROFILES["Happy Pop Lover"]
    for mode_name in SCORING_MODES:
        print_profile_header("Happy Pop Lover", pop_prefs, mode=mode_name)
        results = recommend_songs(pop_prefs, songs, k=5, mode=mode_name)
        print_table(results)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Challenge 3: Diversity penalty
    #
    # Without diversity: the raw top-5 can be dominated by one genre or artist.
    # With diversity:    max 2 songs per genre, max 1 song per artist.
    #   Songs that breach the cap get their score multiplied by 0.6 and are
    #   pushed to the back of the result list so more variety surfaces.
    # ════════════════════════════════════════════════════════════════════════
    print_section_header(
        4, "Challenge 3 — Diversity Penalty",
        "Prevents the same genre/artist from dominating the top-5  "
        "(max 2 per genre, max 1 per artist)"
    )

    # Score ALL songs so the diversity reranker has the full picture
    all_scored = recommend_songs(pop_prefs, songs, k=len(songs), mode="balanced")
    diverse    = diversity_rerank(all_scored, max_per_genre=2, max_per_artist=1)

    sep()
    print("  Happy Pop Lover — RAW top-5  (no diversity constraint)")
    sep()
    print_table(all_scored[:5])

    sep()
    print("  Happy Pop Lover — DIVERSE top-5  (genre cap=2, artist cap=1)")
    sep()
    print_table(diverse[:5])

    print("  Songs that were penalized and pushed down:")
    sep("-", 50)
    penalized = [r for r in diverse if "diversity penalty" in r[2]]
    for song, score, explanation in penalized[:5]:
        note = explanation.split("⚠")[-1].strip() if "⚠" in explanation else ""
        print(f"    {song['title']} ({song['genre']})  →  penalized score: {score:.2f}  [{note}]")
    print()


if __name__ == "__main__":
    main()
