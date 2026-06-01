from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import tempfile, os

from app.parsers.tiktok_parser import parse_tiktok_export
from app.parsers.shopee_parser import parse_shopee_export
from app.parsers.vision_extractor import extract_from_screenshot
from app.engine.normalizer import normalize
from app.engine.entity_resolver import resolve_entity, get_all_entities
from app.engine.scorer import score_stream
from app.engine.analyzer import analyze_stream
from app.engine.history_store import append_history, get_rolling_avg
from app.models.stream import StandardStreamRecord, StreamAnalysis, Platform, StreamType

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def setup(request: Request):
    return templates.TemplateResponse("livestream_setup.html",
        {"request": request, "entities": get_all_entities()})

@router.get("/input")
async def input_page(request: Request):
    return templates.TemplateResponse("livestream_input.html", {"request": request})

@router.post("/analyze")
async def analyze(
    request: Request,
    entity_id: str = Form(...), platform: str = Form(...),
    stream_type: str = Form(...), input_mode: str = Form(...),
    file: UploadFile | None = File(None), image: UploadFile | None = File(None),
    user_notes: str = Form(""), gmv: str = Form("0"), views: str = Form("0"),
    orders: str = Form("0"), duration: str = Form("0"),
    avg_view_duration: str = Form("0"), ctor: str = Form("0"),
    new_followers: str = Form("0"),
):
    entity = resolve_entity(entity_id)
    if not entity:
        return HTMLResponse("Entity not found", status_code=404)

    record = None

    if input_mode == "file" and file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        try:
            if platform in ("tiktok","tokopedia"):
                records = parse_tiktok_export(tmp_path, entity_id, StreamType(stream_type))
            else:
                records = parse_shopee_export(tmp_path, entity_id, StreamType(stream_type))
            record = records[0] if records else None
        finally:
            os.unlink(tmp_path)

    elif input_mode == "image" and image:
        img_bytes = await image.read()
        extracted = extract_from_screenshot(img_bytes, image.content_type)
        record = StandardStreamRecord(
            entity_id=entity_id, platform=Platform(platform),
            stream_type=StreamType(stream_type),
            stream_title=extracted.get("stream_title") or "",
            duration_minutes=0,
            gmv_affiliate=extracted.get("gmv_total"),
            views_total=extracted.get("views"),
            avg_view_duration_s=extracted.get("avg_view_duration_s"),
        )

    elif input_mode == "manual":
        record = StandardStreamRecord(
            entity_id=entity_id, platform=Platform(platform),
            stream_type=StreamType(stream_type),
            duration_minutes=float(duration) if duration else 0,
            gmv_affiliate=int(gmv.replace(".","")) if gmv and gmv != "0" else 0,
            views_total=int(views) if views and views != "0" else 0,
            orders_paid=int(orders) if orders and orders != "0" else 0,
            avg_view_duration_s=float(avg_view_duration) if avg_view_duration and avg_view_duration != "0" else 0,
            ctor=float(ctor) if ctor and ctor != "0" else 0,
            new_followers=int(new_followers) if new_followers and new_followers != "0" else 0,
        )

    if not record:
        return HTMLResponse("Could not parse input", status_code=400)

    record = normalize(record)
    scores = score_stream(record)
    history_avg = get_rolling_avg(entity_id)
    analysis = analyze_stream(record, scores, entity, history_avg, user_notes)
    append_history(entity_id, StreamAnalysis(stream=record, scores=scores, analysis=analysis, user_notes=user_notes))

    return templates.TemplateResponse("livestream_analysis.html",
        {"request": request, "record": record, "scores": scores, "analysis": analysis, "entity": entity})
