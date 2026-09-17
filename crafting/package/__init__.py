import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.crafting")

async def setup(bot: "BallsDexBot"):
    log.info("Loading Crafting package...")
    from .cog import Craft
    await bot.add_cog(Craft(bot))
    log.info("Crafting package loaded successfully!")
