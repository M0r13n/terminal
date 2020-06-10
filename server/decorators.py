import functools


def log_cache_status(logger):
    def wrapper(func):
        @functools.wraps(func)
        def wrap_func(*args, **kwargs):
            result = func(*args, **kwargs)
            info = func.cache_info()
            logger.info(f"Function {func.__name__}: {info}")
            return result

        return wrap_func

    return wrapper
