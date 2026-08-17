# BallsDex Crafting Package

> [!NOTE]
> I don't recommend using this package, this version is filled with bugs. a new version is currently in development which will be a complete rewrite of this package with cleaner code, less boilerplate and more features.

## Commands

| Command | Description |
|---|---|
| `/craft begin` | Start a crafting session, optionally locked to a selected special. |
| `/craft add` | Add one owned countryball instance to the active crafting session. |
| `/craft remove` | Remove one countryball instance from the active crafting session. |
| `/craft clear` | Clear all added ingredients from the active crafting session. |
| `/craft recipes` | Show configured recipes, optionally filtered by result countryball. |
| `/craft elemental` | Consume Fire, Earth, Water, and Electric specials of the selected countryball to create an Elemental special. |

## Installation

### 1 — Configure extra.toml

**If the file doesn't exist:** Create a new file `extra.toml` in your `config` folder under the BallsDex directory.

**If you already have other packages installed:** Add the following configuration to your existing `extra.toml` file. Each package is defined by a `[[ballsdex.packages]]` section, so you can have multiple packages installed.

Add the following configuration:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/Mitoooooooopo/Crafting-package-BD.git@0.3.1#main"
path = "crafting"
enabled = true
```

**Example of multiple packages:**

```toml
# First package
[[ballsdex.packages]]
location = "git+https://github.com/example/other-package.git"
path = "other"
enabled = true

# Crafting Package
[[ballsdex.packages]]
location = "git+https://github.com/Mitoooooooopo/Crafting-package-BD.git@0.3.1#main"
path = "crafting"
enabled = true
```

### 2 — Rebuild and start the bot

```bash
docker compose build
docker compose up -d
```

This will install the package and start the bot.

## Admin Panel Setup

Go to **Crafting → Crafting recipes** and create a recipe.

| Field | Description |
|---|---|
| `Result` | The countryball created when the recipe succeeds. |
| `Ingredients` | Fixed countryballs required by the recipe. |
| `Quantity` | How many of that ingredient are required. |
| `Ingredient groups` | Optional groups where players can provide any matching option. |
| `Required count` | How many balls from that group are required. |

### Ingredient Groups

Ingredient groups let a recipe accept flexible ingredients. For example, a group named `European Countries` with `required_count = 2` can allow the player to use any two configured group options.

After creating a crafting ingredient group, open it in the admin panel and add its group options.

## Admin Panel — Crafting Recipes

Under **Crafting → Crafting recipes** you can see every recipe, including:

- **Result** — countryball created by the recipe
- **Ingredients** — fixed ingredient requirements
- **Ingredient groups** — flexible requirement groups
- **Group options** — countryballs accepted by a group

Recipes and groups are created manually in the admin panel.

## Elemental Crafting

`/craft elemental` automatically finds one non-favorited, unlocked Fire, Earth, Water, and Electric special for the selected countryball in the user's inventory. If all four are available, the command consumes them and gives the user a new Elemental special of the same countryball.

Set the hardcoded IDs in `crafting/package/cog.py` before the event starts:

- `ELEMENTAL_INGREDIENT_SPECIAL_IDS` for Fire, Earth, Water, and Electric
- `ELEMENTAL_RESULT_SPECIAL_ID` for Elemental

## Applying changes without a full restart

After changing commands or installing the package, reload and sync:

```text
@YourBot reload crafting.package
@YourBot reloadtree
```

This updates the commands in Discord. Admin panel display changes may require restarting the admin panel container.
