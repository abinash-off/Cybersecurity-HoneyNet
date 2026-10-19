from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_token, get_current_user, verify_password
from app.config import get_settings
from app.schemas import LoginIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
_hashed = None


def admin_hash() -> str:
    global _hashed
    if _hashed is None:
        from app.auth import hash_password

        _hashed = hash_password(get_settings().admin_password)
    return _hashed


@router.post("/login", response_model=TokenOut)
def login_form(form: OAuth2PasswordRequestForm = Depends()):
    return _issue(form.username, form.password)


@router.post("/login/json", response_model=TokenOut)
def login_json(body: LoginIn):
    return _issue(body.username, body.password)


def _issue(username: str, password: str) -> TokenOut:
    settings = get_settings()
    if username != settings.admin_username or not verify_password(password, admin_hash()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_token(username))


@router.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"username": user}


@router.post("/logout")
def logout(user: str = Depends(get_current_user)):
    return {"ok": True, "user": user, "note": "JWT is stateless; discard the token client-side."}
