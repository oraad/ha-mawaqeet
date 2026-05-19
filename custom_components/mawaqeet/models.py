"""Shared data models for Mawaqeet."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, TypedDict

from .enum import PrayerTime, PrayerTimeOption

type NightTimes = tuple[timedelta, datetime, datetime]
type PrayerTimeEntries = dict[PrayerTime, datetime]
type PrayerTimeConfig = dict[PrayerTimeOption, Any]
type Coordinates = tuple[float, float]


class MawaqeetData(TypedDict):
    """Mawaqeet coordinator data."""

    prayer_times: PrayerTimeEntries
    prayer_times_config: PrayerTimeConfig
