def get_class_data(choice):
    """Return player data based on selected class."""
    classes = {
        "1": {
            "class": "Wizard",
            "HP": 20.0,
            "ATK": 6.0,
            "DEF": 4.0,
            "LVL": 1,
            "EXP": 0,
        },
        "2": {
            "class": "Swordsman",
            "HP": 25.0,
            "ATK": 5.0,
            "DEF": 6.0,
            "LVL": 1,
            "EXP": 0,
        },
        "3": {
            "class": "Ranger",
            "HP": 22.0,
            "ATK": 5.5,
            "DEF": 5.0,
            "LVL": 1,
            "EXP": 0,
        },
    }
    if choice in classes:
        player = classes[choice]
        player["MAX_HP"] = player["HP"]
        # Set up a default inventory with a basic weapon and potions.
        if choice == "1":
            default_weapon = {"name": "Basic Staff", "ATK": 2.0}
        elif choice == "2":
            default_weapon = {"name": "Basic Sword", "ATK": 2.0}
        else:
            default_weapon = {"name": "Basic Bow", "ATK": 2.0}
        player["inventory"] = {
            "weapons": [default_weapon],
            "items": [
                {"name": "Small Potion", "heal": 0.25},
                {"name": "Health Potion", "heal": 0.5},
            ],
        }
        player["equipped_weapon"] = default_weapon
        player["gold"] = 100
        return player
    return None
