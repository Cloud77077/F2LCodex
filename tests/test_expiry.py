from app.file_store import expiry_from_hours

def test_permanent_expiry():
    assert expiry_from_hours(0) is None

def test_temporary_expiry():
    assert expiry_from_hours(1) is not None
