import os
import requests
import json

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Sirf ek model se test pehle:
TEST_MODEL = "meta-llama/llama-3.2-3b-instruct:free"

def main():
    print("=== OpenRouter Test Script ===")
    has_key = bool(OPENROUTER_API_KEY)
    print("API key present? ->", has_key)
    if has_key:
        print("Key prefix:", OPENROUTER_API_KEY[:10], "...")

    if not has_key:
        print("❌ OPENROUTER_API_KEY missing. Set it with: export OPENROUTER_API_KEY=sk-or-<key>")
        return
    if not OPENROUTER_API_KEY.startswith("sk-or-"):
        print("❌ OPENROUTER_API_KEY appears invalid (missing 'sk-or-' prefix). Aborting.")
        return

    prompt = "You are a test bot. Reply with one short sentence saying: 'OpenRouter test successful for Aditya.'"

    body = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50,
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "GGSIPU-OpenRouter-Test",
    }

    print("\n→ Sending request to OpenRouter...")
    try:
        resp = requests.post(OPENROUTER_URL, json=body, headers=headers, timeout=40)
        print("HTTP status:", resp.status_code)

        # Response ka raw text dikhao
        print("\n--- RAW RESPONSE (first 800 chars) ---")
        print(resp.text[:800])
        print("--- END RAW RESPONSE ---\n")

        if resp.status_code != 200:
            print("❌ Non-200 response, something wrong.")
            return

        data = resp.json()
        if "error" in data:
            print("❌ API returned error object:", data["error"])
            return

        content = data["choices"][0]["message"]["content"]
        print("✅ Parsed content:")
        print(content)

    except Exception as e:
        print("❌ Exception occurred:", repr(e))


if __name__ == "__main__":
    main()
