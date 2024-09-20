from pydantic import BaseModel
from datetime import datetime

class EventModel(BaseModel):
    id: str
    subject: str
    start: datetime
    end: datetime
    structure: str
    group: str