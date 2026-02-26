"""Spotify Web API client via spotipy.

Provides artist info, albums, tracks, and playlist details.
Note: As of Feb 2026, artist popularity/followers/top-tracks removed from dev mode.
Docs: https://developer.spotify.com/documentation/web-api
"""
from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from services.config import get_secret

logger = logging.getLogger(__name__)


def _get_client():
    """Get authenticated spotipy client (client credentials flow)."""
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
    except ImportError:
        logger.warning("spotipy not installed — pip install spotipy")
        return None

    client_id = get_secret("SPOTIFY_CLIENT_ID")
    client_secret = get_secret("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None

    try:
        auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(auth_manager=auth)
    except Exception as e:
        logger.warning("Spotify auth failed: %s", e)
        return None


@st.cache_data(ttl=3600)
def get_artist(artist_id: str) -> dict[str, Any] | None:
    """Get artist profile (name, genres, images, external URLs)."""
    sp = _get_client()
    if not sp or not artist_id:
        return None
    try:
        return sp.artist(artist_id)
    except Exception as e:
        logger.warning("Spotify get_artist failed: %s", e)
        return None


@st.cache_data(ttl=3600)
def get_artist_albums(artist_id: str, limit: int = 50) -> list[dict]:
    """Get artist's albums/singles/EPs."""
    sp = _get_client()
    if not sp or not artist_id:
        return []
    try:
        results = sp.artist_albums(artist_id, album_type="album,single", limit=limit)
        return results.get("items", [])
    except Exception as e:
        logger.warning("Spotify get_artist_albums failed: %s", e)
        return []


@st.cache_data(ttl=3600)
def get_album_tracks(album_id: str) -> list[dict]:
    """Get tracks from an album/single."""
    sp = _get_client()
    if not sp or not album_id:
        return []
    try:
        results = sp.album_tracks(album_id)
        return results.get("items", [])
    except Exception as e:
        logger.warning("Spotify get_album_tracks failed: %s", e)
        return []


@st.cache_data(ttl=3600)
def get_track(track_id: str) -> dict[str, Any] | None:
    """Get track details."""
    sp = _get_client()
    if not sp or not track_id:
        return None
    try:
        return sp.track(track_id)
    except Exception as e:
        logger.warning("Spotify get_track failed: %s", e)
        return None


@st.cache_data(ttl=3600)
def search_tracks(query: str, limit: int = 10) -> list[dict]:
    """Search for tracks by name."""
    sp = _get_client()
    if not sp:
        return []
    try:
        results = sp.search(q=query, type="track", limit=limit)
        return results.get("tracks", {}).get("items", [])
    except Exception as e:
        logger.warning("Spotify search failed: %s", e)
        return []


@st.cache_data(ttl=3600)
def get_playlist(playlist_id: str) -> dict[str, Any] | None:
    """Get playlist details including tracks."""
    sp = _get_client()
    if not sp or not playlist_id:
        return None
    try:
        return sp.playlist(playlist_id)
    except Exception as e:
        logger.warning("Spotify get_playlist failed: %s", e)
        return None


def is_available() -> bool:
    """Check if Spotify API is configured and working."""
    return _get_client() is not None
