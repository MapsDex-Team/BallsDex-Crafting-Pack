from typing import Dict, List

from bd_models.models import BallInstance

from crafting.models import CraftingRecipe


async def queryset_to_list(queryset):
    return [item async for item in queryset]


async def find_matching_recipes(ingredient_instance_ids: List[int]) -> List[CraftingRecipe]:
    """Find all recipes that can be crafted with the given ingredient instances."""
    if not ingredient_instance_ids:
        return []

    ball_instances = await queryset_to_list(
        BallInstance.objects.select_related("ball").filter(pk__in=ingredient_instance_ids)
    )

    ball_counts: Dict[int, int] = {}
    for instance in ball_instances:
        ball_counts[instance.ball_id] = ball_counts.get(instance.ball_id, 0) + 1

    all_recipes = await queryset_to_list(
        CraftingRecipe.objects.select_related("result").prefetch_related(
            "ingredients__ingredient",
            "ingredient_groups__options__ball",
        )
    )

    matching_recipes = []
    for recipe in all_recipes:
        if await can_craft_recipe(recipe, ball_counts):
            matching_recipes.append(recipe)

    return matching_recipes


async def can_craft_recipe(recipe: CraftingRecipe, available_ball_counts: Dict[int, int]) -> bool:
    """Check if a recipe can be crafted with available ball counts."""
    recipe_ingredients = await queryset_to_list(
        recipe.ingredients.select_related("ingredient").all()
    )
    for ingredient in recipe_ingredients:
        if ingredient.ingredient_id:
            available_qty = available_ball_counts.get(ingredient.ingredient_id, 0)
            if available_qty < ingredient.quantity:
                return False

    recipe_groups = await queryset_to_list(recipe.ingredient_groups.all())
    for group in recipe_groups:
        group_options = await queryset_to_list(group.options.select_related("ball").all())
        available_from_group = 0

        for option in group_options:
            available_from_group += available_ball_counts.get(option.ball_id, 0)

        if available_from_group < group.required_count:
            return False

    return True


async def determine_ingredient_usage(
    recipe: CraftingRecipe, ingredient_instance_ids: List[int]
) -> List[int]:
    """Determine which specific ball instances to use for a recipe."""
    ball_instances = await queryset_to_list(
        BallInstance.objects.select_related("ball").filter(pk__in=ingredient_instance_ids)
    )

    instances_by_ball = {}
    for instance in ball_instances:
        instances_by_ball.setdefault(instance.ball_id, []).append(instance)

    for ball_id in instances_by_ball:
        instances_by_ball[ball_id].sort(key=lambda x: x.attack_bonus + x.health_bonus)

    instances_to_use = []

    recipe_ingredients = await queryset_to_list(
        recipe.ingredients.select_related("ingredient").all()
    )
    for ingredient in recipe_ingredients:
        if not ingredient.ingredient_id:
            continue

        ball_id = ingredient.ingredient_id
        needed = ingredient.quantity
        if ball_id not in instances_by_ball or len(instances_by_ball[ball_id]) < needed:
            return []

        for _ in range(needed):
            instance = instances_by_ball[ball_id].pop(0)
            instances_to_use.append(instance.pk)

    recipe_groups = await queryset_to_list(recipe.ingredient_groups.all())
    for group in recipe_groups:
        group_options = await queryset_to_list(group.options.select_related("ball").all())
        needed = group.required_count

        available_options = []
        for option in group_options:
            available_qty = len(instances_by_ball.get(option.ball_id, []))
            if available_qty > 0:
                available_options.append((option.ball_id, available_qty))

        available_options.sort(key=lambda x: x[1], reverse=True)

        for ball_id, available_qty in available_options:
            if needed <= 0:
                break

            to_use = min(needed, available_qty)
            for _ in range(to_use):
                instance = instances_by_ball[ball_id].pop(0)
                instances_to_use.append(instance.pk)
            needed -= to_use

        if needed > 0:
            return []

    return instances_to_use
