"""Revenue estimation from streaming data.

Uses per-stream rates to estimate revenue across platforms.
Rates are industry averages for independent artists (2025-2026).
"""
from __future__ import annotations

from dataclasses import dataclass

# Per-stream rates (USD) — industry averages for indie artists
RATES = {
    "Spotify": 0.004,
    "Apple Music": 0.01,
    "YouTube Music": 0.008,
    "YouTube (video)": 0.003,
    "Amazon Music": 0.004,
    "Deezer": 0.004,
    "Tidal": 0.013,
    "Pandora": 0.007,
    "SoundCloud": 0.003,
    "Other": 0.004,
}

# Platform share assumptions for cross-platform streams
# Based on typical indie artist distribution
PLATFORM_SPLIT = {
    "Spotify": 0.60,
    "Apple Music": 0.15,
    "YouTube Music": 0.08,
    "Amazon Music": 0.05,
    "Deezer": 0.04,
    "Tidal": 0.02,
    "Other": 0.06,
}


@dataclass
class RevenueEstimate:
    """Revenue estimate for a track or catalog."""
    total_streams: int
    estimated_revenue: float
    platform_breakdown: dict[str, dict]  # platform -> {streams, revenue, rate}
    blended_rate: float  # effective per-stream rate


def estimate_revenue(total_streams: int, platform_split: dict[str, float] | None = None) -> RevenueEstimate:
    """Estimate revenue from total cross-platform stream count.

    Args:
        total_streams: Total streams across all platforms.
        platform_split: Optional custom platform distribution. Defaults to PLATFORM_SPLIT.

    Returns:
        RevenueEstimate with total and per-platform breakdown.
    """
    split = platform_split or PLATFORM_SPLIT
    breakdown: dict[str, dict] = {}
    total_revenue = 0.0

    for platform, share in split.items():
        streams = int(total_streams * share)
        rate = RATES.get(platform, RATES["Other"])
        revenue = streams * rate
        total_revenue += revenue
        breakdown[platform] = {
            "streams": streams,
            "revenue": revenue,
            "rate": rate,
            "share": share,
        }

    blended_rate = total_revenue / total_streams if total_streams > 0 else 0.0

    return RevenueEstimate(
        total_streams=total_streams,
        estimated_revenue=total_revenue,
        platform_breakdown=breakdown,
        blended_rate=blended_rate,
    )


def estimate_track_revenue(spotify_streams: int) -> float:
    """Quick estimate: given Spotify streams, estimate total revenue across all platforms.

    Assumes Spotify represents ~60% of total streams.
    """
    estimated_total = int(spotify_streams / 0.60)
    result = estimate_revenue(estimated_total)
    return result.estimated_revenue


def monthly_revenue_target(annual_target: float) -> dict[str, int]:
    """Calculate monthly stream targets to hit an annual revenue goal.

    Returns required streams per month for each platform.
    """
    monthly = annual_target / 12
    targets = {}
    for platform, rate in RATES.items():
        if platform != "Other":
            targets[platform] = int(monthly / rate)
    return targets
