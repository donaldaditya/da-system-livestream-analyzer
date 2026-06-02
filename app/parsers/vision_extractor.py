import anthropic, base64, json, os

PROMPT = """Extract all visible livestream metrics from this TikTok or Shopee dashboard screenshot.
Return ONLY valid JSON, no markdown, no explanation outside JSON.

JSON shape (use null for any field not visible):
{
  "platform": "tiktok|shopee",
  "stream_title": null,
  "gmv_total": null,
  "items_sold": null,
  "views": null,
  "impressions": null,
  "gmv_per_hour": null,
  "show_gpm": null,
  "avg_view_duration_s": null,
  "follow_rate": null,
  "tap_through_rate": null,
  "live_ctr": null,
  "order_rate": null,
  "new_followers": null,
  "comments": null,
  "likes": null,
  "shares": null,
  "peak_viewers": null,
  "duration_min": null
}

Extraction rules:
- IDR currency: strip "Rp" and dots → integer (Rp3.166.320 → 3166320)
- Percentages: convert to decimal (2.64% → 0.0264, 88.39% → 0.8839)
- Duration: convert to seconds (1m 8s → 68, 12s → 12)
- K/M suffix: expand (66.53K → 66530, 1.95M → 1950000)
- TikTok "Attributed GMV" = gmv_total
- TikTok "Show GPM" = show_gpm (already in Rp per 1000 impressions)
- TikTok "Tap-through rate (via LIVE pr..." = tap_through_rate
- TikTok "LIVE CTR" or "CTOR" = live_ctr
- TikTok "Follow rate" = follow_rate
- TikTok "Current viewers" or peak = peak_viewers"""

def extract_from_screenshot(image_bytes: bytes, media_type: str = "image/png") -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": PROMPT}
        ]}]
    )
    raw = response.content[0].text.strip()
    # strip markdown code fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
