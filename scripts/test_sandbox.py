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