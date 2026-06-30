from app.utils.human import human_bytes, human_ttl

def test_human_bytes():
    assert human_bytes(0) == "0 B"
    assert human_bytes(1024) == "1.0 KiB"

def test_human_ttl():
    assert human_ttl(0) == "permanent"
    assert human_ttl(48) == "2 days"
