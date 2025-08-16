from bs4 import BeautifulSoup
import requests
from collections import defaultdict

def investing_thisweek_scraper():
    url = 'https://www.investing.com/economic-calendar/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'From': 'fadheeal@gmail.com'
    }

    headers2 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.investing.com/economic-calendar/"

    }

    session = requests.Session()
    session.get("https://www.investing.com/economic-calendar/")
    session.headers.update(headers)
    payload = {
        "importance[]": 3,
        "timeZone": 27,
        "timeFilter": "timeRemain",
        "currentTab": "thisWeek",
        "submitFilters": 1,
        "limit_from": 0
    }

    r = session.post("https://www.investing.com/economic-calendar/Service/getCalendarFilteredData", data=payload, headers=headers2)

    # new_tr = r.content.find_all("tr")

    source = r.json()["data"]

    soup = BeautifulSoup(source, "html.parser")

    rows = soup.find_all("tr", class_="js-event-item")

    data = []
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        datetime = row.get("data-event-datetime")
        date_only = datetime.split(" ")[0] if datetime else None
        time = cells[0].get_text(strip=True)
        country = cells[1].get_text(strip=True)
        imp = 3
        event = cells[3].get_text(strip=True)
        actual = cells[4].get_text(strip=True) if len(cells) > 4 else None
        forecast = cells[5].get_text(strip=True) if len(cells) > 5 else None
        previous = cells[6].get_text(strip=True) if len(cells) > 6 else None

        data.append({
            "time": time,
            "country": country,
            "imp": imp,
            "event": event,
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
            "date": date_only
        })

    return data