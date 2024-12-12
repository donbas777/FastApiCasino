from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from fastapi import FastAPI

from app.db.database import engine

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == "admin" and password == "password":
            request.session.update({"token": "authenticated"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        return True

def create_admin(app: FastAPI, secret_key: str) -> Admin:
    authentication_backend = AdminAuth(secret_key=secret_key)
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    return admin
