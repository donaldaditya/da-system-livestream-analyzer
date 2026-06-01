from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from app.routers import livestream

load_dotenv()

app = FastAPI(title="DA System — Livestream Analyzer", version="0.1")
app.include_router(livestream.router, prefix="/livestream-analyzer")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")
