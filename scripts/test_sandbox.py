from mini_dgm.tasks import load_katas
from mini_dgm.sandbox import run_tests

kata = {k.id: k for k in load_katas()}["rle_encode"]

GOOD = '''
def encode(s):
    if not s:
        return ""
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    return "".join(out)
'''

HARDCODED = '''
def encode(s):
    return "a3b2c1"     # memorizes one public case; generalizes to nothing
'''

INFINITE = '''
def encode(s):
    while True:
        pass
'''

print("GOOD vs HIDDEN tests:")
r = run_tests(GOOD, kata.hidden_tests, timeout_s=kata.timeout_s)
print(f"  status={r.status}  score={r.passed}/{r.total} ({r.score:.0%})  {r.duration_s:.1f}s")

print("HARDCODED vs HIDDEN tests:")
r = run_tests(HARDCODED, kata.hidden_tests, timeout_s=kata.timeout_s)
print(f"  status={r.status}  score={r.passed}/{r.total} ({r.score:.0%})")
for f in r.failures:
    print("    fail:", f.name, "-", f.message[:60])

print("INFINITE vs PUBLIC tests (expect timeout):")
r = run_tests(INFINITE, kata.public_tests, timeout_s=3)
print(f"  status={r.status}  score={r.passed}/{r.total}  {r.duration_s:.1f}s")

"""
    > Output of running "python scripts\test_sandbox.py":

        GOOD vs HIDDEN tests:
        ..\AppData\Local\Temp\minidgm_vjcbxvm5
        status=completed  score=5/5 (100%)  4.3s
        
        HARDCODED vs HIDDEN tests:
        ..\AppData\Local\Temp\minidgm_vweviqob
        status=completed  score=0/5 (0%)
            fail: test_empty - AssertionError: assert 'a3b2c1' == ''
        
        + a3b2c1
            fail: test_one_char - AssertionError: assert 'a3b2c1' == 'a1'
        
        - a1
        + a3b2c1
            fail: test_all_same - AssertionError: assert 'a3b2c1' == 'z5'
        
        - z5
        + a3b2c1
            fail: test_long_run_double_digits - AssertionError: assert 'a3b2c1' == 'a12'
        
        - a12
        + a3b2
            fail: test_mixed - AssertionError: assert 'a3b2c1' == 'a2b3c4'
        
        - a2b3c4
        
        INFINITE vs PUBLIC tests (expect timeout):
        ..\AppData\Local\Temp\minidgm_shhz49bf
        status=timeout  score=0/0  18.6s
"""
