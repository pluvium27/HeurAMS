def truncate(text):
    if len(text) <= 3:
        return text
    return text[:3] + ">"
