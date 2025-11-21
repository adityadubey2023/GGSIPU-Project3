import google.generativeai as genai

# 1. API key yahi daal sakte ho (demo style)
#    (Better practice: env var se lo, but abhi tumhara demo yehi hai)
genai.configure(api_key="AIzaSyAtm15ZFknmgZwk0omTjNQk_GsC6M7144c")

# 2. Model exactly wahi jo tum use kar rahe ho
model = genai.GenerativeModel("gemini-flash-latest")


def fallback_insight(symbol, change, close_price):
    direction = "up" if change > 0 else "down" if change < 0 else "flat"
    return (
        f"[Fallback] {symbol}: price is {direction} ({change:+.2f}) at {close_price:.2f}. "
        f"LLM unavailable, using rule-based analysis."
    )


def generate_market_insight(symbol, change, close_price):
    """
    Ye function Pathway se call hoga.
    Bas prompt banata hai aur Gemini se analysis mangta hai.
    """

    print("\n=====================================================")
    print(f"[DEBUG] Gemini generate_market_insight for {symbol}")
    print("=====================================================\n")

    try:
        change = float(change)
        close_price = float(close_price)
    except Exception:
        return fallback_insight(symbol, change, close_price)

    prompt = f"""
You are a professional financial market analyst.
Write a short intraday analysis in clean, concise English.

Instrument:
- Symbol: {symbol}
- Absolute Change today: {change:+.2f}
- Last Close Price: {close_price:.2f}

Rules:
-Everthing Should be in detail analyse old rate of that stock previous record of the company profit loss statement and give a comprehesive info to user
- Trend should be based on magnitude and direction of the move.
- Explicitly state risk as: low / medium / high.
- Explain if the move looks like normal intraday noise or something meaningful.
- Write 5–7 bullet points.
- Make the analysis specific to this stock and this move, not generic filler text.
- Do NOT give investment advice, just describe behaviour and risk.
"""

    try:
        response = model.generate_content(prompt.strip())
        if not response or not getattr(response, "text", None):
            print("[ERROR] Gemini returned empty or invalid response.")
            return fallback_insight(symbol, change, close_price)

        return response.text.strip()

    except Exception as e:
        print("[EXCEPTION] Gemini crashed:", repr(e))
        return fallback_insight(symbol, change, close_price)
