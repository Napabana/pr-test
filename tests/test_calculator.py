import pytest

from calculator import add, subtract, multiply, divide


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-2, -3) == -5


def test_subtract_positive_numbers():
    assert subtract(5, 3) == 2


def test_subtract_negative_result():
    assert subtract(3, 5) == -2


def test_multiply_positive_numbers():
    assert multiply(4, 3) == 12


def test_multiply_negative_numbers():
    assert multiply(-4, 3) == -12


def test_multiply_by_zero():
    assert multiply(7, 0) == 0


def test_divide_exact():
    assert divide(10, 2) == 5


def test_divide_float_result():
    assert divide(7, 2) == 3.5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)