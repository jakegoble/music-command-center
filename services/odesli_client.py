"""Odesli/Songlink API client.

Generates universal "listen on..." links from a single platform URL.
Free, no auth required. Rate limit: 10 req/min (higher with API key).
Docs: https://odesli.co/
"""
from __future__ import annotations

import logging
from typing import Any

import requests
import streamlit as st

from services.config import get_secret

logger = logging.getLogger(__name__)

BASE_URL = "https://api.song.link/v1-alpha.1/links"


@st.cache_data(ttl=86400)
def get_universal_links(url: str) -> dict[str, Any] | None:
    """Given a platform URL (Spotify, Apple, etc.), return links to all platforms.

    Returns dict with keys: spotify, apple_music, youtube, deezer, tidal, etc.
    """
    if not url:
        return None

    params: dict[str, str] = {"url": url}
    api_key = get_secret("ODESLI_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Extract platform links
        links_by_platform = data.get("linksByPlatform", {})
        result: dict[str, str] = {}
        platform_map = {
            "spotify": "Spotify",
            "appleMusic": "Apple Music",
            "youtube": "YouTube",
            "youtubeMusic": "YouTube Music",
            "deezer": "Deezer",
            "tidal": "Tidal",
            "amazonMusic": "Amazon Music",
            "soundcloud": "SoundCloud",
            "pandora": "Pandora",
        }

        for key, label in platform_map.items():
            if key in links_by_platform:
                result[label] = links_by_platform[key].get("url", "")

        # Also include the page URL (universal link page)
        result["Universal Link"] = data.get("pageUrl", "")

        return result
    except Exception as e:
        logger.warning("Odesli lookup failed for %s: %s", url, e)
        return None


@st.cache_data(ttl=86400)
def get_links_by_isrc(isrc: str) -> dict[str, Any] | None:
    """Look up universal links by ISRC code (no platform URL needed)."""
    if not isrc or isrc == "—":
        return None

    # Odesli doesn't directly support ISRC, but we can construct a Spotify search URL
    # For now, use the entity lookup approach
    params: dict[str, str] = {"platform": "spotify", "type": "song", "id": isrc}
    api_key = get_secret("ODESLI_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(BASE_URL, params=params, timeout=15)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()

        links = data.get("linksByPlatform", {})
        result = {}
        for key in ["spotify", "appleMusic", "youtube", "deezer", "tidal", "amazonMusic"]:
            if key in links:
                result[key] = links[key].get("url", "")

        result["page_url"] = data.get("pageUrl", "")
        return result
    except Exception as e:
        logger.warning("Odesli ISRC lookup failed for %s: %s", isrc, e)
        return None


@st.cache_data(ttl=86400)
def get_links_for_spotify_track(spotify_url: str) -> dict[str, str]:
    """Convenience: get all platform links for a Spotify track URL."""
    result = get_universal_links(spotify_url)
    return result or {}


def is_available() -> bool:
    """Odesli is always available (no auth needed for basic use)."""
    return True
