# Turns a returned generator into a list
def as_list(func):
    def inner(*args, **kwargs):
        return list(func(*args, **kwargs))
    return inner

def as_tuple(func):
    def inner(*args, **kwargs):
        return tuple(func(*args, **kwargs))
    return inner

def as_dict(func):
    def inner(*args, **kwargs):
        return dict(func(*args, **kwargs))
    return inner