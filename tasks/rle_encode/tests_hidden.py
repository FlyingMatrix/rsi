from solution import encode

def test_empty():
    assert encode("") == ""

def test_one_char():
    assert encode("a") == "a1"

def test_all_same():
    assert encode("zzzzz") == "z5"

def test_long_run_double_digits():
    assert encode("a" * 12) == "a12"      # counts can exceed 9

def test_mixed():
    assert encode("aabbbcccc") == "a2b3c4"

