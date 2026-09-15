import pytest

from calculator import add, subtract, multiply, divide, clamp


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


def test_clamp_value_within_range():
    """值在区间内时原样返回。"""
    assert clamp(5, 0, 10) == 5


def test_clamp_value_below_lower():
    """值小于下限时返回下限。"""
    assert clamp(-3, 0, 10) == 0


def test_clamp_value_above_upper():
    """值大于上限时返回上限。"""
    assert clamp(42, 0, 10) == 10


def test_clamp_equal_bounds():
    """下限等于上限时，任何值都返回该边界值。"""
    assert clamp(7, 3, 3) == 3


def test_clamp_invalid_bounds_raises():
    """下限大于上限时抛出 ValueError。"""
    with pytest.raises(ValueError, match="lower must not exceed upper"):
        clamp(5, 10, 0)