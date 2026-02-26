"""Songstats API client — cross-platform streaming analytics via RapidAPI.

Free tier: 1,000 resource hits/month, 10 concurrent requests.
Docs: https://docs.songstats.com/
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests
import streamlit as st

from services.config import get_secret

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
RAPIDAPI_HOST = "songstats.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}/artists"


def _headers() -> dict[str, str]:
    return {
        "X-RapidAPI-Key": get_secret("SONGSTATS_API_KEY"),
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }


def _api_get(endpoint: str, params: dict | None = None) -> dict[str, Any]:
    """Make authenticated GET to Songstats RapidAPI."""
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, headers=_headers(), params=params or {}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _load_static(filename: str) -> dict[str, Any]:
    """Load static fallback JSON file from data/ directory."""
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------------------
# Public API — each function returns data from API or static fallback
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def get_artist_stats(spotify_id: str = "", fallback_file: str = "songstats_jakke.json") -> dict[str, Any]:
    """Get comprehensive artist stats (streams, playlists, charts).

    Falls back to static JSON if API key not configured or request fails.
    """
    api_key = get_secret("SONGSTATS_API_KEY")
    if not api_key or not spotify_id:
        return _load_static(fallback_file)

    try:
        # Fetch overview stats
        info = _api_get("info", {"source": "spotify", "spotify_artist_id": spotify_id})
        stats = _api_get("stats", {"source": "spotify", "spotify_artist_id": spotify_id})

        # Normalize to match our static file format
        spotify_stats = stats.get("stats", {}).get("spotify", {})
        cross_platform = stats.get("stats", {}).get("cross_platform", {})

        return {
            "artist": info.get("artist_name", ""),
            "last_updated": "live",
            "spotify": {
                "total_streams": spotify_stats.get("streams_total", 0),
                "monthly_listeners": spotify_stats.get("monthly_listeners_current", 0),
                "followers": spotify_stats.get("followers_total", 0),
                "popularity_score": spotify_stats.get("popularity", 0),
                "current_playlists": spotify_stats.get("playlists_total", 0),
                "playlist_reach": spotify_stats.get("playlist_reach", 0),
            },
            "cross_platform": {
                "total_streams": cross_platform.get("streams_total", 0),
                "total_playlists": cross_platform.get("playlists_total", 0),
                "playlist_reach": cross_platform.get("playlist_reach", 0),
            },
            "track_popularity": stats.get("track_popularity", {}),
            "_source": "api",
        }
    except Exception as e:
        logger.warning("Songstats API failed, using static fallback: %s", e)
        return _load_static(fallback_file)


@st.cache_data(ttl=3600)
def get_artist_playlists(spotify_id: str = "", fallback_file: str = "songstats_jakke.json") -> list[dict]:
    """Get current playlists for an artist."""
    api_key = get_secret("SONGSTATS_API_KEY")
    if not api_key or not spotify_id:
        data = _load_static(fallback_file)
        return data.get("top_playlists", [])

    try:
        result = _api_get("playlists", {"source": "spotify", "spotify_artist_id": spotify_id})
        playlists = result.get("playlists", [])
        return [
            {"name": p.get("name", ""), "followers": p.get("followers", 0), "source": p.get("source", "spotify")}
            for p in playlists[:20]
        ]
    except Exception as e:
        logger.warning("Songstats playlists API failed: %s", e)
        data = _load_static(fallback_file)
        return data.get("top_playlists", [])


@st.cache_data(ttl=3600)
def get_jakke_stats() -> dict[str, Any]:
    """Convenience: get Jakke stats."""
    spotify_id = get_secret("JAKKE_SPOTIFY_ID")
    return get_artist_stats(spotify_id, "songstats_jakke.json")


@st.cache_data(ttl=3600)
def get_enjune_stats() -> dict[str, Any]:
    """Convenience: get Enjune stats."""
    spotify_id = get_secret("ENJUNE_SPOTIFY_ID")
    return get_artist_stats(spotify_id, "songstats_enjune.json")
