import json
from pathlib import Path
from app.models.stream import StandardStreamRecord, PerformanceScore, DimensionScore, PerformanceTier, MarketBand
from app.engine.history_store import get_rolling_avg

BENCHMARKS = json.loads(Path("config/benchmarks.json").read_text())
WEIGHTS = {"revenue":0.30,"traffic":0.20,"engagement":0.15,"conversion":0.20,
           "audience_growth":0.05,"product_mix":0.05,"consistency":0.05}

def _band(v, t) -> MarketBand:
    if v >= t["elite"]: return MarketBand.elite
    if v >= t["good"]: return MarketBand.good
    if v >= t["avg"]: return MarketBand.avg
    return MarketBand.poor

def _band_score(b: MarketBand) -> int:
    return {"elite":95,"good":75,"avg":55,"poor":30}[b]

def _self_score(v, avg) -> int:
    if not avg: return 55
    r = v / avg
    if r >= 1.3: return 90
    if r >= 1.1: return 75
    if r >= 0.9: return 55
    if r >= 0.7: return 35
    return 20

def score_stream(record: StandardStreamRecord) -> PerformanceScore:
    pk = "tiktok" if record.platform in ("tiktok","tokopedia") else "shopee"
    bm = BENCHMARKS[pk]["market_defaults"]
    hist = get_rolling_avg(record.entity_id)

    def dim(label, value, key) -> DimensionScore:
        if not value:
            return DimensionScore(label=label, score=0, market_band=MarketBand.poor)
        t = bm.get(key, {})
        band = _band(value, t) if t else MarketBand.avg
        ms = _band_score(band)
        avg = hist.get(key)
        ss = _self_score(value, avg) if avg else ms
        vs = round((value/avg-1)*100,1) if avg else None
        score = int(ms*0.40+ss*0.60) if hist else ms
        return DimensionScore(label=label, score=score, vs_self_pct=vs, market_band=band)

    if pk == "tiktok":
        rev = dim("Revenue", record.gmv_per_hour, "show_gpm_idr")
        trf = DimensionScore(label="Traffic", score=min(100,int((record.views_total or 0)/500)), market_band=MarketBand.avg)
        eng = dim("Engagement", record.avg_view_duration_s, "avg_view_duration_s")
        cnv = dim("Conversion", record.ctor, "ctor")
        aud = dim("Audience growth", record.follow_rate, "follow_rate")
        prd = dim("Product mix", record.product_ctr, "product_ctr")
    else:
        rev = dim("Revenue", record.gmv_per_hour, "gmv_per_hour_idr")
        trf = DimensionScore(label="Traffic", score=min(100,int((record.viewers_total or 0)/200)), market_band=MarketBand.avg)
        eng = dim("Engagement", record.avg_view_duration_s, "avg_view_duration_s")
        cnv = dim("Conversion", record.conversion_rate, "conversion_rate")
        aud = DimensionScore(label="Audience growth", score=50, market_band=MarketBand.avg)
        prd = dim("Product mix", record.atc_rate, "atc_rate")

    avg_gmv = hist.get("gmv_total", 0)
    con_score = _self_score(record.gmv_total, avg_gmv) if avg_gmv else 50
    con = DimensionScore(label="Consistency", score=con_score, market_band=MarketBand.avg)

    dims = [rev,trf,eng,cnv,aud,prd,con]
    weights = list(WEIGHTS.values())
    overall = int(sum(d.score * w for d, w in zip(dims, weights)))
    tier = (PerformanceTier.S if overall>=85 else PerformanceTier.A if overall>=70
            else PerformanceTier.B if overall>=55 else PerformanceTier.C if overall>=40
            else PerformanceTier.D)

    return PerformanceScore(overall=overall, tier=tier, revenue=rev, traffic=trf,
        engagement=eng, conversion=cnv, audience_growth=aud, product_mix=prd, consistency=con)
