from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Platform(str, Enum):
    tiktok = "tiktok"
    shopee = "shopee"
    tokopedia = "tokopedia"

class StreamType(str, Enum):
    bau = "bau"
    campaign_payday = "campaign_payday"
    campaign_double = "campaign_double"
    campaign_brand = "campaign_brand"
    collab = "collab"
    other = "other"

class PerformanceTier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class MarketBand(str, Enum):
    elite = "elite"
    good = "good"
    avg = "avg"
    poor = "poor"

class StandardStreamRecord(BaseModel):
    entity_id: str
    platform: Platform
    stream_type: StreamType
    stream_title: str = ""
    start_time: Optional[datetime] = None
    duration_minutes: float = 0
    gmv_affiliate: Optional[int] = None
    items_sold: Optional[int] = None
    viewers_peak: Optional[int] = None
    show_gpm: Optional[int] = None
    tap_through_rate: Optional[float] = None
    orders_paid: Optional[int] = None
    customers_unique: Optional[int] = None
    views_total: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    likes: Optional[int] = None
    ctor: Optional[float] = None
    avg_view_duration_s: Optional[float] = None
    new_followers: Optional[int] = None
    product_impressions: Optional[int] = None
    product_clicks: Optional[int] = None
    product_ctr: Optional[float] = None
    gmv_confirmed: Optional[int] = None
    viewers_total: Optional[int] = None
    viewers_active: Optional[int] = None
    orders_confirmed: Optional[int] = None
    add_to_cart: Optional[int] = None
    gmv_total: int = 0
    gmv_per_hour: float = 0
    conversion_rate: Optional[float] = None
    engagement_rate: Optional[float] = None
    follow_rate: Optional[float] = None
    atc_rate: Optional[float] = None

class DimensionScore(BaseModel):
    label: str
    score: int
    vs_self_pct: Optional[float] = None
    market_band: MarketBand = MarketBand.avg

class PerformanceScore(BaseModel):
    overall: int
    tier: PerformanceTier
    revenue: DimensionScore
    traffic: DimensionScore
    engagement: DimensionScore
    conversion: DimensionScore
    audience_growth: DimensionScore
    product_mix: DimensionScore
    consistency: DimensionScore

class NextAction(BaseModel):
    priority: int
    action: str
    expected_impact: str

class CoachingFlag(BaseModel):
    metric: str
    flag: str
    fix: str
    check_outside: Optional[str] = None

class AnalysisResult(BaseModel):
    performance_tier: PerformanceTier
    overall_score: int
    headline: str
    vs_self: str
    vs_market: str
    what_worked: list[str]
    what_didnt: list[str]
    root_causes: list[str]
    next_stream_actions: list[NextAction]
    metric_commentary: dict[str, str]
    coaching_flags: list[CoachingFlag]
    analysis_quality_suggestions: list[str]
    whatsapp_summary: str

class StreamAnalysis(BaseModel):
    stream: StandardStreamRecord
    scores: PerformanceScore
    analysis: AnalysisResult
    analyzed_at: datetime = Field(default_factory=datetime.now)
    user_notes: Optional[str] = None
