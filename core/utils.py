try:
    from functools import lru_cache as origin_lru_cache
except ImportError:
    from fastcache import lru_cache as origin_lru_cache


cached_funcs = []


def lru_cache(*args, **kwargs):
    def wrap_func(func):
        func = origin_lru_cache(*args, **kwargs)(func)
        cached_funcs.append(func)
        return func
    return wrap_func


def parse_config(config):
    pass


def clear_caches():
    for func in cached_funcs:
        func.cache_clear()


try:
    from inspect import signature
except ImportError:
    from funcsigs import signature