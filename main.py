from fastapi import FastAPI, HTTPException

from scraper.investing_scraper import investing_thisweek_scraper
from scraper.investing_scraper import investing_thisday_scraper
from scraper.bankholiday_thisweek_scrapper import bankholiday_thisweek_scraper
from scraper.bankholiday_thisday_scrapper import bankholiday_thisday_scraper
from scraper.investing_markets import investing_markets_currencies
from scraper.investing_markets import get_names
from scraper.yahoo_news import economic_news

from redis import Redis
import httpx
import json
from scraper.yahoo_news import get_news_title
import asyncio
from redis import asyncio as aioredis

import socketio

app = FastAPI()
investingScrapThisweek = investing_thisweek_scraper()
investingScrapThisday = investing_thisday_scraper()
bankholiday_thisweek = bankholiday_thisweek_scraper()
bankholiday_thisday = bankholiday_thisday_scraper()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)

ws = socketio.ASGIApp(sio, other_asgi_app=app)

stop_event = asyncio.Event()
background_task: asyncio.Task | None = None

# WebSocket

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    return True

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


# API
@app.get("/")
async def root():
    return {"IKAN"}

async def background_loop():
    while not stop_event.is_set(): 
        print("⏳ Running scheduled task...")
        await asyncio.wait_for(fetching(), timeout=10)

        await asyncio.sleep(20) 

@app.on_event("startup")
async def startup_event():
    app.state.redis = aioredis.Redis(host='localhost', port=6379)
    app.state.http_client = httpx.AsyncClient()
    global background_task
    stop_event.clear()
    background_task = asyncio.create_task(background_loop())

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down background loop...")
    stop_event.set()
    if background_task:
        background_task.cancel()   # cancel the running task
        try:
            await background_task  # wait for cancellation
        except asyncio.CancelledError:
            print("✅ Background task cancelled")
    app.state.redis.close()



@app.get("/api/v1/scrap/investing/economic-calendar/{calendar}")
async def economic_calendar(calendar):
    if calendar == 'thisweek':
        return investingScrapThisweek
    elif calendar == 'thisday':
        return investingScrapThisday
    else :
        raise HTTPException(
            status_code=404,
            detail=f"no valid calendar: {calendar}"
        )

@app.get("/api/v1/scrap/investing/bank-holiday/{calendar}")
async def bank_holiday(calendar):
    if calendar == 'thisweek':
        return bankholiday_thisweek
    elif calendar == 'thisday':
        return bankholiday_thisday
    else :
        raise HTTPException(
            status_code=404,
            detail=f"no valid calendar: {calendar}"
        )

@app.get("/api/v1/scrap/investing/markets/{types}")
async def markets(types):
    if types == 'currencies':
        return investing_markets_currencies()
    
@app.get("/api/v1/news")
async def news():
    value = app.state.redis.get('news')
    return json.loads(value)

async def fetching():
    print('ping')
    value = await app.state.redis.get('news')
    cache = await app.state.redis.get('title_cache')

    print('ok')

    title = await asyncio.to_thread(get_news_title)

    print('ok')

    print(title)
    print(cache.decode("utf-8"))

    if value is None:
        value = await asyncio.to_thread(economic_news)
        data_str = json.dumps(value)
        await app.state.redis.set('news', data_str)
        await app.state.redis.set('title_cache', title)

    elif title != cache.decode("utf-8"):
        print("title is diff, cache updated")
        value = await asyncio.to_thread(economic_news)
        data_str = json.dumps(value)
        await app.state.redis.set('news', data_str)
        await app.state.redis.set('title_cache', title)

        await sio.emit("new_news", data_str)
