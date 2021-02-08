#!/usr/bin/env python3
"""
YZ-LABOT_NEXT
Discord guild administrative support bot for YZ-LABO
"""

import os
import logging

from dotenv import load_dotenv

from yzlabot import YB_BOT
from yzlabot.cogs import *

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("=== YZ-LABOT ===")
    logging.info("Loading .env file")
    load_dotenv()
    feature_cogs = (
        ConfigCog(),
        WelcomeCog(),
        SelfRoleCog(YB_BOT),
        InviteBlockerCog(),
        VoiceRoomCog()
    )
    for cog in feature_cogs:
        YB_BOT.add_cog(cog)
        logging.info(f"Cog module added: {cog.__class__.__name__}")

    # Running bot
    if os.environ.get("DISCORD_TOKEN") is not None:
        logging.info("Starting YZ-LABOT")
        YB_BOT.run(os.environ.get("DISCORD_TOKEN"))
    else:
        logging.fatal("DISCORD_TOKEN value is required")
