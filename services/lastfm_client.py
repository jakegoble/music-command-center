"""Last.fm API client.

Provides listener counts, play counts, similar artists, and genre tags.
Free API key: https://www.last.fm/api/account/create
Docs: https://www.last.fm/api
"""
from __future__ import annotations

import logging
from typing import Any

import requests
import streamlit as st

from services.config import get_secret

logger = logging.getLogger(__name__)

BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def _api_get(method: str, params: dict | None = None) -> dict[str, Any]:
    """Make GET request to Last.fm API."""
    base_params = {
        "method": method,
        "api_key": get_secret("LASTFM_API_KEY"),
        "format": "json",
    }
    if params:
        base_params.update(params)
    resp = requests.get(BASE_URL, params=base_params, timeout=15)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=3600)
def get_artist_info(artist: str) -> dict[str, Any] | None:
    """Get artist info including listeners, playcount, bio, tags."""
    api_key = get_secret("LASTFM_API_KEY")
    if not api_key:
        return None

    try:
        data = _api_get("artist.getinfo", {"artist": artist})
        artist_data = data.get("artist", {})
        stats = artist_data.get("stats", {})
        tags = [t["name"] for t in artist_data.get("tags", {}).get("tag", [])]
        similar = [
            {"name": s["name"], "match": s.get("match", "")}
            for s in artist_data.get("similar", {}).get("artist", [])
        ]
        return {
            "name": artist_data.get("name", ""),
            "listeners": int(stats.get("listeners", 0)),
            "playcount": int(stats.get("playcount", 0)),
            "tags": tags,
            "similar_artists": similar,
            "bio_summary": artist_data.get("bio", {}).get("summary", ""),
            "url": artist_data.get("url", ""),
        }
    except Exception as e:
        logger.warning("Last.fm artist info failed: %s", e)
        return None


@st.cache_data(ttl=3600)
def get_top_tracks(artist: str, limit: int = 10) -> list[dict]:
    """Get top tracks for an artist by play count."""
    api_key = get_secret("LASTFM_API_KEY")
    if not api_key:
        return []

    try:
        data = _api_get("artist.gettoptracks", {"artist": artist, "limit": limit})
        tracks = data.get("toptracks", {}).get("track", [])
        return [
            {
                "name": t.get("name", ""),
                "playcount": int(t.get("playcount", 0)),
                "listeners": int(t.get("listeners", 0)),
                "url": t.get("url", ""),
            }
            for t in tracks
        ]
    except Exception as e:
        logger.warning("Last.fm top tracks failed: %s", e)
        return []


@st.cache_data(ttl=3600)
def get_similar_artists(artist: str, limit: int = 10) -> list[dict]:
    """Get similar artists (useful for audience discovery)."""
    api_key = get_secret("LASTFM_API_KEY")
    if not api_key:
        return []

    try:
        data = _api_get("artist.getsimilar", {"artist": artist, "limit": limit})
        similar = data.get("similarartists", {}).get("artist", [])
        return [
            {
                "name": s.get("name", ""),
                "match": float(s.get("match", 0)),
                "url": s.get("url", ""),
            }
            for s in similar
        ]
    except Exception as e:
        logger.warning("Last.fm similar artists failed: %s", e)
        return []


@st.cache_data(ttl=3600)
def get_track_info(artist: str, track: str) -> dict[str, Any] | None:
    """Get track-level info (listeners, playcount, tags)."""
    api_key = get_secret("LASTFM_API_KEY")
    if not api_key:
        return None

    try:
        data = _api_get("track.getinfo", {"artist": artist, "track": track})
        t = data.get("track", {})
        tags = [tag["name"] for tag in t.get("toptags", {}).get("tag", [])]
        return {
            "name": t.get("name", ""),
            "artist": t.get("artist", {}).get("name", ""),
            "listeners": int(t.get("listeners", 0)),
            "playcount": int(t.get("playcount", 0)),
            "tags": tags,
            "url": t.get("url", ""),
        }
    except Exception as e:
        logger.warning("Last.fm track info failed: %s", e)
        return None


def is_available() -> bool:
    """Check if Last.fm API is configured."""
    return bool(get_secret("LASTFM_API_KEY"))
