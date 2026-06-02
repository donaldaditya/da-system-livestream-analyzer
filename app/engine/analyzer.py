import anthropic, json, os
from app.models.stream import StandardStreamRecord, PerformanceScore, AnalysisResult

def _client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM = """You are a livestream commerce analyst for Emtek Commerce / Sinemart Digital,
an MCN on TikTok Shop, Shopee, Tokopedia in Indonesia.
Direct. No filler. Respond ONLY in the JSON schema. No markdown."""

def analyze_stream(record: StandardStreamRecord, scores: PerformanceScore,
                   entity: dict, history_avg: dict, user_notes: str = "") -> AnalysisResult:
    def fmt(v): return f"Rp {int(v):,}".replace(",",".")
    dims = [(n,d) for n,d in [("Revenue",scores.revenue),("Traffic",scores.traffic),
        ("Engagement",scores.engagement),("Conversion",scores.conversion),
        ("Audience growth",scores.audience_growth),("Product mix",scores.product_mix),
        ("Consistency",scores.consistency)]]
    dim_lines = "\n".join(f"{n} | {d.score}/100 | vs avg: {d.vs_self_pct or 'N/A'}% | {d.market_band}" for n,d in dims)
    target = entity.get("target_gmv_per_stream", 0)
    vs_t = round((record.gmv_total/target-1)*100,1) if target else "N/A"

    prompt = f"""Analyze this livestream:
ENTITY: {entity.get('display_name')} | {entity.get('tier')} | {entity.get('category')}
PLATFORM: {record.platform} | TYPE: {record.stream_type}
STREAM: "{record.stream_title}" | {record.duration_minutes:.0f} min

SCORES:
{dim_lines}

METRICS:
GMV: {fmt(record.gmv_total)} | GMV/hr: {fmt(record.gmv_per_hour)}
Views: {record.views_total or record.viewers_total or 'N/A'}
Avg view: {record.avg_view_duration_s or 'N/A'}s
Conversion: {round((record.conversion_rate or 0)*100,2)}%
Follow rate: {round((record.follow_rate or 0)*100,2)}%

HISTORY: 6-stream avg GMV: {fmt(history_avg.get('gmv_total',0)) if history_avg else 'No history'}
TARGET: {fmt(target)} | vs target: {vs_t}%
NOTES: {user_notes or 'None'}

Respond ONLY in this exact JSON:
{{"performance_tier":"S|A|B|C|D","overall_score":0,"headline":"max 15 words",
"vs_self":"one sentence","vs_market":"one sentence",
"what_worked":["item1","item2","item3"],"what_didnt":["item1","item2"],
"root_causes":["cause1","cause2"],
"next_stream_actions":[{{"priority":1,"action":"action","expected_impact":"impact"}},
{{"priority":2,"action":"action","expected_impact":"impact"}},
{{"priority":3,"action":"action","expected_impact":"impact"}}],
"metric_commentary":{{"revenue":"","traffic":"","engagement":"","conversion":"","audience_growth":"","product_mix":""}},
"coaching_flags":[{{"metric":"","flag":"","fix":""}}],
"analysis_quality_suggestions":["suggestion"],
"whatsapp_summary":"Bahasa Indonesia, max 5 bullets"}}"""

    response = _client().messages.create(
        model="claude-sonnet-4-6", max_tokens=2000,
        system=SYSTEM, messages=[{"role":"user","content":prompt}]
    )
    raw = response.content[0].text.strip().replace("```json","").replace("```","").strip()
    return AnalysisResult(**json.loads(raw))
