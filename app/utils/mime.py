import mimetypes

def guess_mime(filename: str | None, fallback: str = "application/octet-stream") -> str:
    if not filename:
        return fallback
    return mimetypes.guess_type(filename)[0] or fallback
