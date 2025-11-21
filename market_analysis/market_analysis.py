import time
import pathway as pw
import yfinance as yf

from llm_client import generate_market_insight


# ============================
# 1. yfinance se data laana
# ============================

def fetch_market_data(symbol: str = "AAPL"):
    """
    Yahoo Finance (yfinance) se latest market data fetch karta hai.
    - API key ki zaroorat nahi
    - Project ke liye kaafi reliable
    """
    try:
        ticker = yf.Ticker(symbol)
        # Last 1 minute ka data le lo
        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            print("yfinance: empty history data")
            return None

        last = hist.tail(1).iloc[0]

        return {
            "symbol": symbol,
            "date": str(last.name),   # index is Timestamp
            "close": float(last["Close"]),
            "high": float(last["High"]),
            "low": float(last["Low"]),
            "open": float(last["Open"]),
        }
    except Exception as e:
        print("yfinance error:", e)
        return None


# ============================
# 2. Pathway Schema
# ============================

class MarketSchema(pw.Schema):
    symbol: str
    date: str
    close: float
    high: float
    low: float
    open: float


# ============================
# 3. Streaming Source
# ============================

class MarketStream(pw.io.python.ConnectorSubject):
    """
    Ye class har 60 second me yfinance se latest candle fetch karegi
    aur naya record Pathway ko push karegi.
    """

    def run(self) -> None:
        while True:
            data = fetch_market_data("AAPL")
            if data is not None:
                print("Fetched market data:", data)
                self.next(
                    symbol=data["symbol"],
                    date=data["date"],
                    close=data["close"],
                    high=data["high"],
                    low=data["low"],
                    open=data["open"],
                )

            # 1 minute ka gap – isko kam/zyada kar sakte ho
            time.sleep(60)


market_table = pw.io.python.read(
    MarketStream(),
    schema=MarketSchema,
    autocommit_duration_ms=2000,
)


# ============================
# 4. Basic Analytics
# ============================

def daily_change(open_price: float, close_price: float) -> float:
    return round(close_price - open_price, 2)


analytics = market_table.select(
    symbol=market_table.symbol,
    date=market_table.date,
    close=market_table.close,
    daily_change=pw.apply(daily_change, market_table.open, market_table.close),
)


# ============================
# 5. LLM Insights via OpenRouter
# ============================

insights = analytics.select(
    symbol=analytics.symbol,
    date=analytics.date,
    close_price=analytics.close,
    daily_change=analytics.daily_change,
    insight=pw.apply(
        generate_market_insight,
        analytics.symbol,
        analytics.daily_change,
        analytics.close,
    ),
)


# ============================
# 6. Output
# ============================

pw.io.jsonlines.write(insights, "market_insights.jsonl")


if __name__ == "__main__":
    pw.run()
