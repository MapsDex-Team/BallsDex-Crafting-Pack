import random
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from bd_models.models import BallInstance, Player, Special, TradeObject
from ballsdex.core.utils.transformers import (
    BallEnabledTransform,
    BallInstanceTransform,
    SpecialEnabledTransform,
)
from ballsdex.settings import settings

from .logic import queryset_to_list
from crafting.models import CraftingRecipe
from .session_manager import crafting_sessions

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

ELEMENTAL_INGREDIENT_SPECIAL_IDS = {
    "Fire": 19,
    "Earth": 22,
    "Water": 23,
    "Electric": 27,
}
ELEMENTAL_RESULT_SPECIAL_ID = 28

class Craft(commands.GroupCog, group_name="craft"):
    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.settings = settings

    @app_commands.command()
    async def begin(
        self,
        interaction: discord.Interaction,
        special: Optional[SpecialEnabledTransform] = None,
    ):
        """
        Start a crafting session.

        Parameters
        ----------
        special: Special | None
            The special event to lock this crafting session to.
        """
        await interaction.response.defer()

        user_id = interaction.user.id

        if user_id in crafting_sessions:
            await interaction.followup.send(
                "You already have an active crafting session. Please finish or cancel it before starting a new one.",
                ephemeral=True,
            )
            return

        player, _ = await Player.objects.aget_or_create(discord_id=user_id)

        crafting_sessions[user_id] = {
            "player": player,
            "ingredient_instances": [],
            "special": special,
            "started_at": discord.utils.utcnow(),
            "message": None,
        }

        await update_crafting_display(interaction, user_id, is_new=True)

    @app_commands.command()
    async def add(
        self,
        interaction: discord.Interaction,
        countryball: BallInstanceTransform,
    ):
        """
        Add a countryball to crafting session

        Parameters
        ----------
        countryball: BallInstance
            The countryball instance to add as an ingredient.
        """
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id

        countryball = await BallInstance.objects.select_related("ball", "special").aget(
            pk=countryball.pk
        )

        if await countryball.is_locked():
            return await interaction.followup.send(
                "❌ This countryball is currently reserved in a trade and can't be used for crafting.",
                ephemeral=True,
            )

        if user_id not in crafting_sessions:
            return await interaction.followup.send(
                "❌ Start a crafting session first with `/craft begin`.", ephemeral=True
            )

        session = crafting_sessions[user_id]
        player = session["player"]

        if countryball.player_id != player.pk:
            return await interaction.followup.send(
                "❌ You don't own this countryball!", ephemeral=True
            )

        if session["special"] and countryball.special_id != session["special"].pk:
            return await interaction.followup.send(
                f"❌ This ball isn't the right special ({session['special'].name})!",
                ephemeral=True,
            )

        if not session["special"] and countryball.special_id is not None:
            return await interaction.followup.send(
                "❌ No specials allowed in this session!", ephemeral=True
            )

        if countryball.pk in session["ingredient_instances"]:
            return await interaction.followup.send(
                f"❌ Already added #{countryball.pk:0X}!", ephemeral=True
            )

        session["ingredient_instances"].append(countryball.pk)

        await interaction.followup.send(
            f"Added {countryball.ball.country} #{countryball.pk:0X} to crafting session!",
            ephemeral=True,
        )

        await update_crafting_display(interaction, user_id)

    @app_commands.command()
    async def remove(
        self,
        interaction: discord.Interaction,
        countryball: BallInstanceTransform,
    ):
        """
        Remove a countryball from your active crafting session.

        Parameters
        ----------
        countryball: BallInstance
            The countryball instance to remove from the ingredients.
        """
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        countryball = await BallInstance.objects.select_related("ball", "special").aget(
            pk=countryball.pk
        )

        if user_id not in crafting_sessions:
            return await interaction.followup.send(
                "❌ No active crafting session!", ephemeral=True
            )

        session = crafting_sessions[user_id]
        if countryball.pk not in session["ingredient_instances"]:
            return await interaction.followup.send(
                f"❌ Instance #{countryball.pk:0X} not in your session!", ephemeral=True
            )

        session["ingredient_instances"].remove(countryball.pk)

        await interaction.followup.send(
            f"Removed {countryball.ball.country} #{countryball.pk:0X} from crafting session!",
            ephemeral=True,
        )

        await update_crafting_display(interaction, user_id)

    @app_commands.command()
    async def clear(
        self,
        interaction: discord.Interaction,
    ):
        """
        Clear all added ingredients from crafting session.
        """
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id

        if user_id not in crafting_sessions:
            return await interaction.followup.send(
                "❌ No active crafting session!", ephemeral=True
            )

        crafting_sessions[user_id]["ingredient_instances"] = []
        await update_crafting_display(interaction, user_id)
        await interaction.followup.send(
            "Cleared all ingredients from your crafting session.", ephemeral=True
        )

    @app_commands.command()
    async def recipes(
        self,
        interaction: discord.Interaction,
        countryball: Optional[BallEnabledTransform] = None,
    ):
        """
        Show active crafting recipes.

        Parameters
        ----------
        countryball: Ball | None
            The crafted result to show recipes for.
        """
        ball = countryball

        queryset = CraftingRecipe.objects.select_related("result").prefetch_related(
            "ingredients__ingredient",
            "ingredient_groups__options__ball",
        )
        if ball:
            recipes = await queryset_to_list(queryset.filter(result=ball))
            title = f"🔨 Recipes for {ball.country}"
        else:
            recipes = await queryset_to_list(queryset.all()[:10])
            title = "🔨 Available Recipes (Top 10)"

        if not recipes:
            return await interaction.response.send_message(
                "❌ No recipes found.", ephemeral=True
            )

        embed = discord.Embed(title=title, color=0x0099FF)

        for recipe in recipes:
            desc = []
            ingredients = await queryset_to_list(
                recipe.ingredients.select_related("ingredient").all()
            )
            groups = await queryset_to_list(recipe.ingredient_groups.all())

            for ing in ingredients:
                if not ing.ingredient:
                    continue
                emoji = interaction.client.get_emoji(ing.ingredient.emoji_id)
                desc.append(f"{emoji} {ing.ingredient.country} x{ing.quantity}")

            for group in groups:
                options = await queryset_to_list(group.options.select_related("ball").all()[:5])
                option_text = [
                    f"{interaction.client.get_emoji(option.ball.emoji_id)} {option.ball.country}"
                    for option in options
                ]
                desc.append(
                    f"**{group.name}** (choose {group.required_count}): {' | '.join(option_text)}"
                )

            result_emoji = interaction.client.get_emoji(recipe.result.emoji_id)
            embed.add_field(
                name=f"{result_emoji} {recipe.result.country}",
                value="\n".join(desc) or "*No ingredients configured*",
                inline=False,
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def elemental(
        self,
        interaction: discord.Interaction,
        countryball: BallEnabledTransform,
    ):
        """
        Craft an Elemental special from Fire, Earth, Water, and Electric specials.

        Parameters
        ----------
        countryball: Ball
            The ball to craft into an Elemental special.
        """
        await interaction.response.defer()

        player, _ = await Player.objects.aget_or_create(discord_id=interaction.user.id)
        configured_ids = [
            *ELEMENTAL_INGREDIENT_SPECIAL_IDS.values(),
            ELEMENTAL_RESULT_SPECIAL_ID,
        ]
        if any(special_id <= 0 for special_id in configured_ids):
            return await interaction.followup.send(
                "❌ Elemental crafting is currently disabled.",
                ephemeral=True,
            )
        if len(set(configured_ids)) != len(configured_ids):
            return await interaction.followup.send(
                "❌ Elemental crafting special IDs must all be different.",
                ephemeral=True,
            )

        try:
            elemental_special = await Special.objects.aget(pk=ELEMENTAL_RESULT_SPECIAL_ID)
        except Special.DoesNotExist:
            return await interaction.followup.send(
                "❌ The configured Elemental special ID does not exist.",
                ephemeral=True,
            )

        required_special_ids = set(ELEMENTAL_INGREDIENT_SPECIAL_IDS.values())
        candidates = await queryset_to_list(
            BallInstance.objects.select_related("ball", "special")
            .filter(
                player=player,
                ball=countryball,
                special_id__in=required_special_ids,
                favorite=False,
            )
            .order_by("pk")
        )

        candidates.sort(key=lambda candidate: (candidate.attack_bonus + candidate.health_bonus, candidate.pk))
        ingredients_by_special = {}
        for candidate in candidates:
            if candidate.special_id in ingredients_by_special:
                continue
            if await candidate.is_locked(refresh=False):
                continue
            ingredients_by_special[candidate.special_id] = candidate

        missing_specials = [
            name
            for name, special_id in ELEMENTAL_INGREDIENT_SPECIAL_IDS.items()
            if special_id not in ingredients_by_special
        ]
        if missing_specials:
            missing = ", ".join(missing_specials)
            return await interaction.followup.send(
                f"❌ You need one non-favorited, unlocked **{countryball.country}** for each element. Missing: {missing}.",
                ephemeral=True,
            )

        ingredients_to_delete = [
            ingredients_by_special[special_id]
            for special_id in ELEMENTAL_INGREDIENT_SPECIAL_IDS.values()
        ]
        ingredient_ids = [ingredient.pk for ingredient in ingredients_to_delete]

        try:
            await TradeObject.objects.filter(ballinstance_id__in=ingredient_ids).adelete()

            found_count = await BallInstance.objects.filter(pk__in=ingredient_ids).acount()
            if found_count != len(ingredient_ids):
                return await interaction.followup.send(
                    "❌ Not all ingredients could be found. Nothing was crafted.",
                    ephemeral=True,
                )

            await BallInstance.objects.filter(pk__in=ingredient_ids).adelete()

            crafted_instance = await BallInstance.objects.acreate(
                player=player,
                ball=countryball,
                special_id=ELEMENTAL_RESULT_SPECIAL_ID,
                health_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
                attack_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
            )
        except Exception as e:
            print(f"Unexpected error in craft_elemental: {e}")
            return await interaction.followup.send(
                "❌ An unexpected error occurred while crafting Elemental. Please try again.",
                ephemeral=True,
            )

        ball_emoji = interaction.client.get_emoji(countryball.emoji_id)
        special_prefix = f"{elemental_special.emoji} " if elemental_special.emoji else ""
        ingredient_summary = []
        for ingredient in ingredients_to_delete:
            ingredient_emoji = interaction.client.get_emoji(ingredient.ball.emoji_id)
            special_text = f"{ingredient.special.emoji} " if ingredient.special.emoji else ""
            ingredient_summary.append(
                f"{ingredient_emoji} {special_text}{ingredient.special.name} {ingredient.ball.country} (#{ingredient.pk:0X})"
            )

        embed = discord.Embed(
            title="✅ Elemental Crafting Successful!",
            description=(
                f"Successfully crafted **{special_prefix}{elemental_special.name} "
                f"{ball_emoji} {countryball.country}** (ID: #{crafted_instance.pk:0X})!"
            ),
            color=0x00FF00,
        )
        embed.add_field(
            name="New instance Stats",
            value=f"**ATK:** {crafted_instance.attack_bonus:+d} | **HP:** {crafted_instance.health_bonus:+d}",
            inline=False,
        )
        embed.add_field(
            name="Ingredients Used",
            value="\n".join(ingredient_summary),
            inline=False,
        )

        await interaction.followup.send(embed=embed)


async def update_crafting_display(interaction, user_id, is_new=False):
    from .crafting_utils import update_crafting_display as _update

    await _update(interaction, user_id, is_new)