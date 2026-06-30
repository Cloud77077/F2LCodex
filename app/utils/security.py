import hashlib, hmac, secrets
from app.config import get_settings

def generate_token(nbytes: int | None = None) -> str:
    settings = get_settings()
    return secrets.token_urlsafe(nbytes or settings.token_bytes)

def token_hash(token: str) -> str:
    key = get_settings().secret_key.encode()
    return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()

def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
