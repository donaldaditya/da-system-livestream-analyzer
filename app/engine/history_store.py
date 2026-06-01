import json
from pathlib import Path
from app.models.stream import StreamAnalysis

HISTORY_DIR = Path("data/history")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def _path(entity_id: str) -> Path:
    return HISTORY_DIR / f"{entity_id}.json"

def get_history(entity_id: str) -> list[dict]:
    p = _path(entity_id)
    return json.loads(p.read_text()) if p.exists() else []

def append_history(entity_id: str, analysis: StreamAnalysis) -> None:
    history = get_history(entity_id)
    history.append(analysis.model_dump(mode="json"))
    _path(entity_id).write_text(json.dumps(history, indent=2, default=str))

def get_rolling_avg(entity_id: str, n: int = 6) -> dict[str, float]:
    history = get_history(entity_id)[-n:]
    if not history:
        return {}
    avgs = {}
    metrics = ["gmv_total","gmv_per_hour","conversion_rate","avg_view_duration_s",
               "follow_rate","ctor","tap_through_rate","product_ctr","atc_rate"]
    for m in metrics:
        vals = [h["stream"].get(m) for h in history if h["stream"].get(m) is not None]
        if vals:
            avgs[m] = sum(vals) / len(vals)
    return avgs
