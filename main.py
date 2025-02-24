from helpers import (
    datetime_to_isoformat,
    parse_events,
    generate_calendars
)

from datetime import datetime

import requests
import click

API_URL = "https://unical.prod.up.cineca.it/api/Impegni/getImpegniCalendarioPubblico"
CLIENT_ID = "5de6319d4414ab02f80b613a"

@click.command()
@click.option(
    "--id", "calendar_id",
    prompt="Inserisci ID calendario",
    help="ID del calendario pubblico"
)
@click.option(
    "--start", "start_date",
    prompt="Inserisci data inizio (YYYY-MM-DD)",
    help="Data inizio"
)
@click.option(
    "--end", "end_date",
    prompt="Inserisci data fine (YYYY-MM-DD)",
    help="Data fine"
)
def main(
    calendar_id: str,
    start_date: str,
    end_date: str
) -> None:
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    response = requests.post(
        url=API_URL,
        json={
            "clienteId": CLIENT_ID,
            "linkCalendarioId": calendar_id,
            "dataInizio": datetime_to_isoformat(start_date),
            "dataFine": datetime_to_isoformat(end_date)
        }
    )
    assert response.status_code == 200, "Request error"

    data = response.json()
    events = parse_events(data)
    generate_calendars(events)

if __name__ == "__main__":
    main()