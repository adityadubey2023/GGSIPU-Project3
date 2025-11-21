# api_server.py

import json
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Financial Monitoring API", version="1.0.0")

# CORS so that frontend (localhost) can call this API easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev, open; you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INSIGHTS_FILE = Path("market_analysis") / "multi_market_insights.jsonl"


def load_latest_insights() -> List[Dict[str, Any]]:
    """
    Reads the JSONL file and returns the latest record per symbol.
    """
    if not INSIGHTS_FILE.exists():
        raise FileNotFoundError(f"{INSIGHTS_FILE} not found")

    latest_by_symbol: Dict[str, Dict[str, Any]] = {}

    with INSIGHTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            symbol = record.get("symbol")
            if not symbol:
                continue

            # Overwrite – last occurrence in file is "latest"
            latest_by_symbol[symbol] = record

    # Convert dict -> list
    return list(latest_by_symbol.values())


@app.get("/api/market/latest")
def get_latest_market_insights() -> List[Dict[str, Any]]:
    """
    Returns the latest insights for all symbols.
    """
    try:
        data = load_latest_insights()
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Insights file not found. Run the Pathway pipeline first.")


@app.get("/api/market/symbol/{symbol}")
def get_symbol_insights(symbol: str) -> Dict[str, Any]:
    """
    Returns the latest insight for a specific symbol (e.g. AAPL, RELIANCE.NS).
    """
    try:
        data = load_latest_insights()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Insights file not found. Run the Pathway pipeline first.")

    for record in data:
        if record.get("symbol") == symbol:
            return record

    raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
