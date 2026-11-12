from fastapi import FastAPI, HTTPException
import yfinance as yf

app = FastAPI(
    title="Multibagger Stock Screener API",
    description="API Backend untuk menyaring saham berdasarkan strategi Value, Growth, dan Corporate Action",
    version="1.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Selamat datang di Multibagger Screener API via GitHub!",
        "docs_url": "/docs"
    }

@app.get("/api/screen/{ticker}")
def screen_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        name = info.get("longName", "Tidak diketahui")
        sector = info.get("sector", "Tidak diketahui")
        per = info.get("trailingPE", None)
        pbv = info.get("priceToBook", None)
        roe = info.get("returnOnEquity", None)
        revenue_growth = info.get("revenueGrowth", None)
        
        roe_pct = (roe * 100) if roe is not None else 0.0
        rev_growth_pct = (revenue_growth * 100) if revenue_growth is not None else 0.0
        
        is_value = (per is not None and 0 < per <= 15.0) and (pbv is not None and pbv <= 2.0)
        is_growth = (rev_growth_pct >= 15.0) and (roe_pct >= 15.0)
        
        score = 0
        if is_value: score += 40
        if is_growth: score += 40
        if per and per < 10: score += 20

        return {
            "ticker": ticker.upper(),
            "company_name": name,
            "sector": sector,
            "metrics": {
                "per": per,
                "pbv": pbv,
                "roe_pct": round(roe_pct, 2),
                "revenue_growth_pct": round(rev_growth_pct, 2),
            },
            "evaluation": {
                "passed_value_criteria": is_value,
                "passed_growth_criteria": is_growth,
                "multibagger_score": score,
                "status": "Potensi Tinggi" if score >= 60 else "Belum Memenuhi Syarat Optimal"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Gagal: {str(e)}")
      
