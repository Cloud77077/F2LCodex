from dataclasses import dataclass

@dataclass(frozen=True)
class ByteRange:
    start: int
    end: int
    @property
    def length(self) -> int:
        return self.end - self.start + 1

def parse_range_header(header: str | None, size: int) -> ByteRange | None:
    if not header:
        return None
    if size < 0 or not header.startswith("bytes=") or "," in header:
        raise ValueError("invalid range")
    spec = header[6:].strip()
    if "-" not in spec:
        raise ValueError("invalid range")
    first, last = spec.split("-", 1)
    if first == "":
        if not last.isdigit():
            raise ValueError("invalid suffix range")
        suffix = int(last)
        if suffix <= 0:
            raise ValueError("invalid suffix range")
        if size == 0:
            raise IndexError("unsatisfiable")
        start = max(size - suffix, 0)
        return ByteRange(start, size - 1)
    if not first.isdigit() or (last and not last.isdigit()):
        raise ValueError("invalid range")
    start = int(first)
    end = int(last) if last else size - 1
    if start >= size or start > end or size == 0:
        raise IndexError("unsatisfiable")
    return ByteRange(start, min(end, size - 1))

def content_range(byte_range: ByteRange, size: int) -> str:
    return f"bytes {byte_range.start}-{byte_range.end}/{size}"
