"""
Thin wrapper around the Ollama API (gpt-oss model), configured to use
Ollama's CLOUD API (https://ollama.com) with an API key instead of a
locally pulled model. 

"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()  # this reads .env file in the current working directory into os.environ

# Ollama Cloud's OpenAI-compatible chat endpoint.
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
MODEL_NAME = "gpt-oss:120b-cloud"  
REQUEST_TIMEOUT_SECONDS = 60

API_KEY = os.environ.get("OLLAMA_API_KEY")



def call_ollama(prompt: str, expect_json: bool = False) -> str | None:
    """
    Sends a prompt to Ollama Cloud and returns the raw text response.
    Returns None on any failure (missing key, connection error, timeout,
    bad status code) so callers can fall back gracefully instead of crashing.
    """
    if not API_KEY:
        print("[llm_client] OLLAMA_API_KEY not set -- skipping LLM call, using fallback.")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0},  
    }
    if expect_json:
        payload["format"] = "json"  # If JSON output is expected, I request Ollama's structured JSON mode.

    try:
        response = requests.post(
            OLLAMA_CLOUD_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        # Chat endpoint returns {"message": {"role": ..., "content": ...}, ...}
        return data.get("message", {}).get("content", "").strip()
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"[llm_client] Ollama Cloud call failed, will use fallback. Reason: {e}")
        return None


def call_ollama_json(prompt: str) -> dict | None:
    """
    Convenience wrapper for calls where we expect a JSON object back.
    Returns a parsed dict, or None if the call failed or the response
    wasn't valid JSON (e.g. the model added stray commentary).
    """
    raw = call_ollama(prompt, expect_json=True)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("[llm_client] Model did not return valid JSON, using fallback.")
        return None
