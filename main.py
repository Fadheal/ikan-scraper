from fastapi import FastAPI
from scraper.investing_scraper import investing_thisweek_scraper

app = FastAPI()
investingScrap = investing_thisweek_scraper()

@app.get("/")
def root():
    return {"IKAN"}

@app.get("/api/v1/scrap/investing")
def this_week_calendar():
    return investingScrap