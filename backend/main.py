import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel, HttpUrl


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="AI Web Scraper API",
    version="1.0.0",
)


# ============================================================
# CORS configuration
# ============================================================

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Gemini configuration
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )
else:
    gemini_client = None


# ============================================================
# Request / Response models
# ============================================================

class SummarizeRequest(BaseModel):
    url: HttpUrl


class SummarizeResponse(BaseModel):
    url: str
    summary: str


# ============================================================
# Clean scraped text
# ============================================================

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# Scrape webpage
# ============================================================

def scrape_page(url: str) -> str:

    parsed = urlparse(url)

    # Only allow HTTP/HTTPS URLs
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(
            status_code=400,
            detail="Only HTTP and HTTPS URLs are supported.",
        )

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; AIWebScraper/1.0)"
                )
            },
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        raise HTTPException(
            status_code=400,
            detail=f"Could not fetch webpage: {exc}",
        ) from exc

    # Make sure the response is HTML
    content_type = response.headers.get(
        "content-type",
        "",
    )

    if "text/html" not in content_type.lower():

        raise HTTPException(
            status_code=400,
            detail="The URL does not point to an HTML webpage.",
        )

    # Parse HTML
    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # Remove unnecessary elements
    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        element.decompose()

    # Prefer meaningful content
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    # Extract readable text
    text = clean_text(
        main.get_text(
            " ",
            strip=True,
        )
    )

    if not text:

        raise HTTPException(
            status_code=422,
            detail="No readable text was found on the webpage.",
        )

    # Limit the amount of text sent to Gemini
    return text[:30000]


# ============================================================
# Gemini summarization
# ============================================================

def summarize_with_gemini(text: str) -> str:

    if not gemini_client:

        raise HTTPException(
            status_code=500,
            detail=(
                "GEMINI_API_KEY is not configured. "
                "Add it to backend/.env."
            ),
        )

    prompt = (
        "Summarize the webpage content below in "
        "4-6 concise bullet points.\n\n"

        "Focus on:\n"
        "- Main ideas\n"
        "- Important facts\n"
        "- Key conclusions\n\n"

        "Do not invent information that is not present "
        "in the webpage content.\n\n"

        "WEBPAGE CONTENT:\n"
        f"{text}"
    )

    try:

        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        summary = (response.text or "").strip()

        if not summary:

            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty summary.",
            )

        return summary

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"Gemini summarization error: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "AI summarization failed. "
                f"Gemini error: {exc}"
            ),
        ) from exc


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI Web Scraper API is running"
    }


# ============================================================
# Health endpoint
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "gemini_configured": bool(
            gemini_client
        ),
    }


# ============================================================
# Summarize endpoint
# ============================================================

@app.post(
    "/summarize",
    response_model=SummarizeResponse,
)
def summarize(
    request: SummarizeRequest,
):

    # Convert URL to string
    url = str(request.url)

    # 1. Scrape webpage
    text = scrape_page(url)

    # 2. Generate AI summary
    summary = summarize_with_gemini(text)

    # 3. Return response
    return SummarizeResponse(
        url=url,
        summary=summary,
    )