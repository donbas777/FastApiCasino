import enum

from pydantic import BaseModel, Field


class Colours(str, enum.Enum):
    green = "green"
    red = "red"
    black = "black"

class PlayRolletColorSchema(BaseModel):
    bet: float
    color: Colours

class PlayRolletNumberSchema(BaseModel):
    bet: float
    number: int = Field(..., ge=0, le=36)

class PlaySlotsSchema(BaseModel):
    bet: float

class RefillBalanceSchema(BaseModel):
    bet: float

class PlayRollDiceSchema(BaseModel):
    bet: float
    greater_then_7: bool = True

