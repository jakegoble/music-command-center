"""Centralized data loaders — imported by all pages."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_songs_all() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "jakke_songs_all.csv")
    df["release_date"] = pd.to_datetime(df["release_date"], format="mixed", errors="coerce")
    return df


@st.cache_data
def load_songs_recent() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "jakke_top_songs_recent.csv")


@st.cache_data
def load_ig_insights() -> dict:
    with open(DATA_DIR / "instagram_jakke_insights_30d.json") as f:
        return json.load(f)


@st.cache_data
def load_catalog() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "musicteam_catalog.csv")


@st.cache_data
def load_ig_yearly() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ig_yearly_stats.csv")


@st.cache_data
def load_ig_monthly() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "ig_monthly_stats.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df


@st.cache_data
def load_ig_top_posts() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "ig_top_posts.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_ig_collaborators() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ig_collaborators.csv")


@st.cache_data
def load_ig_content_type() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ig_content_type_performance.csv")


@st.cache_data
def load_ig_day_of_week() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ig_day_of_week.csv")


@st.cache_data
def load_songstats_jakke() -> dict:
    with open(DATA_DIR / "songstats_jakke.json") as f:
        return json.load(f)


@st.cache_data
def load_songstats_enjune() -> dict:
    with open(DATA_DIR / "songstats_enjune.json") as f:
        return json.load(f)


@st.cache_data
def load_music_collaborators() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "music_collaborators.csv")
