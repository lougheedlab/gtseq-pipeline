__all__ = ["ascii_normalize"]


def ascii_normalize(s: str) -> str:
    return s.encode("ascii", "ignore").decode("utf-8")
