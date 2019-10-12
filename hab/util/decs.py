from .proc import Process

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

def as_proc(**_kwargs):
    def outer(func):
        def inner(*args, **kwargs):
            return Process(func(*args, **kwargs), **_kwargs)
        return inner
    return outer
