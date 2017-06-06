def splice(values, start, end):
    return values[start:end] if end != 0 else values[start:]
