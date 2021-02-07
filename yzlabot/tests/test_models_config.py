import pytest
from pydantic.error_wrappers import ValidationError

from yzlabot.models import Config


def test_config_validate_error():
    # no enough values
    with pytest.raises(ValidationError):
        Config(config_id="test")
    # no extra value
    with pytest.raises(ValidationError):
        Config(config_id="test", value="test", extra_value="test")
    # do not insert not permitted type
    with pytest.raises(ValidationError):
        Config(config_id="test", value=["test", bytes])


def test_config_valid_single():
    # valid configuration with single str
    cfg = Config(config_id="test", value="valid")
    assert type(cfg.value) == str and cfg.value == "valid"
    # valid configuration with single int
    cfg = Config(config_id="test", value=123)
    assert type(cfg.value) == str and cfg.value == str(123)


def test_config_valid_multiple():
    # valid configuration with multiple str
    cfg = Config(config_id="test", value=["valid", "value"])
    assert type(cfg.value) == list
    for v in cfg.value:
        assert type(v) == str
    # valid configuration with single int
    cfg = Config(config_id="test", value=[123, 456])
    assert type(cfg.value) == list
    for v in cfg.value:
        assert type(v) == str
