import numpy as np
import traceback
import time
import json

from functools import wraps


STYLE = {
    'fore': {
        'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
        'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37,
    },
    'back': {
        'black': 40, 'red': 41, 'green': 42, 'yellow': 43,
        'blue': 44, 'purple': 45, 'cyan': 46, 'white': 47,
    },

    'mode': {
        'bold': 1, 'underline': 4, 'blink': 5, 'invert': 7
    },
    'default': {

        'end': 0
    }
}


def retry_call(n):
    def single_retry(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            for i in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print("[error retry] {} {}".format(e, traceback.format_exc()))
                    time.sleep(n)
            raise Exception('[retry giveup]')
        return wrap_func
    return single_retry


def fail_silent(func):
    @wraps(func)
    def wrap_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("[error giveup] {} {} ".format(e, traceback.format_exc()))
    return wrap_func


def fail_default(default_return):
    def single_retry(func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print("[error return default] {} {}".format(e, traceback.format_exc()))
                return default_return
        return wrap_func
    return single_retry


def pretty_macd_list(origin_list):
    if np.isnan(origin_list[0]):
        return origin_list
    else:
        p = int(-np.log10(abs(origin_list[0])))
        return [str(round(i * 10**(p), 2)) for i in origin_list]


def use_style(string, mode='', fore='', back=''):
    mode = '%s' % STYLE['mode'][mode] if mode in STYLE['mode'] else ''
    fore = '%s' % STYLE['fore'][fore] if fore in STYLE['fore'] else ''
    back = '%s' % STYLE['back'][back] if back in STYLE['back'] else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end = '\033[%sm' % STYLE['default']['end'] if style else ''
    return '%s%s%s' % (style, string, end)


red = lambda x: use_style(x, fore='red')
yellow = lambda x: use_style(x, fore='yellow')
green = lambda x: use_style(x, fore='green')


def load_api_key(exchange_name):
    with open("secrets.json") as secrets_file:
        secrets = json.load(secrets_file)
        secrets_file.close()
        apikey, secretkey = secrets[exchange_name]['api_key'], secrets[exchange_name]['secret_key']
        return apikey, secretkey