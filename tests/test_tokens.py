from app.utils.security import generate_token

def test_token_is_urlsafe():
    token = generate_token(16)
    assert "/" not in token and "+" not in token
    assert len(token) >= 20
