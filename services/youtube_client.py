"""YouTube Data API v3 client.

Provides channel stats, video metrics, and search.
Free: 10,000 quota units/day (channel/video detail = 1 unit, search = 100 units).
Docs: https://developers.google.com/youtube/v3
"""
from __future__ import annotations

import logging
from typing import Any

import requests
import streamlit as st

from services.config import get_secret

logger = logging.getLogger(__name__)

BASE_URL = "https://www.googleapis.com/youtube/v3"


def _api_get(endpoint: str, params: dict) -> dict[str, Any]:
    """Make GET request to YouTube Data API."""
    params["key"] = get_secret("YOUTUBE_API_KEY")
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=3600)
def get_channel_stats(channel_id: str = "") -> dict[str, Any] | None:
    """Get channel subscriber count, view count, video count."""
    api_key = get_secret("YOUTUBE_API_KEY")
    channel_id = channel_id or get_secret("JAKKE_YOUTUBE_CHANNEL")
    if not api_key or not channel_id:
        return None

    try:
        data = _api_get("channels", {"part": "statistics,snippet", "id": channel_id})
        items = data.get("items", [])
        if not items:
            return None
        item = items[0]
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        return {
            "title": snippet.get("title", ""),
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "description": snippet.get("description", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
        }
    except Exception as e:
        logger.warning("YouTube channel stats failed: %s", e)
        return None


@st.cache_data(ttl=3600)
def get_recent_videos(channel_id: str = "", limit: int = 10) -> list[dict]:
    """Get recent videos from a channel with view/like counts."""
    api_key = get_secret("YOUTUBE_API_KEY")
    channel_id = channel_id or get_secret("JAKKE_YOUTUBE_CHANNEL")
    if not api_key or not channel_id:
        return []

    try:
        # Search for recent uploads (costs 100 quota units)
        search = _api_get("search", {
            "part": "id",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": limit,
        })
        video_ids = [item["id"]["videoId"] for item in search.get("items", []) if "videoId" in item.get("id", {})]

        if not video_ids:
            return []

        # Get full video details (costs 1 unit per call)
        videos = _api_get("videos", {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
        })

        results = []
        for v in videos.get("items", []):
            stats = v.get("statistics", {})
            snippet = v.get("snippet", {})
            results.append({
                "id": v["id"],
                "title": snippet.get("title", ""),
                "published": snippet.get("publishedAt", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "url": f"https://youtube.com/watch?v={v['id']}",
            })
        return results
    except Exception as e:
        logger.warning("YouTube recent videos failed: %s", e)
        return []


@st.cache_data(ttl=7200)
def search_videos(query: str, limit: int = 5) -> list[dict]:
    """Search YouTube for videos matching query."""
    api_key = get_secret("YOUTUBE_API_KEY")
    if not api_key:
        return []

    try:
        data = _api_get("search", {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": limit,
        })
        return [
            {
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published": item["snippet"]["publishedAt"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "url": f"https://youtube.com/watch?v={item['id']['videoId']}",
            }
            for item in data.get("items", [])
            if "videoId" in item.get("id", {})
        ]
    except Exception as e:
        logger.warning("YouTube search failed: %s", e)
        return []


def is_available() -> bool:
    """Check if YouTube API is configured."""
    return bool(get_secret("YOUTUBE_API_KEY"))
