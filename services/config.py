"""Centralized secrets and configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass

import streamlit as st


def get_secret(key: str, default: str = "") -> str:
    """Get secret from st.secrets, then env var, then default."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        return os.environ.get(key, default)


def is_configured(key: str) -> bool:
    """Check if a secret/API key is available."""
    return bool(get_secret(key))


@dataclass
class APIStatus:
    """Status of an API connection."""
    name: str
    configured: bool
    live: bool = False
    error: str = ""


def get_all_api_status() -> list[APIStatus]:
    """Return configuration status of all API integrations."""
    apis = [
        ("Songstats (RapidAPI)", "SONGSTATS_API_KEY"),
        ("Spotify", "SPOTIFY_CLIENT_ID"),
        ("Instagram Graph API", "INSTAGRAM_ACCESS_TOKEN"),
        ("YouTube Data API", "YOUTUBE_API_KEY"),
        ("Last.fm", "LASTFM_API_KEY"),
        ("MusicBrainz", "_always_free_"),
        ("Odesli/Songlink", "_always_free_"),
    ]
    results = []
    for name, key in apis:
        if key.startswith("_"):
            results.append(APIStatus(name=name, configured=True, live=True))
        else:
            results.append(APIStatus(name=name, configured=is_configured(key)))
    return results


# Artist identifiers used across services
JAKKE_SPOTIFY_ID = get_secret("JAKKE_SPOTIFY_ID", "")
ENJUNE_SPOTIFY_ID = get_secret("ENJUNE_SPOTIFY_ID", "")
ILU_SPOTIFY_ID = get_secret("ILU_SPOTIFY_ID", "")
JAKKE_YOUTUBE_CHANNEL = get_secret("JAKKE_YOUTUBE_CHANNEL", "")
JAKKE_LASTFM_ARTIST = get_secret("JAKKE_LASTFM_ARTIST", "Jakke")
ENJUNE_LASTFM_ARTIST = get_secret("ENJUNE_LASTFM_ARTIST", "Enjune")
