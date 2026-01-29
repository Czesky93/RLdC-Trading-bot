"""FastAPI application for RLdC Trading AiNalyzer Bot."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from rldc.config import AppConfig
from rldc.db.storage import Storage
from rldc.reports.generator import generate_report


def create_app(config: AppConfig) -> FastAPI:
    """Create FastAPI app."""

    app = FastAPI(title="RLdC Trading AiNalyzer Bot", version="0.7.0-beta")
    templates = Jinja2Templates(directory="src/rldc/web/templates")
    storage = Storage(config.db_path)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "version": "0.7.0-beta"}

    @app.get("/pairs")
    def pairs() -> dict:
        return {"pairs": config.default_pairs}

    @app.get("/analyze")
    def analyze(pair: str, timeframe: str = "1h") -> JSONResponse:
        if pair not in config.default_pairs:
            raise HTTPException(status_code=404, detail="Pair not configured")
        report = generate_report(storage, config, pair, timeframe)
        return JSONResponse(content=report)

    @app.get("/reports")
    def reports() -> dict:
        files = []
        if config.report_dir.exists():
            files = [path.name for path in config.report_dir.glob("*.json")]
        return {"reports": files}

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        pairs_data = []
        for pair in config.default_pairs:
            signal = storage.latest_signal(pair, "1h")
            pairs_data.append({"pair": pair, "signal": signal})
        return templates.TemplateResponse(
            "index.html", {"request": request, "pairs": pairs_data}
        )

    return app
