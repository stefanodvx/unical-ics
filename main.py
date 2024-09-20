from pydantic import BaseModel
from datetime import datetime

import requests
import icalendar
import json

API_URL = "https://unical.prod.up.cineca.it/api/Impegni/getImpegniCalendarioPubblico"
CLIENT_ID = "5de6319d4414ab02f80b613a" # ?

CALENDAR_ID = input("Inserisci ID calendario: ")

class Event(BaseModel):
    id: str
    subject: str
    start: datetime
    end: datetime
    structure: str
    group: str

def date_to_str(obj: datetime) -> str:
    return obj.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def str_to_date(obj: str) -> datetime:
    return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.000Z")

def parse_events(data: list) -> list["Event"]:
    events = []
    for event in data:
        start = str_to_date(event["dataInizio"])
        end = str_to_date(event["dataFine"])

        event_info = event["evento"]
        structure_info = event["edifici"][0]
        structure = structure_info["descrizione"]
        details = event_info["dettagliDidattici"][0]
        partition = details["partizione"]
        description = partition["descrizione"]
        group = description.split(" ", maxsplit=1)[-1]

        events.append(Event(
            id=event_info["_id"],
            subject=details["nome"],
            start=start,
            end=end,
            group=group,
            structure=structure
        ))
    return events

def generate_calendars(events: list["Event"]) -> str:
    group_a = icalendar.Calendar()
    group_b = icalendar.Calendar()

    for event in events:
        obj = icalendar.Event()
        obj.add("name", event.subject)
        obj.add("summary", event.subject)
        obj.add("dtstart", event.start)
        obj.add("dtend", event.end)
        obj.add("location", event.structure)
        if event.group == "A":
            group_a.add_component(obj)
        elif event.group == "B":
            group_b.add_component(obj)

    with open("group_a.ics", "wb+") as f:
        f.write(group_a.to_ical())

    with open("group_b.ics", "wb+") as f:
        f.write(group_b.to_ical())

def main():
    response = requests.post(
        url=API_URL,
        json={
            "clienteId": CLIENT_ID,
            "linkCalendarioId": CALENDAR_ID,
            "dataInizio": date_to_str(datetime(2024, 9, 1, 22, 0, 0)),
            "dataFine": date_to_str(datetime(2025, 6, 30, 22, 0, 0))
        }
    )
    assert response.status_code == 200, "Errore nella richiesta"

    data = response.json()
    events = parse_events(data)
    generate_calendars(events)

if __name__ == "__main__":
    main()