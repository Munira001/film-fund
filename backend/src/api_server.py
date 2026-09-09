import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from src.filmfund_adk_agent import search_film_funding

app = FastAPI(title="Film Fund API")

# Newsletter signups from the landing page footer are appended here.
NEWSLETTER_FILE = (
    Path(__file__).resolve().parents[1] / "data" / "newsletter_subscribers.json"
)
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class NewsletterSignup(BaseModel):
    email: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://film-funds.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Film Fund API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/newsletter")
def newsletter_signup(payload: NewsletterSignup):
    email = payload.email.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")

    NEWSLETTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    subscribers: list[dict] = []
    if NEWSLETTER_FILE.exists():
        try:
            subscribers = json.loads(NEWSLETTER_FILE.read_text() or "[]")
        except json.JSONDecodeError:
            subscribers = []

    if not any(entry.get("email") == email for entry in subscribers):
        subscribers.append(
            {
                "email": email,
                "subscribed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        NEWSLETTER_FILE.write_text(json.dumps(subscribers, indent=2) + "\n")

    return {"status": "ok", "email": email}


@app.get("/api/grants/search")
def search_grants(
    q: str = Query(..., min_length=1),
    genre: str | None = None,
    location: str | None = None,
    budget: float | None = None,
):
    query_parts = [q]

    if genre:
        query_parts.append(f"genre: {genre}")

    if location:
        query_parts.append(f"location: {location}")

    if budget is not None:
        query_parts.append(f"budget: {budget}")

    query = " ".join(query_parts)

    result = search_film_funding(query)

    if result["status"] != "success":
        return {
            "grants": [],
            "error": result.get("message", "Grant search failed"),
        }

    grants = []

    for item in result["evidence_packet"]["results"]:
        grants.append(
            {
                "id": item.get("result_id"),
                "title": item.get("title", ""),
                "organization": item.get("source", ""),
                "url": item.get("url", ""),
                "description": item.get("excerpt", ""),
                "deadline": "Not stated",
                "funding": "Not stated",
                "eligibility": "Not stated",
                "category": genre or "Film Funding",
                "location": location or "Not stated",
            }
        )

    return {"grants": grants}
