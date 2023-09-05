
from pydantic import BaseModel

class ContestantRegistration(BaseModel):
    contestantName: str
    husbandName: str
    vocalRange: int
    location: int

class PowerUpItem(BaseModel):
    item: str
    boost: int

