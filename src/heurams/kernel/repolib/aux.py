from ...utils.lict import Lict


def merge(x: Lict, y: Lict):
    return Lict(list(x.values()) + list(y.values()))
