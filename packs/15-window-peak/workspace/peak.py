def peaks(values: list[int], width: int) -> list[int]:
    """Broken: returns the first item of each window, not the max."""
    if width <= 0 or len(values) < width:
        return []
    return [values[i] for i in range(len(values) - width + 1)]
