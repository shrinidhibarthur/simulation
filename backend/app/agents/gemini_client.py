"""
Async wrapper around the google-genai SDK (REST-based, replaces deprecated google-generativeai).
All generate_content calls are offloaded to a thread pool so they don't block FastAPI's event loop.
"""
import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor

from google import genai
from google.genai import types

from app.config import settings

_executor = ThreadPoolExecutor(max_workers=4)
_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


def _make_config(temperature: float = 0.3) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=temperature,
        max_output_tokens=8192,
    )


def _strip_fences(text: str) -> str:
    """Strip markdown code fences Gemini sometimes adds even in JSON mode."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _sync_generate(prompt: str, temperature: float) -> str:
    client = get_client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=_make_config(temperature),
    )
    return response.text


async def generate_json(prompt: str, temperature: float = 0.3, retries: int = 3) -> dict | list:
    """
    Call Gemini and return parsed JSON.
    Offloads the synchronous SDK call to a thread pool executor.
    Retries with exponential backoff on transient errors.
    """
    loop = asyncio.get_event_loop()
    last_exc: Exception | None = None

    for attempt in range(retries):
        try:
            raw = await loop.run_in_executor(_executor, lambda: _sync_generate(prompt, temperature))
            cleaned = _strip_fences(raw)
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            last_exc = exc
            await asyncio.sleep(2 ** attempt)
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError(f"Gemini call failed after {retries} attempts: {last_exc}") from last_exc
