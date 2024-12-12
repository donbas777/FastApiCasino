import os
from typing import Union
import requests

from fastapi import HTTPException, APIRouter
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.future import select
from app.db.database import new_session
from app.store.user_repository import pwd_context, access_security
from app.db.models import User
from dotenv import load_dotenv

load_dotenv()


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.environ.get("SECRET_KEY")
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
    "SECRET_KEY": SECRET_KEY,
}

config = Config(environ=config_data)
google_app = APIRouter(tags=["google_auth"])

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    redirect_uri='http://localhost:8000/auth/callback',
    client_kwargs={'scope': 'openid profile email'},
)

@google_app.get('/auth/callback')
async def auth(code: Union[str, None] = None):
    if not code:
        raise HTTPException(status_code=400, detail="Code not provided by Google")

    token_url = "https://oauth2.googleapis.com/token"
    google_client_id = config("GOOGLE_CLIENT_ID")
    google_client_secret = config("GOOGLE_CLIENT_SECRET")
    redirect_uri = 'http://localhost:8000/auth/callback'

    data = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=token_response.status_code,
            detail=f"Error fetching token: {token_response.text}",
        )

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found")

    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if user_info_response.status_code != 200:
        raise HTTPException(
            status_code=user_info_response.status_code,
            detail=f"Error fetching user info: {user_info_response.text}",
        )

    user_info = user_info_response.json()
    email = user_info.get("email")
    username = user_info.get("name", "Google User")
    password = pwd_context.hash(access_token)


    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    async with new_session() as session:
        result = await session.execute(select(User).filter(User.email == email))
        user = result.scalars().first()

        if not user:
            user = User(email=email, username=username, password=password, token=access_token)
            session.add(user)
        else:
            user.token = access_token
        await session.commit()
        await session.refresh(user)
    return_token = access_security.create_access_token(subject={"id": str(user.id)})

    return {"email": user.email, "access_token": return_token}
