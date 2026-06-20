from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bd_models", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="CraftingRecipe",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "result",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="crafted_by",
                        to="bd_models.ball",
                    ),
                ),
            ],
            options={
                "db_table": "craftingrecipe",
            },
        ),
        migrations.CreateModel(
            name="CraftingIngredientGroup",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("required_count", models.PositiveIntegerField(default=1)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ingredient_groups",
                        to="crafting.craftingrecipe",
                    ),
                ),
            ],
            options={
                "db_table": "craftingingredientgroup",
            },
        ),
        migrations.CreateModel(
            name="CraftingIngredient",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "ingredient",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="bd_models.ball",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ingredients",
                        to="crafting.craftingrecipe",
                    ),
                ),
            ],
            options={
                "db_table": "craftingingredient",
            },
        ),
        migrations.CreateModel(
            name="CraftingGroupOption",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "ball",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="group_memberships",
                        to="bd_models.ball",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="crafting.craftingingredientgroup",
                    ),
                ),
            ],
            options={
                "db_table": "craftinggroupoption",
            },
        ),
        migrations.AddConstraint(
            model_name="craftingingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_recipe_ingredient"
            ),
        ),
        migrations.AddConstraint(
            model_name="craftinggroupoption",
            constraint=models.UniqueConstraint(fields=("group", "ball"), name="unique_group_ball"),
        ),
    ]
