def human_bytes(num: int) -> str:
    if num < 0:
        raise ValueError("bytes cannot be negative")
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(num)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024

def human_ttl(hours: int) -> str:
    if hours == 0:
        return "permanent"
    if hours < 24:
        return f"{hours} hour" + ("" if hours == 1 else "s")
    days = hours / 24
    return f"{days:g} day" + ("" if days == 1 else "s")
