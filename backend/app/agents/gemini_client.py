"""
Thin async wrapper around the google-generativeai SDK.
The SDK is synchronous — all calls are offloaded to a thread pool
to avoid blocking the FastAPI event loop.
"""
import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.config import settings

_executor = ThreadPoolExecutor(max_workers=4)


def _init_model() -> genai.GenerativeModel:
    genai.configure(api_key=settings.google_api_key)
    return genai.GenerativeModel(
        model_name=settings.gemini_model,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            temperature=0.3,
            max_output_tokens=8192,
        ),
    )


_model: genai.GenerativeModel | None = None


def get_model() -> genai.GenerativeModel:
    global _model
    if _model is None:
        _model = _init_model()
    return _model


def _strip_fences(text: str) -> str:
    """Remove markdown code fences Gemini occasionally wraps around JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


async def generate_json(prompt: str, retries: int = 3) -> dict | list:
    """Call Gemini and return parsed JSON. Retries with exponential backoff."""
    loop = asyncio.get_event_loop()
    last_exc: Exception | None = None

    for attempt in range(retries):
        try:
            model = get_model()
            response = await loop.run_in_executor(_executor, lambda: model.generate_content(prompt))
            raw = response.text
            cleaned = _strip_fences(raw)
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            last_exc = exc
            await asyncio.sleep(2 ** attempt)
        except Exception as exc:
            last_exc = exc
            # Rate limit or transient error
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError(f"Gemini call failed after {retries} attempts: {last_exc}") from last_exc
