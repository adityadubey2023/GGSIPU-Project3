import os
import requests
import json

# ================================================================
# ENV-BASED API KEY (YOU MUST SET IN TERMINAL or ~/.zshrc)
# ================================================================

OPENROUTER_API_KEY = os.getenv("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", "")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ==========================
# MULTI-MODEL ROTATION LIST
# ==========================

FREE_MODELS = [
    "x-ai/grok-4.1-fast:free",
    "z-ai/glm-4.5-air:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "deepseek/deepseek-r1-0528:free",
    "qwen/qwen3-coder:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "google/gemma-3-27b-it:free",
]


# ================================================================
# RULE-BASED FALLBACK
# ================================================================

def fallback_insight(symbol, change, close_price):
    direction = "up" if change > 0 else "down" if change < 0 else "flat"
    return (
        f"[Fallback] {symbol}: price is {direction} ({change:+.2f}) at {close_price:.2f}. "
        f"LLM unavailable, using rule-based analysis."
    )


# ================================================================
# MAIN FUNCTION (called from Pathway)
# ================================================================

def generate_market_insight(symbol, change, close_price):
    print("\n=====================================================")
    print(f"[DEBUG] LLM call triggered for {symbol}")
    print("=====================================================\n")

    if not OPENROUTER_API_KEY or not OPENROUTER_API_KEY.startswith("sk-or-"):
        print("[ERROR] Missing or invalid OPENROUTER_API_KEY")
        return fallback_insight(symbol, change, close_price)

    prompt = f"""
You are a professional financial market analyst.
Write a short intraday analysis in clean, concise English.

Instrument:
- Symbol: {symbol}
- Change: {change:+.2f}
- Last Close: {close_price:.2f}

Rules:
- Trend should be based on magnitude and direction of move.
- Mention risk (low/medium/high).
- Explain if the move is normal intraday noise or meaningful.
- Write 5–7 bullet points.
- Must be unique for this specific stock. No generic filler.
"""

    # Try each model one by one
    for model in FREE_MODELS:
        print(f"\n[DEBUG] Trying model: {model}")

        body = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt.strip()}
            ],
            "max_tokens": 220,
            "temperature": 0.9,
            "top_p": 0.9,
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "GGSIPU-Financial-Monitoring",
        }

        try:
            print("[DEBUG] Sending request to OpenRouter...")
            resp = requests.post(OPENROUTER_URL, json=body, headers=headers, timeout=40)
            print(f"[DEBUG] HTTP Status = {resp.status_code}")

            if resp.status_code != 200:
                print("[ERROR] Model failed:", model, resp.text[:180])
                continue

            data = resp.json()

            if "error" in data:
                print("[ERROR] API Model Error:", data["error"])
                continue

            content = data["choices"][0]["message"]["content"]
            if not content:
                print("[ERROR] Model returned empty content.")
                continue

            print(f"[DEBUG] SUCCESS with model: {model}")
            return content.strip()

        except Exception as e:
            print(f"[EXCEPTION] Model crashed: {model} → {repr(e)}")
            continue

    print("[ERROR] ALL MODELS FAILED → fallback triggered.")
    return fallback_insight(symbol, change, close_price)
