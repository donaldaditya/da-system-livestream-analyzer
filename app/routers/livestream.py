from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import tempfile, os, re
from datetime import datetime

from app.parsers.tiktok_parser import parse_tiktok_export
from app.parsers.shopee_parser import parse_shopee_export
from app.parsers.vision_extractor import extract_from_screenshot
from app.engine.normalizer import normalize
from app.engine.scorer import score_stream
from app.engine.analyzer import analyze_stream
from app.engine.history_store import append_history, get_rolling_avg
from app.models.stream import StandardStreamRecord, StreamAnalysis, Platform, StreamType

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or f"session_{datetime.now().strftime('%Y%m%d_%H%M')}"

def _build_entity(entity_name: str, target_gmv: str) -> dict:
    return {
        "display_name": entity_name or "Unknown",
        "tier": "unknown",
        "category": "general",
        "target_gmv_per_stream": int(target_gmv) if target_gmv and target_gmv.strip().isdigit() else 0,
        "contract_type": "external",
    }

def _f(val: str, default=0.0) -> float:
    try: return float(val.replace(",", ".").replace("%", "").strip()) if val and val.strip() else default
    except: return default

def _i(val: str, default=0) -> int:
    try: return int(float(val.replace(",", "").strip())) if val and val.strip() else default
    except: return default

@router.get("/")
async def setup(request: Request):
    return templates.TemplateResponse(request, "livestream_setup.html")

@router.get("/input")
async def input_page(request: Request):
    return templates.TemplateResponse(request, "livestream_input.html", {
        "entity_name": request.query_params.get("entity_name", ""),
        "target_gmv":  request.query_params.get("target_gmv", ""),
        "currency":    request.query_params.get("currency", "IDR"),
        "platform":    request.query_params.get("platform", "tiktok"),
        "stream_type": request.query_params.get("stream_type", "bau"),
    })

@router.post("/analyze")
async def analyze(
    request: Request,
    entity_name: str = Form(""),
    platform: str = Form(...),
    stream_type: str = Form(...),
    input_mode: str = Form(...),
    target_gmv: str = Form(""),
    file_subtype: str = Form("data"),
    # file upload
    file: UploadFile | None = File(None),
    # screenshot fields — TikTok
    ss_gmv: str = Form("0"), ss_items_sold: str = Form("0"),
    ss_views: str = Form("0"), ss_peak_viewers: str = Form("0"),
    ss_duration: str = Form("0"), ss_show_gpm: str = Form("0"),
    ss_avg_view: str = Form("0"), ss_tap_through: str = Form("0"),
    ss_ctor: str = Form("0"), ss_follow_rate: str = Form("0"),
    ss_new_followers: str = Form("0"), ss_comments: str = Form("0"),
    ss_likes: str = Form("0"), ss_shares: str = Form("0"),
    # screenshot fields — Shopee
    ss_orders: str = Form("0"), ss_viewers_total: str = Form("0"),
    ss_viewers_active: str = Form("0"), ss_add_to_cart: str = Form("0"),
    # manual fields
    gmv: str = Form("0"), views: str = Form("0"), orders: str = Form("0"),
    duration: str = Form("0"), avg_view_duration: str = Form("0"),
    ctor: str = Form("0"), new_followers: str = Form("0"),
    user_notes: str = Form(""),
):
    # derive entity id from name or timestamp
    entity_id = _slug(entity_name) if entity_name.strip() else _slug(f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    entity = _build_entity(entity_name, target_gmv)
    record = None

    if input_mode == "file" and file and file.filename:
        # use filename as entity id if no name given
        if not entity_name.strip():
            entity_id = _slug(os.path.splitext(file.filename)[0])
            entity["display_name"] = os.path.splitext(file.filename)[0]

        if file_subtype == "image":
            # image/pdf — use Claude Vision to extract metrics
            img_bytes = await file.read()
            media_type = file.content_type or "image/png"
            try:
                extracted = extract_from_screenshot(img_bytes, media_type)
            except Exception as e:
                return HTMLResponse(f"Could not extract metrics from image: {e}", status_code=400)
            if platform == "tiktok":
                record = StandardStreamRecord(
                    entity_id=entity_id, platform=Platform.tiktok,
                    stream_type=StreamType(stream_type),
                    stream_title=extracted.get("stream_title") or "",
                    gmv_affiliate=extracted.get("gmv_total"),
                    views_total=int(extracted.get("views") or 0) or None,
                    avg_view_duration_s=extracted.get("avg_view_duration_s"),
                    show_gpm=int(extracted.get("show_gpm") or 0) or None,
                    tap_through_rate=extracted.get("tap_through_rate"),
                    ctor=extracted.get("live_ctr"),
                    follow_rate=extracted.get("follow_rate"),
                )
            else:
                record = StandardStreamRecord(
                    entity_id=entity_id, platform=Platform.shopee,
                    stream_type=StreamType(stream_type),
                    gmv_confirmed=extracted.get("gmv_total"),
                    viewers_total=int(extracted.get("views") or 0) or None,
                    avg_view_duration_s=extracted.get("avg_view_duration_s"),
                )
        else:
            # data file — parse xlsx/csv
            suffix = os.path.splitext(file.filename)[1] or ".xlsx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name
            try:
                if platform == "tiktok":
                    records = parse_tiktok_export(tmp_path, entity_id, StreamType(stream_type))
                else:
                    records = parse_shopee_export(tmp_path, entity_id, StreamType(stream_type))
                record = records[0] if records else None
            except Exception as e:
                return HTMLResponse(f"File parsing failed: {e}", status_code=400)
            finally:
                os.unlink(tmp_path)

    elif input_mode == "screenshot":
        if platform == "tiktok":
            record = StandardStreamRecord(
                entity_id=entity_id, platform=Platform.tiktok,
                stream_type=StreamType(stream_type),
                duration_minutes=_f(ss_duration),
                gmv_affiliate=_i(ss_gmv),
                items_sold=_i(ss_items_sold),
                views_total=_i(ss_views),
                viewers_peak=_i(ss_peak_viewers),
                show_gpm=_i(ss_show_gpm),
                avg_view_duration_s=_f(ss_avg_view),
                tap_through_rate=_f(ss_tap_through) / 100 if _f(ss_tap_through) > 1 else _f(ss_tap_through),
                ctor=_f(ss_ctor) / 100 if _f(ss_ctor) > 1 else _f(ss_ctor),
                follow_rate=_f(ss_follow_rate) / 100 if _f(ss_follow_rate) > 1 else _f(ss_follow_rate),
                new_followers=_i(ss_new_followers),
                comments=_i(ss_comments),
                likes=_i(ss_likes),
                shares=_i(ss_shares),
            )
        else:
            record = StandardStreamRecord(
                entity_id=entity_id, platform=Platform.shopee,
                stream_type=StreamType(stream_type),
                duration_minutes=_f(ss_duration),
                gmv_confirmed=_i(ss_gmv),
                orders_confirmed=_i(ss_orders),
                items_sold=_i(ss_items_sold),
                viewers_total=_i(ss_viewers_total),
                viewers_active=_i(ss_viewers_active),
                avg_view_duration_s=_f(ss_avg_view),
                add_to_cart=_i(ss_add_to_cart),
                comments=_i(ss_comments),
            )

    elif input_mode == "manual":
        record = StandardStreamRecord(
            entity_id=entity_id, platform=Platform(platform),
            stream_type=StreamType(stream_type),
            duration_minutes=_f(duration),
            gmv_affiliate=_i(gmv),
            views_total=_i(views),
            orders_paid=_i(orders),
            avg_view_duration_s=_f(avg_view_duration),
            ctor=_f(ctor) / 100 if _f(ctor) > 1 else _f(ctor),
            new_followers=_i(new_followers),
        )

    if not record:
        return HTMLResponse("Could not parse input — please check your data and try again.", status_code=400)

    record = normalize(record)
    scores = score_stream(record)
    history_avg = get_rolling_avg(entity_id)
    try:
        analysis = analyze_stream(record, scores, entity, history_avg, user_notes)
    except Exception as e:
        return HTMLResponse(f"Analysis failed: {e}", status_code=500)
    append_history(entity_id, StreamAnalysis(stream=record, scores=scores, analysis=analysis, user_notes=user_notes))

    return templates.TemplateResponse(request, "livestream_analysis.html",
        {"record": record, "scores": scores, "analysis": analysis, "entity": entity})
