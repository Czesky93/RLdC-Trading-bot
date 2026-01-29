"""Lightweight portal apps for RLdC advanced modules."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def create_portal_app(title: str, description: str, links: list[tuple[str, str]]) -> FastAPI:
    """Create a simple HTML portal app."""

    app = FastAPI(title=title, version="0.7.0-beta")

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        links_html = "".join(
            f"<li><a href='{href}'>{label}</a></li>" for label, href in links
        )
        html = f"""
        <html>
          <head><title>{title}</title></head>
          <body>
            <h1>{title}</h1>
            <p>{description}</p>
            <ul>{links_html}</ul>
            <p><em>Uwaga: to panel informacyjny, nie porada inwestycyjna.</em></p>
          </body>
        </html>
        """
        return HTMLResponse(content=html)

    @app.get("/status")
    def status() -> dict:
        return {"status": "ok", "note": "portal informational"}

    @app.get("/reports")
    def reports() -> dict:
        return {"reports": [], "note": "portal informational"}

    return app
