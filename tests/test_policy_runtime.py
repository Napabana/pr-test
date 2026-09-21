from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.runtime import policy_mode


def test_policy_mode_is_configured_string():
    value = policy_mode()
    assert isinstance(value, str)
    assert value
