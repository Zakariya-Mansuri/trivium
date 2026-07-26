from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from app.api.deps import get_current_user
from app.db.base import utcnow
from app.db.session import get_db
from app.models import RefreshToken, User
from app.schemas.auth import (
    LLMConfigIn,
    LLMConfigOut,
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserOut,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(db: DBSession, user: User) -> TokenResponse:
    refresh_raw = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_raw),
            expires_at=refresh_token_expiry(),
        )
    )
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=refresh_raw,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def signup(request: Request, body: SignupRequest, db: DBSession = Depends(get_db)):
    email = body.email.lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(email=email, display_name=body.display_name, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    return _issue_tokens(db, user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def login(request: Request, body: LoginRequest, db: DBSession = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    # Same error for unknown email and wrong password — no account enumeration.
    if user is None or user.deleted_at is not None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def refresh(request: Request, body: RefreshRequest, db: DBSession = Depends(get_db)):
    record = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(body.refresh_token))
    )
    if record is None or record.revoked or record.expires_at < utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.get(User, record.user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    # Rotation: each refresh token is single-use.
    record.revoked = True
    db.commit()
    return _issue_tokens(db, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: RefreshRequest, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(body.refresh_token),
            RefreshToken.user_id == user.id,
        )
    )
    if record is not None:
        record.revoked = True
        db.commit()


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(body: UserUpdate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.learning_intensity is not None:
        user.learning_intensity = body.learning_intensity
    if body.notification_prefs is not None:
        user.notification_prefs = body.notification_prefs
    db.commit()
    db.refresh(user)
    return user


# --- Attached LLM provider (BYOK, OpenCode-style) ---


def _llm_config_out(user: User) -> LLMConfigOut:
    from app.core.config import settings as app_settings
    from app.core.crypto import decrypt_secret
    from app.llm.registry import PROVIDERS

    if user.llm_provider and user.llm_api_key_enc:
        key = decrypt_secret(user.llm_api_key_enc)
        spec = PROVIDERS.get(user.llm_provider, {})
        return LLMConfigOut(
            provider=user.llm_provider,
            model=user.llm_model or spec.get("default_model"),
            key_hint=f"••••{key[-4:]}" if key else None,
            source="user",
            active_label=f"Your {spec.get('label', user.llm_provider)} key",
        )
    env_provider = app_settings.LLM_PROVIDER.lower()
    has_env = env_provider in PROVIDERS and bool(app_settings.LLM_API_KEY)
    return LLMConfigOut(
        provider=None,
        model=None,
        key_hint=None,
        source="server_default",
        active_label=f"Server default ({PROVIDERS[env_provider]['label']})" if has_env else "Offline mock (no key configured)",
    )


@router.get("/me/llm", response_model=LLMConfigOut)
def get_llm_config(user: User = Depends(get_current_user)):
    return _llm_config_out(user)


@router.get("/me/llm/providers")
def list_llm_providers(user: User = Depends(get_current_user)):
    from app.llm.registry import public_catalog

    return {"providers": public_catalog()}


@router.put("/me/llm", response_model=LLMConfigOut)
def set_llm_config(body: LLMConfigIn, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    from app.core.crypto import encrypt_secret
    from app.llm.registry import PROVIDERS

    if body.provider not in PROVIDERS:
        raise HTTPException(status_code=422, detail=f"Unknown provider. Supported: {', '.join(PROVIDERS)}")
    user.llm_provider = body.provider
    user.llm_model = body.model or None
    user.llm_api_key_enc = encrypt_secret(body.api_key)
    db.commit()
    db.refresh(user)
    return _llm_config_out(user)


@router.delete("/me/llm", response_model=LLMConfigOut)
def clear_llm_config(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    user.llm_provider = None
    user.llm_model = None
    user.llm_api_key_enc = None
    db.commit()
    db.refresh(user)
    return _llm_config_out(user)


@router.post("/me/llm/test")
@limiter.limit(settings.RATE_LIMIT_LLM)
def test_llm_config(request: Request, user: User = Depends(get_current_user)):
    """Sends a one-word completion through the user's attached provider."""
    from app.llm import get_llm
    from app.llm.base import LLMError
    from app.llm.mock import MockProvider

    provider = get_llm(user)
    if isinstance(provider, MockProvider):
        return {"ok": True, "provider": "mock", "note": "No real provider attached — using the offline mock."}
    try:
        reply = provider.complete(
            [{"role": "user", "content": "Reply with exactly one word: WORKING"}], max_tokens=200
        )
        return {"ok": True, "provider": provider.name, "model": provider.model, "reply": reply[:80]}
    except LLMError as exc:
        return {"ok": False, "provider": provider.name, "error": str(exc)[:300]}


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def change_password(
    request: Request,
    body: PasswordChangeRequest,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Current password is incorrect")
    user.hashed_password = hash_password(body.new_password)
    # Revoke all refresh tokens on password change.
    for token in db.scalars(select(RefreshToken).where(RefreshToken.user_id == user.id, RefreshToken.revoked == False)):  # noqa: E712
        token.revoked = True
    db.commit()
