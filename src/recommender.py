import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Challenge 2: Scoring Modes
#
# Each mode is a dict of weight multipliers for the four core features.
# "balanced"      — default, equal weight to all four signals
# "genre_first"   — genre weight tripled; energy/mood reduced to tiebreakers
# "mood_first"    — emotional vibe drives everything; genre barely matters
# "energy_focused"— closeness to the target energy is the strongest signal
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 2.0,
        "mood":  1.0,
        "energy": 1.0,
        "valence": 0.5,
    },
    "genre_first": {
        "genre": 4.0,
        "mood":  0.5,
        "energy": 0.5,
        "valence": 0.25,
    },
    "mood_first": {
        "genre": 0.75,
        "mood":  3.5,
        "energy": 0.5,
        "valence": 0.5,
    },
    "energy_focused": {
        "genre": 1.0,
        "mood":  0.5,
        "energy": 2.5,
        "valence": 0.5,
    },
}

MODE_DESCRIPTIONS: Dict[str, str] = {
    "balanced":      "Equal weight to genre, mood, energy, and valence.",
    "genre_first":   "Genre dominates; everything else is a tiebreaker.",
    "mood_first":    "Emotional vibe drives ranking; genre barely matters.",
    "energy_focused":"Songs closest to the target energy score highest.",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and all its audio/metadata attributes."""
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
    # Challenge 1: five new advanced attributes (defaults keep old tests working)
    popularity: int = 50          # chart popularity 0–100
    release_decade: int = 2020    # decade of release: 1980, 1990, 2000, 2010, 2020
    mood_tag: str = ""            # detailed mood label e.g. "euphoric", "nostalgic"
    instrumentalness: float = 0.0 # 0 = fully vocal, 1 = fully instrumental
    liveness: float = 0.0         # 0 = studio, 1 = sounds like a live recording


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Challenge 1: optional extended preference fields (None = no preference)
    target_popularity: Optional[int] = None
    preferred_decade: Optional[int] = None
    preferred_mood_tag: Optional[str] = None
    likes_instrumental: Optional[bool] = None
    target_liveness: Optional[float] = None


# ---------------------------------------------------------------------------
# Functional API  (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with all numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # core numeric fields
            row["id"]           = int(row["id"])
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            # Challenge 1: new numeric fields (safe fallbacks for old CSV files)
            row["popularity"]       = int(float(row.get("popularity") or 50))
            row["release_decade"]   = int(float(row.get("release_decade") or 2020))
            row["mood_tag"]         = row.get("mood_tag", "")
            row["instrumentalness"] = float(row.get("instrumentalness") or 0.0)
            row["liveness"]         = float(row.get("liveness") or 0.0)
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, str]:
    """
    Score one song against user preferences using the specified scoring mode.
    Returns (total_score, explanation_string).
    """
    weights = SCORING_MODES[mode]
    score = 0.0
    reasons: List[str] = []

    # ── Core features (weights vary by mode) ──────────────────────────────────

    # Genre match: strongest categorical signal
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        pts = weights["genre"]
        score += pts
        reasons.append(f"genre match (+{pts})")

    # Mood match: emotional vibe
    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        pts = weights["mood"]
        score += pts
        reasons.append(f"mood match (+{pts})")

    # Energy similarity: reward closeness to target, not highest/lowest value
    energy_pts = round(
        (1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))) * weights["energy"], 2
    )
    score += energy_pts
    reasons.append(f"energy similarity (+{energy_pts:.2f})")

    # Valence similarity: how "positive/bright" the song feels
    valence_pts = round(
        (1.0 - abs(song["valence"] - user_prefs.get("valence", 0.5))) * weights["valence"], 2
    )
    score += valence_pts
    reasons.append(f"valence match (+{valence_pts:.2f})")

    # ── Challenge 1: Advanced feature bonuses (only if user set a preference) ─

    # Popularity: up to +0.5 points based on proximity to target
    if user_prefs.get("target_popularity") is not None:
        pop_pts = round(
            0.5 * (1.0 - abs(song["popularity"] - user_prefs["target_popularity"]) / 100), 2
        )
        score += pop_pts
        reasons.append(f"popularity match (+{pop_pts:.2f})")

    # Release decade: exact match earns +0.5
    if user_prefs.get("preferred_decade") is not None:
        if song["release_decade"] == user_prefs["preferred_decade"]:
            score += 0.5
            reasons.append("decade match (+0.5)")

    # Detailed mood tag: more specific than mood, exact match earns +0.5
    if user_prefs.get("preferred_mood_tag"):
        if song["mood_tag"].lower() == user_prefs["preferred_mood_tag"].lower():
            score += 0.5
            reasons.append("mood-tag match (+0.5)")

    # Instrumentalness preference: up to +0.3 points
    if user_prefs.get("likes_instrumental") is not None:
        if user_prefs["likes_instrumental"]:
            inst_pts = round(song["instrumentalness"] * 0.3, 2)
        else:
            inst_pts = round((1.0 - song["instrumentalness"]) * 0.3, 2)
        score += inst_pts
        reasons.append(f"instrumental pref (+{inst_pts:.2f})")

    # Liveness preference: up to +0.3 points based on proximity
    if user_prefs.get("target_liveness") is not None:
        live_pts = round(
            (1.0 - abs(song["liveness"] - user_prefs["target_liveness"])) * 0.3, 2
        )
        score += live_pts
        reasons.append(f"liveness match (+{live_pts:.2f})")

    return round(score, 2), " | ".join(reasons)


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, mode: str = "balanced"
) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top-k results sorted highest to lowest."""
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]
    # sorted() returns a new list; .sort() would modify the original in place
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]


def diversity_rerank(
    results: List[Tuple], max_per_genre: int = 2, max_per_artist: int = 1
) -> List[Tuple]:
    """
    Challenge 3: Re-rank results to prevent genre/artist over-representation.

    How it works:
    - Walk through the already-ranked list from highest to lowest score.
    - Accept a song into the "diverse" list only if its genre hasn't appeared
      max_per_genre times yet AND its artist hasn't appeared max_per_artist times.
    - Songs that breach either limit are penalized (score × 0.6) and pushed to
      the back of the final list, re-sorted among themselves.

    This forces the top-5 to contain a variety of genres and artists even when
    one genre dominates the raw scores.
    """
    genre_count: Dict[str, int] = {}
    artist_count: Dict[str, int] = {}
    primary: List[Tuple] = []
    penalized: List[Tuple] = []

    for song, score, explanation in results:
        genre  = song["genre"]
        artist = song["artist"]
        genre_ok  = genre_count.get(genre, 0)  < max_per_genre
        artist_ok = artist_count.get(artist, 0) < max_per_artist

        if genre_ok and artist_ok:
            primary.append((song, score, explanation))
            genre_count[genre]   = genre_count.get(genre, 0) + 1
            artist_count[artist] = artist_count.get(artist, 0) + 1
        else:
            reasons = []
            if not genre_ok:
                reasons.append(f"genre '{genre}' cap reached ({max_per_genre})")
            if not artist_ok:
                reasons.append(f"artist '{artist}' already picked")
            new_score = round(score * 0.6, 2)
            penalized.append(
                (song, new_score, explanation + f"  ⚠ diversity penalty ({', '.join(reasons)})")
            )

    penalized.sort(key=lambda x: x[1], reverse=True)
    return primary + penalized


# ---------------------------------------------------------------------------
# OOP API  (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP wrapper around the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Compute a numeric score for a Song dataclass against a UserProfile."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.0
        score += 1.0 - abs(song.energy - user.target_energy)
        if user.likes_acoustic:
            score += song.acousticness * 0.5
        else:
            score += (1.0 - song.acousticness) * 0.25
        # Challenge 1 bonuses (only when the UserProfile specifies a preference)
        if user.target_popularity is not None:
            score += 0.5 * (1.0 - abs(song.popularity - user.target_popularity) / 100)
        if user.preferred_decade is not None and song.release_decade == user.preferred_decade:
            score += 0.5
        if user.preferred_mood_tag and song.mood_tag.lower() == user.preferred_mood_tag.lower():
            score += 0.5
        if user.likes_instrumental is not None:
            score += song.instrumentalness * 0.3 if user.likes_instrumental \
                     else (1.0 - song.instrumentalness) * 0.3
        if user.target_liveness is not None:
            score += (1.0 - abs(song.liveness - user.target_liveness)) * 0.3
        return round(score, 2)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Songs sorted by score for the given UserProfile."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why this song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append("genre match (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append("mood match (+1.0)")
        energy_pts = round(1.0 - abs(song.energy - user.target_energy), 2)
        reasons.append(f"energy similarity (+{energy_pts:.2f})")
        if user.likes_acoustic:
            reasons.append(f"acoustic preference (+{round(song.acousticness * 0.5, 2):.2f})")
        if user.preferred_mood_tag and song.mood_tag.lower() == user.preferred_mood_tag.lower():
            reasons.append("mood-tag match (+0.5)")
        return " | ".join(reasons) if reasons else "no strong match"
