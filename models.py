from pydantic import BaseModel
from datetime import datetime

class EventModel(BaseModel):
    id: str
    subject: str
    start: datetime
    end: datetime
    location: str
    group: str
    color: str
    description: str