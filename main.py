import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables, delete_tables
from app.store.user_admin_repository import create_admin
from app.views.auth_router import router
from app.views.router import game
from app.views.user_router import user
from app.google_auth.google_auth import google_app
from app.stripe.stripe_config import stripe_router
from app.db.models import UserAdmin
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = create_admin(app, secret_key=SECRET_KEY)
admin.add_view(UserAdmin)

app.include_router(router)
app.include_router(user)
app.include_router(game)
app.include_router(google_app)
app.include_router(stripe_router)
