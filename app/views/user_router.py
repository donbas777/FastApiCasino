from fastapi import APIRouter, Security, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials

from app.schemas.schemas import RefillBalanceSchema
from app.store.user_repository import UserRepository, access_security

user = APIRouter(prefix="/users", tags=["users"])

user_repository = UserRepository()



@user.get("/my_balance")
async def get_balance(credentials: JwtAuthorizationCredentials = Security(access_security)):
    balance = await user_repository.get_balance(credentials)
    return {"balance": balance}

@user.get("/users_list")
async def get_users():
    users = await user_repository.get_users()
    return {"users": users}

@user.post("/refill_balance")
async def refill_balance(
        data: RefillBalanceSchema,
        credentials: JwtAuthorizationCredentials = Security(access_security)
):
    await user_repository.change_balance(credentials, data.bet)
    user_balance = await user_repository.get_balance(credentials)
    return {
        "balance refill": f"+{data.bet}",
        "your balance": user_balance,
    }

@user.post("/update_username", status_code=200)
async def update_username(
        credentials: JwtAuthorizationCredentials = Security(access_security),
        username: str = None
):
    try:
        await user_repository.update_username(credentials, username)
        return {"message": "username updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@user.delete("/delete_account", status_code=204)
async def delete_user(credentials: JwtAuthorizationCredentials = Security(access_security)):
    try:
        await user_repository.delete_user(credentials)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
