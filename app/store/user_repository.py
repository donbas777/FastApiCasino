import os
from fastapi import Depends, HTTPException, status, Security
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from sqlalchemy import select, delete
from passlib.context import CryptContext

from app.tasks import send_welcome_email
from app.db.database import new_session
from app.db.models import User
from app.games.games import play_rollet, play_slots, play_roll_dice
from app.schemas.schemas import (
    PlayRolletColorSchema,
    PlayRolletNumberSchema,
    PlaySlotsSchema,
    PlayRollDiceSchema
)
from app.schemas.user_schemas import UserCreateSchema
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

access_security = JwtAccessBearer(secret_key=SECRET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    async def login_user(self, username: str, password: str):
        async with new_session() as session:
            result = await session.execute(select(User).filter(User.username == username))
            user = result.scalar_one_or_none()

            if user and pwd_context.verify(password, user.password):
                return access_security.create_access_token(subject={"id": str(user.id)})
            else:
                raise HTTPException(status_code=401, detail="Invalid username or password")

    async def get_current_user(
            self,
            credentials: JwtAuthorizationCredentials = Security(access_security)
    ) -> User:
        async with new_session() as session:
            result = await session.execute(select(User).filter(User.id == credentials.subject))
            return result.scalar_one_or_none()

    async def get_users(self):
        async with new_session() as session:
            result = await session.execute(select(User).order_by(User.id.desc()))
            return result.scalars().all()

    async def login_required(self, user: User = Depends(get_current_user)) -> User:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def registration(self, data: UserCreateSchema) -> User:
        async with new_session() as session:
            user_dict = data.model_dump()
            user_dict["password"] = pwd_context.hash(user_dict["password"])
            user = User(**user_dict)
            session.add(user)
            await session.flush()
            await session.commit()
            send_welcome_email.delay(user.email)
            return user

    async def get_balance(
            self,
            credentials: JwtAuthorizationCredentials = Security(access_security)
    ):
        async with new_session() as session:
            user_id = credentials.subject.get("id")
            result = await session.execute(select(User.balance).filter(User.id == user_id))
            balance = result.scalar_one_or_none()
            return balance

    async def change_balance(
            self, credentials: JwtAuthorizationCredentials = Security(access_security),
            amount: float = 0
    ):
        async with new_session() as session:
            try:
                user_id = credentials.subject.get("id")
                result = await session.execute(select(User).filter(User.id == user_id))
                user = result.scalar_one_or_none()

                if user is None:
                    return None
                user.balance += amount
                await session.commit()
                await session.refresh(user)
                return user
            except Exception as e:
                await session.rollback()
                raise e

    async def delete_user(self, credentials: JwtAuthorizationCredentials = Security(access_security)):
        async with new_session() as session:
            try:
                user_id = credentials.subject.get("id")
                await session.execute(delete(User).filter(User.id == user_id))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def update_username(
            self,
            credentials: JwtAuthorizationCredentials = Security(access_security),
            new_username: str = None
    ):
        async with new_session() as session:
            try:
                user_id = credentials.subject.get("id")
                result = await session.execute(select(User).filter(User.id == user_id))
                user = result.scalar_one_or_none()
                user.username = new_username
                await session.commit()
                await session.refresh(user)
                return user
            except Exception as e:
                await session.rollback()
                raise e

    async def play_rollet_by_colour(
            self,
            data: PlayRolletColorSchema,
            credentials: JwtAuthorizationCredentials = Security(access_security)
    ):
        async with new_session() as session:
            user_balance = await self.get_balance(credentials)
            if user_balance < data.bet:
                return {
                    "message": "ПОПОВНИ БАЛАНС СУКА!"
                }
            result = play_rollet()
            if result[1] == data.color and result[1] == "green":
                win = data.bet * 35
                await self.change_balance(credentials, win)
                return {
                    "result": f"{result[0], result[1]}",
                    "message": f"You win {data.bet * 36}"
                }
            elif result[1] == data.color:
                win = data.bet
                await self.change_balance(credentials, win)
                return {
                    "result": f"{result[0], result[1]}",
                    "message": f"You win {data.bet * 2}"
                }
            else:
                lose = -data.bet
                await self.change_balance(credentials, lose)
                return {
                    "result": f"{result[0], result[1]}",
                    "message": f"You lose {data.bet}"
                }

    async def play_rollet_by_number(
            self,
            data: PlayRolletNumberSchema,
            credentials: JwtAuthorizationCredentials = Security(access_security)
    ):
        async with new_session() as session:

            user_balance = await self.get_balance(credentials)
            if user_balance < data.bet:
                return {
                    "message": "ПОПОВНИ БАЛАНС СУКА!"
                }

            result = play_rollet()
            if result[0] == data.number:
                win = data.bet * 35
                await self.change_balance(credentials, win)
                return {
                    "result": f"{result[0], result[1]}",
                    "message": f"You win {data.bet * 36}"
                }
            else:
                lose = -data.bet
                await self.change_balance(credentials, lose)
                return {
                    "result": f"{result[0], result[1]}",
                    "message": f"You lose {data.bet}"
                }

    async def play_slots(
            self, data: PlaySlotsSchema,
            credentials: JwtAuthorizationCredentials = Security(access_security)
    ):
        async with new_session() as session:

            user_balance = await self.get_balance(credentials)
            if user_balance < data.bet:
                return {
                    "message": "ПОПОВНИ БАЛАНС СУКА!"
                }

            message = "You lose!"
            result = play_slots()

            if result[1][0] == result[1][1] and result[1][1] == result[1][2]:
                win = data.bet * 6
                await self.change_balance(credentials, win)
                message = f"Congratulations, you win {win}"
            elif result[0][0] == result[1][1] and result[2][2] == result[1][1]:
                win = data.bet * 6
                await self.change_balance(credentials, win)
                message = f"Congratulations, you win {win} diagonal"
            elif result[0][2] == result[1][1] and result[2][0] == result[1][1]:
                win = data.bet * 6
                await self.change_balance(credentials, win)
                message = f"Congratulations, you win {win} diagonal"
            else:
                lose = -data.bet
                await self.change_balance(credentials, lose)
            return {
                "_": f"{result[0][0]} | {result[0][1]} | {result[0][2]}",
                ".": f"{result[1][0]} | {result[1][1]} | {result[1][2]}",
                "-": f"{result[2][0]} | {result[2][1]} | {result[2][2]}",
                "message": f"{message}"
            }

    async def play_roll_dice(
            self, data: PlayRollDiceSchema,
            credentials: JwtAuthorizationCredentials = Security(access_security)
    ):
        async with new_session() as session:
            user_balance = await self.get_balance(credentials)
            if user_balance < data.bet:
                return {
                    "message": "ПОПОВНИ БАЛАНС СУКА!"
                }
            result = play_roll_dice()
            sum = result[0] + result[1]
            if (data.greater_then_7 is True and sum > 7) or (data.greater_then_7 is False and sum < 7):
                win = data.bet * 2
                await self.change_balance(credentials, win)
                return {
                    "result": f"{result[0]}  |  {result[1]}",
                    "message": "You win"
                }
            else:
                lose = -data.bet
                await self.change_balance(credentials, lose)
                return {
                    "result": f"{result[0]}  |  {result[1]}",
                    "message": "You lose"
                }
