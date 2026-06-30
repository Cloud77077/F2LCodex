from app.utils.security import generate_token, token_hash, constant_time_equal

def test_token_unique_and_hash_not_plaintext():
    a, b = generate_token(), generate_token()
    assert a != b
    assert token_hash(a) != a
    assert token_hash(a) != token_hash(b)

def test_constant_time_equal():
    assert constant_time_equal("abc", "abc")
    assert not constant_time_equal("abc", "abd")
