# BallsDex V3 Crafting Package

Crafting system for **BallsDex V3**.

## Commands

| Command | Description |
|---|---|
| `/craft begin` | Start a crafting session, optionally locked to a selected special. |
| `/craft add` | Add one owned countryball instance to the active crafting session. |
| `/craft remove` | Remove one countryball instance from the active crafting session. |
| `/craft clear` | Clear all added ingredients from the active crafting session. |
| `/craft recipes` | Show configured recipes, optionally filtered by result countryball. |

## Installation

### 1 — Configure extra.toml

**If the file doesn't exist:** Create a new file `extra.toml` in your `config` folder under the BallsDex directory.

**If you already have other packages installed:** Add the following configuration to your existing `extra.toml` file. Each package is defined by a `[[ballsdex.packages]]` section, so you can have multiple packages installed.

Add the following configuration:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/Mitoooooooopo/Crafting-package-BD.git"
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
location = "git+https://github.com/Mitoooooooopo/Crafting-package-BD.git"
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

## Applying changes without a full restart

After changing commands or installing the package, reload and sync:

```text
@YourBot reload crafting.package
@YourBot reloadtree
```

This updates the command list in Discord within seconds. Admin panel display changes may require restarting the admin panel container.

## Crafting Result

When a craft succeeds, the bot edits the crafting message with the crafted result:

```text
Successfully crafted United States of America (ID: #1A2B)!
```

The success embed also lists the ingredients used, the new instance stats, total sacrificed stats, and net stat change.
