import pandas as pd
import re
from app.models.stream import StandardStreamRecord, Platform, StreamType

def parse_idr(value) -> int:
    if pd.isna(value) or str(value).strip() == "":
        return 0
    s = str(value).replace("Rp", "").replace(".", "").replace(",", "").strip()
    return int(s) if s.isdigit() else 0

def parse_duration(value: str) -> float:
    if pd.isna(value) or str(value).strip() == "":
        return 0.0
    s = str(value)
    h = int(m.group(1)) if (m := re.search(r"(\d+)h", s)) else 0
    mins = int(m.group(1)) if (m := re.search(r"(\d+)min", s)) else 0
    secs = int(m.group(1)) if (m := re.search(r"(\d+)s", s)) else 0
    return h * 60 + mins + secs / 60

def parse_duration_seconds(value: str) -> float:
    if pd.isna(value) or str(value).strip() == "":
        return 0.0
    s = str(value)
    mins = int(m.group(1)) if (m := re.search(r"(\d+)min", s)) else 0
    secs = int(m.group(1)) if (m := re.search(r"(\d+)s", s)) else 0
    return mins * 60 + secs

def parse_pct(value) -> float:
    if pd.isna(value):
        return 0.0
    s = str(value).replace("%", "").strip()
    try:
        f = float(s)
        return f / 100 if f > 1 else f
    except ValueError:
        return 0.0

def parse_tiktok_export(filepath: str, entity_id: str, stream_type: StreamType) -> list[StandardStreamRecord]:
    df = pd.read_excel(filepath, sheet_name="LIVE analytics", header=0)
    records = []
    for _, row in df.iterrows():
        record = StandardStreamRecord(
            entity_id=entity_id,
            platform=Platform.tiktok,
            stream_type=stream_type,
            stream_title=str(row.get("LIVE", "")),
            duration_minutes=parse_duration(str(row.get("Duration", ""))),
            gmv_affiliate=parse_idr(row.get("Affiliate GMV", 0)),
            items_sold=int(row.get("Items sold", 0) or 0),
            viewers_peak=int(row.get("Viewers", 0) or 0),
            show_gpm=parse_idr(row.get("Show GPM", 0)),
            tap_through_rate=parse_pct(row.get("Tap-through rate", 0)),
            orders_paid=int(row.get("Orders paid", 0) or 0),
            customers_unique=int(row.get("Customers", 0) or 0),
            views_total=int(row.get("Views", 0) or 0),
            comments=int(row.get("Comments", 0) or 0),
            shares=int(row.get("Shares", 0) or 0),
            likes=int(row.get("Likes", 0) or 0),
            ctor=parse_pct(row.get("CTOR", 0)),
            avg_view_duration_s=parse_duration_seconds(str(row.get("Avg viewing duration", ""))),
            new_followers=int(row.get("New followers", 0) or 0),
            product_impressions=int(row.get("Product impressions", 0) or 0),
            product_clicks=int(row.get("Product clicks", 0) or 0),
            product_ctr=parse_pct(row.get("CTR", 0)),
        )
        records.append(record)
    return records
