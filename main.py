from fastapi import FastAPI, HTTPException
from scraper.investing_thisweek_scraper import investing_thisweek_scraper
from scraper.investing_thisday_scraper import investing_thisday_scraper

app = FastAPI()
investingScrapThisweek = investing_thisweek_scraper()
investingScrapThisday = investing_thisday_scraper()

@app.get("/")
def root():
    return {"IKAN"}

@app.get("/api/v1/scrap/investing/economic-calendar/{timeframe}")
def economic_calendar(timeframe):
    if timeframe == 'thisweek':
        return investingScrapThisweek
    elif timeframe == 'thisday':
        return investingScrapThisday
    else :
        raise HTTPException(
            status_code=404,
            detail=f"no valid timeframe: {timeframe}"
        )
        