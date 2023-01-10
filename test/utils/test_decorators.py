from typing import Callable, Any, Dict

import pytest

from src.utils.decorators import run_once


@run_once
def wrapped_function_a(arg_a: int, arg_b: int, arg_c: int) -> int:
    return arg_a * arg_b * arg_c


@run_once
def wrapped_function_b(arg_a: bool) -> bool:
    return arg_a


class SomeObject:

    some_var: int = 1

    @run_once
    def wrapped_method_c(self, arg_a: int, arg_b: int, arg_c: int) -> int:
        return (arg_a + arg_b + arg_c) * self.some_var

    @run_once
    def wrapped_static_method_d(self, arg_a: float, arg_b: float, arg_c: float) -> float:
        return (arg_a - arg_b - arg_c) * self.some_var


some_object = SomeObject()


class TestDecoratorsRunOnce:

    @pytest.mark.parametrize("wrapped, func_args, expected_result",
                             [
                                 (wrapped_function_a, [{"arg_a": 2, "arg_b": 3, "arg_c": 4}, {"arg_a": 5, "arg_b": 6, "arg_c": 7}], 24),
                                 (wrapped_function_b, [{"arg_a": False}, {"arg_a": True}, {"arg_a": False}, {"arg_a": True}], False),
                                 (some_object.wrapped_method_c, [{"arg_a": 2, "arg_b": 3, "arg_c": 4}, {"arg_a": 5, "arg_b": 6, "arg_c": 7}], 9),
                                 (some_object.wrapped_static_method_d, [{"arg_a": 2.1, "arg_b": 3.1, "arg_c": 4.1}, {"arg_a": 5, "arg_b": 6, "arg_c": 7}], -5.1),
                             ])
    def test_run_once(self, wrapped: Callable, func_args: Dict, expected_result: Any):
        for args in func_args:
            assert wrapped(**args) == expected_result
