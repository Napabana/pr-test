import pytest

from label_utils import normalize_label


def test_normalize_label_basic():
    assert normalize_label("Agent Runtime") == "agent-runtime"


def test_normalize_label_trims_outer_whitespace():
    assert normalize_label("  Agent Runtime  ") == "agent-runtime"


def test_normalize_label_collapses_repeated_whitespace():
    assert normalize_label("Agent   Runtime") == "agent-runtime"


def test_normalize_label_empty_raises():
    with pytest.raises(ValueError, match="label must not be empty"):
        normalize_label("   ")
