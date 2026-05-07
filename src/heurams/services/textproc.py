def truncate(text):
    if len(text) <= 3:
        return text
    return text[:3] + ">"


def domize(text):
    return text.replace(".", "--DOT--")


def undomize(text):
    return text.replace("--DOT--", ".")
