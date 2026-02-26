"""MusicBrainz API client.

Provides music metadata: ISRCs, release dates, recordings, artist identities.
Free, no auth required. Rate limit: 1 request/second.
Docs: https://musicbrainz.org/doc/MusicBrainz_API
"""
from __future__ import annotations

import logging
import time
from typing import Any

import requests
import streamlit as st

logger = logging.getLogger(__name__)

BASE_URL = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": "MusicCommandCenter/2.0 (jake@radanimal.co)", "Accept": "application/json"}

# Simple rate limiter
_last_request_time = 0.0


def _rate_limit() -> None:
    """Enforce 1 request/second rate limit."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_request_time = time.time()


def _api_get(endpoint: str, params: dict | None = None) -> dict[str, Any]:
    """Make GET request to MusicBrainz API."""
    _rate_limit()
    url = f"{BASE_URL}/{endpoint}"
    base_params = {"fmt": "json"}
    if params:
        base_params.update(params)
    resp = requests.get(url, params=base_params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=86400)
def search_artist(name: str) -> list[dict]:
    """Search for an artist by name. Returns list of matches."""
    try:
        data = _api_get("artist", {"query": name, "limit": 5})
        return [
            {
                "id": a.get("id", ""),
                "name": a.get("name", ""),
                "sort_name": a.get("sort-name", ""),
                "type": a.get("type", ""),
                "country": a.get("country", ""),
                "disambiguation": a.get("disambiguation", ""),
                "score": a.get("score", 0),
            }
            for a in data.get("artists", [])
        ]
    except Exception as e:
        logger.warning("MusicBrainz artist search failed: %s", e)
        return []


@st.cache_data(ttl=86400)
def get_artist_releases(artist_id: str) -> list[dict]:
    """Get all releases (albums/singles) for an artist MBID."""
    if not artist_id:
        return []

    try:
        data = _api_get(f"release-group", {"artist": artist_id, "limit": 100})
        return [
            {
                "id": rg.get("id", ""),
                "title": rg.get("title", ""),
                "type": rg.get("primary-type", ""),
                "first_release_date": rg.get("first-release-date", ""),
            }
            for rg in data.get("release-groups", [])
        ]
    except Exception as e:
        logger.warning("MusicBrainz releases failed: %s", e)
        return []


@st.cache_data(ttl=86400)
def get_recording_by_isrc(isrc: str) -> dict[str, Any] | None:
    """Look up a recording by ISRC code."""
    if not isrc or isrc == "—":
        return None

    try:
        data = _api_get(f"isrc/{isrc}")
        recordings = data.get("recordings", [])
        if not recordings:
            return None
        rec = recordings[0]
        return {
            "id": rec.get("id", ""),
            "title": rec.get("title", ""),
            "length_ms": rec.get("length", 0),
            "isrc": isrc,
            "artist_credit": [
                {"name": ac.get("name", ""), "artist_id": ac.get("artist", {}).get("id", "")}
                for ac in rec.get("artist-credit", [])
            ],
        }
    except Exception as e:
        logger.warning("MusicBrainz ISRC lookup failed for %s: %s", isrc, e)
        return None


@st.cache_data(ttl=86400)
def search_recording(title: str, artist: str = "") -> list[dict]:
    """Search for a recording by title and optional artist."""
    query = f'recording:"{title}"'
    if artist:
        query += f' AND artist:"{artist}"'

    try:
        data = _api_get("recording", {"query": query, "limit": 5})
        return [
            {
                "id": r.get("id", ""),
                "title": r.get("title", ""),
                "score": r.get("score", 0),
                "length_ms": r.get("length", 0),
                "isrcs": r.get("isrcs", []),
                "artist_credit": [
                    {"name": ac.get("name", "")}
                    for ac in r.get("artist-credit", [])
                ],
                "releases": [
                    {"title": rel.get("title", ""), "date": rel.get("date", "")}
                    for rel in r.get("releases", [])[:3]
                ],
            }
            for r in data.get("recordings", [])
        ]
    except Exception as e:
        logger.warning("MusicBrainz recording search failed: %s", e)
        return []


def is_available() -> bool:
    """MusicBrainz is always available (no auth needed)."""
    return True
