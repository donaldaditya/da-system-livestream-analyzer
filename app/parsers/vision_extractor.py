import anthropic, base64, json, os

PROMPT = """Extract all visible livestream metrics from this dashboard screenshot.
Return ONLY valid JSON, no markdown, no explanation.
JSON shape (null for any field not visible):
{"platform":"tiktok|shopee|tokopedia","stream_title":null,"gmv_total":null,"items_sold":null,
"impressions":null,"views":null,"gmv_per_hour":null,"show_gpm":null,"avg_view_duration_s":null,
"comment_rate":null,"follow_rate":null,"tap_through_rate":null,"live_ctr":null,"order_rate":null,
"top_products":null,"traffic_sources":null,"audience_gender":null}
Rules: IDR as integers (Rp6.168.156→6168156), percentages as decimals (5.97%→0.0597),
durations in seconds (1m8s→68), K suffix (66.53K→66530)"""

def extract_from_screenshot(image_bytes: bytes, media_type: str = "image/png") -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": PROMPT}
        ]}]
    )
    raw = response.content[0].text.strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)
