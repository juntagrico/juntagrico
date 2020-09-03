def chainable(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return args[0]
    return wrapper
