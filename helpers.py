from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional
from models import EventModel

import icalendar

TIMEZONE = ZoneInfo("Europe/Rome")
COLORS = {"A": "mediumpurple", "B": "palegreen"}

def datetime_to_isoformat(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def isoformat_to_datetime(iso_str: str) -> datetime:
    dt = datetime.fromisoformat(iso_str.replace(".000Z", ""))
    return dt.replace(tzinfo=timezone.utc).astimezone(TIMEZONE)

def get_teachers(docenti: list[dict]) -> str:
    return ", ".join(f"{d['cognome']} {d['nome']}" for d in docenti) if docenti else ""

def get_location(classroom_entry: dict) -> Optional[str]:
    if not classroom_entry:
        return None
    classroom = classroom_entry.get("descrizione")
    building = classroom_entry.get("edificio", {}).get("descrizione")
    return f"{building}: Aula {classroom}" if building and classroom else None

def get_study_group(partition_entry: dict) -> Optional[str]:
    description = partition_entry.get("descrizione", "")
    parts = description.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else None

def parse_events(raw_data: list[dict]) -> list[EventModel]:
    events = []

    for idx, entry in enumerate(raw_data):
        event_info = entry.get("evento")
        if not event_info:
            continue
        try:
            start = isoformat_to_datetime(entry["dataInizio"])
            end = isoformat_to_datetime(entry["dataFine"])
        except (KeyError, ValueError):
            continue
        classroom_info = entry.get("aule", [])
        if not classroom_info:
            continue
        location = get_location(classroom_info[0])
        if not location:
            continue

        details = event_info.get("dettagliDidattici", [{}])
        if not details:
            continue
        details = details[0]
        if not details:
            continue
        teachers = get_teachers(entry.get("docenti", []))
        description = f"Docenti: {teachers}" if teachers else ""

        partitions = entry.get("fattoreDiPartizione", [{}])
        if not partitions:
            continue
        partitions = partitions[0].get("partizioni", [])
        if not partitions:
            continue
        group = get_study_group(partitions[0])
        if not group:
            continue
        if not details.get("nome"):
            continue
        events.append(
            EventModel(
                id=str(idx) + event_info["_id"],
                subject=details["nome"],
                start=start,
                end=end,
                group=group,
                location=location,
                color=COLORS.get(group[0], ""),
                description=description
            )
        )
    
    return events

def create_ical_event(event: EventModel) -> icalendar.Event:
    cal_event = icalendar.Event()
    cal_event.add("uid", event.id)
    cal_event.add("summary", event.subject)
    cal_event.add("dtstart", event.start)
    cal_event.add("dtend", event.end)
    cal_event.add("location", event.location)
    
    if event.description:
        cal_event.add("description", event.description)
    if event.color:
        cal_event.add("x-apple-color", event.color)
        cal_event.add("color", event.color)
    
    return cal_event

def generate_calendars(events: list[EventModel]) -> None:
    calendars = {
        "A": icalendar.Calendar(),
        "B": icalendar.Calendar()
    }

    for event in events:
        if event.group not in calendars:
            continue
        calendars[event.group].add_component(create_ical_event(event))

    for group, calendar in calendars.items():
        with open(f"group_{group.lower()}.ics", "wb") as f:
            f.write(calendar.to_ical())