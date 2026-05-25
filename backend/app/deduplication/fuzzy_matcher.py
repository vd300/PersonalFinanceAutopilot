from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover
    fuzz = None


def similarity(left: str | None, right: str | None) -> int:
    if not left or not right:
        return 0
    if fuzz:
        return int(fuzz.token_sort_ratio(left, right))
    return int(SequenceMatcher(None, left.lower(), right.lower()).ratio() * 100)

