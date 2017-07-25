from functools import wraps, lru_cache

import time

def retry_call(n):
    def single_retry(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            for i in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print("error in retry call {}".format(e))
                    time.sleep(i)
            raise Exception("all retry failed")
        return wrap_func
    return single_retry

