from solution import encode

def test_basic():
    assert encode("aaabbc") == "a3b2c1"

def test_single_runs():
    assert encode("abc") == "a1b1c1"

