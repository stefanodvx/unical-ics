from helpers import (
    date_to_str,
    parse_events,
    generate_calendars
)

from datetime import datetime

import requests

API_URL = "https://unical.prod.up.cineca.it/api/Impegni/getImpegniCalendarioPubblico"
CLIENT_ID = "5de6319d4414ab02f80b613a"

def main():
    calendar_id = input("Inserisci ID calendario: ")

    response = requests.post(
        url=API_URL,
        json={
            "clienteId": CLIENT_ID,
            "linkCalendarioId": calendar_id,
            "dataInizio": date_to_str(datetime(2024, 9, 1, 22, 0, 0)),
            "dataFine": date_to_str(datetime(2025, 6, 30, 22, 0, 0))
        }
    )
    assert response.status_code == 200, "Request error"

    data = response.json()
    events = parse_events(data)
    generate_calendars(events)

if __name__ == "__main__":
    main()