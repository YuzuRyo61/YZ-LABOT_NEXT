from .config import (
    ConfigCog,
    CONFIG_WELCOME_MESSAGE_ID,
    CONFIG_WELCOME_CHANNEL_ID,
    CONFIG_GENERAL_ROLE_ID,
    CONFIG_MEMBER_NOTIFY_ID,
    CONFIG_ROLE_TABLE,
    CONFIG_SELF_ROLE_CHANNEL_ID,
)
from .welcome import WelcomeCog
from .self_role import SelfRoleCog


__all__ = [
    "ConfigCog",
    "WelcomeCog",
    "SelfRoleCog",
    "CONFIG_WELCOME_MESSAGE_ID",
    "CONFIG_WELCOME_CHANNEL_ID",
    "CONFIG_GENERAL_ROLE_ID",
    "CONFIG_MEMBER_NOTIFY_ID",
    "CONFIG_ROLE_TABLE",
    "CONFIG_SELF_ROLE_CHANNEL_ID",
]
