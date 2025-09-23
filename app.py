from datetime import datetime
from dateutil import tz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from ics import Calendar, Event
from flask import Flask, redirect

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

app = Flask(__name__)

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

def get_timetable(session):
    c = Calendar()
    timetable_url = os.getenv("TIMETABLE_URL")

    response = session.get(timetable_url)
    soup = BeautifulSoup(response.text, "html.parser")
    periods = soup.find_all("td", {"class": "cell-item", "data-start": True, "data-end": True})
    for x in periods:
        e = Event()
        e.name = x.find("span", {"class": "title"}).get_text()
        start_time = datetime.strptime(x.get("data-start"), DATE_FORMAT).replace(tzinfo=tz.gettz('Europe/London'))
        end_time = datetime.strptime(x.get("data-end"), DATE_FORMAT).replace(tzinfo=tz.gettz('Europe/London'))
        e.begin = start_time.astimezone(tz.tzutc()).strftime(DATE_FORMAT)
        e.end = end_time.astimezone(tz.tzutc()).strftime(DATE_FORMAT)
        c.events.add(e)
    return c.serialize()

@app.route("/")
def home():
    return redirect("/timetable.ics")

@app.route('/timetable.ics')
def timetable():
    session = requests.Session()
    login(session)
    calendar_data = get_timetable(session)
    return calendar_data, {'Content-Type': 'text/calendar'}

if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", port=5000, debug=True)