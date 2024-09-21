from models import EventModel
from datetime import datetime

import icalendar

COLORS = {"A": "mediumpurple", "B": "palegreen"}

def date_to_str(obj: datetime) -> str:
    return obj.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def str_to_date(obj: str) -> datetime:
    return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.000Z")

def parse_events(data: list) -> list["EventModel"]:
    events = []
    for event in data:
        start = str_to_date(event["dataInizio"])
        end = str_to_date(event["dataFine"])

        event_info = event["evento"]
        classroom_info = event["aule"][0]
        classroom = classroom_info["descrizione"]
        building = classroom_info["edificio"]["descrizione"]
        teachers = ", ".join(
            f"{x['cognome']} {x['nome']}"
            for x in event["docenti"]
        ) if len(event.get("docenti", [])) > 0 else ""
        description = f"Teachers: {teachers}"
        location = f"{building}: Aula {classroom}"
        details = event_info["dettagliDidattici"][0]
        partition = details["partizione"]
        group = partition["descrizione"].split(
            " ", maxsplit=1)[-1]
        color = COLORS.get(group)

        events.append(
            EventModel(
                id=event_info["_id"],
                subject=details["nome"],
                start=start,
                end=end,
                group=group,
                location=location,
                color=color,
                description=description
            )
        )
    return events

def generate_calendars(events: list["EventModel"]) -> None:
    group_a = icalendar.Calendar()
    group_b = icalendar.Calendar()

    for event in events:
        obj = icalendar.Event()
        obj.add("uid", event.id)
        obj.add("name", event.subject)
        obj.add("summary", event.subject)
        obj.add("dtstart", event.start)
        obj.add("dtend", event.end)
        obj.add("location", event.location)
        obj.add("color", event.color)
        obj.add("description", event.description)
        if event.group == "A":
            group_a.add_component(obj)
        elif event.group == "B":
            group_b.add_component(obj)

    with open("group_a.ics", "wb+") as f:
        f.write(group_a.to_ical())

    with open("group_b.ics", "wb+") as f:
        f.write(group_b.to_ical())