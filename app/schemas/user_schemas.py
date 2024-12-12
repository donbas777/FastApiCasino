from pydantic import BaseModel, EmailStr, field_validator



class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    balance: float

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")

        return password


class UserLoginSchema(BaseModel):
    username: str
    password: str
