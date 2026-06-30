import pytest
from app.utils.ranges import parse_range_header, content_range

def test_open_range():
    r = parse_range_header("bytes=5-", 10)
    assert (r.start, r.end, r.length) == (5, 9, 5)

def test_closed_range_clamped():
    r = parse_range_header("bytes=0-999", 100)
    assert content_range(r, 100) == "bytes 0-99/100"

def test_suffix_range():
    r = parse_range_header("bytes=-4", 10)
    assert (r.start, r.end) == (6, 9)

def test_unsatisfiable():
    with pytest.raises(IndexError): parse_range_header("bytes=10-20", 10)

def test_multi_range_rejected():
    with pytest.raises(ValueError): parse_range_header("bytes=0-1,3-4", 10)
