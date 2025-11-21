import time
import os
import pathway as pw
import yfinance as yf

from llm_client import generate_market_insight

# ============================
# 1. CONFIG
# ============================

SYMBOLS = [
    # ---------- India (NSE) ----------
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ITC.NS", "LT.NS",
    "BHARTIARTL.NS", "ASIANPAINT.NS", "HCLTECH.NS", "WIPRO.NS",
    "MARUTI.NS", "TITAN.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS",
    "ADANIENT.NS", "ADANIPORTS.NS",

    # ---------- US ----------
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "NFLX",
    "JPM", "V", "MA", "JNJ", "UNH", "PG", "DIS", "INTC", "CSCO", "ORCL",
    "PYPL", "AMD",

    # ---------- Europe ----------
    "NESN.SW", "SIE.DE", "AIR.PA", "SAP.DE", "MC.PA",
    "ASML.AS", "RDSA.AS", "ULVR.L", "HSBA.L", "BP.L",

    # ---------- Asia ex-India ----------
    "0700.HK", "9988.HK", "7203.T", "6758.T", "005930.KS",

    # ---------- Crypto ----------
    "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",

    # ---------- FX ----------
    "USDINR=X", "EURUSD=X", "GBPUSD=X",
]

POLL_INTERVAL_SECONDS = 60


# ============================
# 2. Data Fetch
# ============================

def fetch_market_data(symbol: str):
    try:
        ticker = yf.Ticker(symbol)

        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            hist = ticker.history(period="5d", interval="5m")
        if hist.empty:
            hist = ticker.history(period="5d", interval="15m")
        if hist.empty:
            hist = ticker.history(period="1mo", interval="30m")

        if hist.empty:
            print(f"[WARN] No data found for {symbol}")
            return None

        last = hist.tail(1).iloc[0]

        return dict(
            symbol=symbol,
            date=str(last.name),
            close=float(last["Close"]),
            high=float(last["High"]),
            low=float(last["Low"]),
            open=float(last["Open"])
        )
    except Exception as e:
        print(f"[ERROR] {symbol}:", e)
        return None


# ============================
# 3. Pathway Schema
# ============================

class MarketSchema(pw.Schema):
    symbol: str
    date: str
    close: float
    high: float
    low: float
    open: float


# ============================
# 4. Streaming Source
# ============================

class MultiSymbolMarketStream(pw.io.python.ConnectorSubject):
    def run(self):
        while True:
            print("\n[INFO] Fetching...")
            for sym in SYMBOLS:
                data = fetch_market_data(sym)
                if data:
                    print("PUSH:", data)
                    self.next(**data)
                else:
                    print("SKIP:", sym)
            time.sleep(POLL_INTERVAL_SECONDS)


market_table = pw.io.python.read(
    MultiSymbolMarketStream(),
    schema=MarketSchema,
    autocommit_duration_ms=2000,
)


# ============================
# 5. Analytics
# ============================

def price_change(op, cl):
    return cl - op

def price_change_pct(op, cl):
    if op == 0:
        return 0.0
    return (cl - op) / op * 100


analytics = market_table.select(
    **market_table,  # keep original fields
    change_abs=pw.apply(price_change, market_table.open, market_table.close),
    change_pct=pw.apply(price_change_pct, market_table.open, market_table.close),
)


# ============================
# 6. LLM insight generation
# ============================

insights = analytics.select(
    **analytics,
    insight=pw.apply(
        lambda s, d, c: generate_market_insight(s, d, c) or "Insight unavailable",
        analytics.symbol,
        analytics.change_abs,
        analytics.close,
    )
)


# ============================
# 7. Output JSON
# ============================

OUTFILE = os.path.join(os.path.dirname(__file__), "multi_market_insights.jsonl")

# Write JSONL to the script directory to avoid confusion about CWD
pw.io.jsonlines.write(insights, OUTFILE)


if __name__ == "__main__":
    pw.run()
