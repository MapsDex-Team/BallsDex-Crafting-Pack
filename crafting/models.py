from django.db import models

from bd_models.models import Ball

class CraftingRecipe(models.Model):
    result = models.ForeignKey(Ball, on_delete=models.CASCADE, related_name="crafted_by")

    class Meta:
        db_table = "craftingrecipe"

    def __str__(self):
        if self.result:
            return f"{self.result} Recipe"
        return "Unnamed Crafting Recipe"


class CraftingIngredient(models.Model):
    recipe = models.ForeignKey("CraftingRecipe", on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(
        Ball,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "craftingingredient"
        constraints = [
            models.UniqueConstraint(fields=("recipe", "ingredient"), name="unique_recipe_ingredient")
        ]

    def __str__(self):
        return f"{self.ingredient} x{self.quantity}"

class CraftingIngredientGroup(models.Model):
    recipe = models.ForeignKey("CraftingRecipe", on_delete=models.CASCADE, related_name="ingredient_groups")
    name = models.CharField(max_length=100)
    required_count = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "craftingingredientgroup"

    def __str__(self):
        return f"{self.name} (need {self.required_count})"


class CraftingGroupOption(models.Model):
    group = models.ForeignKey("CraftingIngredientGroup", on_delete=models.CASCADE, related_name="options")
    ball = models.ForeignKey(Ball, on_delete=models.CASCADE, related_name="group_memberships")

    class Meta:
        db_table = "craftinggroupoption"
        constraints = [
            models.UniqueConstraint(fields=("group", "ball"), name="unique_group_ball")
        ]

    def __str__(self):
        return f"{self.ball} in {self.group.name}"
