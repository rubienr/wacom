from functools import wraps
from typing import Callable


def run_once(wrapped_func: Callable):
    """
    Decorator to
      - run a call-able once and
      - always yield the same result on subsequent calls.

    :param wrapped_func: the callable to wrap
    :return: the same result reference as calculated on the 1st call
    """

    @wraps(wrapped_func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.result = wrapped_func(*args, **kwargs)
            wrapper.has_run = True
        return wrapper.result

    wrapper.has_run = False
    return wrapper
