from fastapi import APIRouter
from app.schemas.user_schemas import UserCreateSchema, UserLoginSchema
from app.store.user_repository import UserRepository
from app.google_auth.google_auth import config

router = APIRouter(prefix="", tags=["authorization"])

user_repository = UserRepository()


@router.post("/login")
async def login(
        user: UserLoginSchema
):
    token = await user_repository.login_user(user.username, user.password)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register")
async def register(
    user: UserCreateSchema
):
    user_id = await user_repository.registration(user)
    return user_id

@router.get('/login/google')
async def login():
    google_client_id = config("GOOGLE_CLIENT_ID")
    google_redirect_uri = f'http://localhost:8000/auth/callback'
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code&client_id={google_client_id}"
        f"&redirect_uri={google_redirect_uri}"
        f"&scope=openid%20profile%20email&access_type=offline&prompt=select_account"
    )
    return {"url": auth_url}
