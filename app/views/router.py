from fastapi import APIRouter, Security
from fastapi_jwt import JwtAuthorizationCredentials

from app.schemas.schemas import (
    PlayRolletColorSchema,
    PlayRolletNumberSchema,
    PlaySlotsSchema,
    PlayRollDiceSchema
)
from app.store.user_repository import UserRepository, access_security

game = APIRouter(prefix="/games", tags=["games"])

user_repository = UserRepository()


@game.post("/rollet/cplay")
async def play_rollet_by_colour(
        play: PlayRolletColorSchema,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    result = await user_repository.play_rollet_by_colour(play, credentials)
    return result

@game.post("/rollet/nplay")
async def play_rollet_by_number(
        play: PlayRolletNumberSchema,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    result = await user_repository.play_rollet_by_number(play, credentials)
    return result

@game.post("/slots/play")
async def play_slots(
        play: PlaySlotsSchema,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    result = await user_repository.play_slots(play, credentials)
    return result

@game.post("/roll_dice/play")
async def play_roll_dice(
        play: PlayRollDiceSchema,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    result = await user_repository.play_roll_dice(play, credentials)
    return result
