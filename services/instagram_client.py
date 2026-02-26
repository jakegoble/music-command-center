"""Instagram Graph API client.

Provides follower stats, post insights, demographics, and engagement data.
Requires a Business/Creator account + long-lived access token from Meta.
Docs: https://developers.facebook.com/docs/instagram-api
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
GRAPH_URL = "https://graph.facebook.com/v19.0"


def _load_static(filename: str) -> Any:
    """Load static fallback file from data/ directory."""
    path = DATA_DIR / filename
    if path.exists():
        if filename.endswith(".json"):
            with open(path) as f:
                return json.load(f)
        elif filename.endswith(".csv"):
            import pandas as pd
            return pd.read_csv(path)
    return {} if filename.endswith(".json") else None


def _api_get(endpoint: str, params: dict | None = None) -> dict[str, Any]:
    """Make authenticated GET to Instagram Graph API."""
    token = get_secret("INSTAGRAM_ACCESS_TOKEN")
    base_params = {"access_token": token}
    if params:
        base_params.update(params)
    resp = requests.get(f"{GRAPH_URL}/{endpoint}", params=base_params, timeout=15)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=3600)
def get_account_info() -> dict[str, Any]:
    """Get account info (followers, follows, media count)."""
    token = get_secret("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = get_secret("INSTAGRAM_USER_ID")
    if not token or not ig_user_id:
        static = _load_static("instagram_jakke_insights_30d.json")
        return static.get("account", {})

    try:
        data = _api_get(ig_user_id, {"fields": "username,followers_count,follows_count,media_count"})
        return {
            "username": data.get("username", ""),
            "followers": data.get("followers_count", 0),
            "following": data.get("follows_count", 0),
            "posts_count": data.get("media_count", 0),
        }
    except Exception as e:
        logger.warning("Instagram account info failed: %s", e)
        static = _load_static("instagram_jakke_insights_30d.json")
        return static.get("account", {})


@st.cache_data(ttl=3600)
def get_insights_30d() -> dict[str, Any]:
    """Get 30-day insights overview (views, reach, interactions, etc.)."""
    token = get_secret("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = get_secret("INSTAGRAM_USER_ID")
    if not token or not ig_user_id:
        return _load_static("instagram_jakke_insights_30d.json")

    try:
        # Fetch account-level insights
        metrics = "impressions,reach,accounts_engaged,profile_views"
        data = _api_get(f"{ig_user_id}/insights", {
            "metric": metrics,
            "period": "days_28",
        })

        # Parse into our expected format
        values = {}
        for item in data.get("data", []):
            name = item.get("name", "")
            vals = item.get("values", [{}])
            values[name] = vals[0].get("value", 0) if vals else 0

        account = get_account_info()

        return {
            "account": account,
            "overview": {
                "views_30d": values.get("impressions", 0),
                "accounts_reached": values.get("reach", 0),
                "interactions": values.get("accounts_engaged", 0),
                "accounts_engaged": values.get("accounts_engaged", 0),
                "profile_visits": values.get("profile_views", 0),
                "external_link_taps": 0,
            },
            "_source": "api",
        }
    except Exception as e:
        logger.warning("Instagram insights failed, using static: %s", e)
        return _load_static("instagram_jakke_insights_30d.json")


@st.cache_data(ttl=3600)
def get_recent_media(limit: int = 25) -> list[dict]:
    """Get recent media posts with basic metrics."""
    token = get_secret("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = get_secret("INSTAGRAM_USER_ID")
    if not token or not ig_user_id:
        return []

    try:
        data = _api_get(f"{ig_user_id}/media", {
            "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink",
            "limit": limit,
        })
        return data.get("data", [])
    except Exception as e:
        logger.warning("Instagram recent media failed: %s", e)
        return []


@st.cache_data(ttl=3600)
def get_demographics() -> dict[str, Any]:
    """Get follower demographics (age, gender, city, country)."""
    token = get_secret("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = get_secret("INSTAGRAM_USER_ID")
    if not token or not ig_user_id:
        static = _load_static("instagram_jakke_insights_30d.json")
        return static.get("follower_demographics", {})

    try:
        data = _api_get(f"{ig_user_id}/insights", {
            "metric": "follower_demographics",
            "period": "lifetime",
            "metric_type": "total_value",
            "breakdown": "city",
        })
        return data.get("data", [{}])[0].get("total_value", {})
    except Exception as e:
        logger.warning("Instagram demographics failed: %s", e)
        static = _load_static("instagram_jakke_insights_30d.json")
        return static.get("follower_demographics", {})


def is_available() -> bool:
    """Check if Instagram API is configured."""
    return bool(get_secret("INSTAGRAM_ACCESS_TOKEN") and get_secret("INSTAGRAM_USER_ID"))
