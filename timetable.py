import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from ics import Calendar, Event

def login(session):
    base_url = os.getenv("BASE_URL")
    login_url = os.getenv("LOGIN_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    response = session.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    token = soup.find("input", {"name": "form[_token]"})["value"]
    payload = {
        "form[username]": username,
        "form[password]": password,
        "form[_token]": token,
    }
    response = session.post(login_url, data=payload)
    response.raise_for_status()
    return session

def scrape_table(session):
    c = Calendar()
    timetable_url = os.getenv("TIMETABLE_URL")

    response = session.get(timetable_url)
    soup = BeautifulSoup(response.text, "html.parser")
    periods = soup.find_all("td", {"class": "cell-item", "data-start": True, "data-end": True})
    for x in periods:
        e = Event()
        e.name = x.find("span", {"class": "title"}).get_text()
        e.begin = x.get("data-start")
        e.end = x.get("data-end")
        c.events.add(e)
    with open("timetable.ics", "w") as f:
        f.writelines(c.serialize_iter())

if __name__ == "__main__":
    load_dotenv()
    session = requests.Session()
    login(session)
    scrape_table(session)