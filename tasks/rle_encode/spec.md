# Run-length encoding

Implement a function `encode(s: str) -> str` that performs run-length encoding.

Each maximal run of a repeated character is replaced by that character followed
by the length of the run, preserving order.

Examples:
    encode("aaabbc") -> "a3b2c1"
    encode("")       -> ""

Constraints:
- `s` contains only lowercase ASCII letters (a-z).
- Return a string; for empty input return an empty string.
