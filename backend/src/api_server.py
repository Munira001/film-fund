import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from filmfund_adk_agent import search_film_funding

app = FastAPI(title="Film Fund API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


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
