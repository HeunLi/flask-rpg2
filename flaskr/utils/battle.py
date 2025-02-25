import random


def encounter_enemies(area, world_state):
    """Randomly selects an enemy for the given area, including bosses if conditions are met."""
    # Regular enemies by area
    enemies = {
        "Forest": [
            {
                "name": "Diwata",
                "HP": 18.0,
                "ATK": 4.5,
                "DEF": 4.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Healing Herb", "type": "item"},
                    {"name": "Nature Staff", "type": "weapon", "ATK": 3.0},
                ],
            },
            {
                "name": "Kapri",
                "HP": 20.0,
                "ATK": 4.0,
                "DEF": 5.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Mystic Acorn", "type": "item"},
                    {"name": "Wooden Sword", "type": "weapon", "ATK": 2.5},
                ],
            },
            {
                "name": "Tikbalang",
                "HP": 22.0,
                "ATK": 5.5,
                "DEF": 3.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Lucky Feather", "type": "item"},
                    {"name": "Hoof Blade", "type": "weapon", "ATK": 3.5},
                ],
            },
        ],
        "Mountains": [
            {
                "name": "Mananggal",
                "HP": 25.0,
                "ATK": 5.0,
                "DEF": 4.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Bat Wing", "type": "item"},
                    {"name": "Cursed Dagger", "type": "weapon", "ATK": 4.0},
                ],
            },
            {
                "name": "Tyanak",
                "HP": 18.0,
                "ATK": 6.0,
                "DEF": 3.5,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Demonic Doll", "type": "item"},
                    {"name": "Tiny Blade", "type": "weapon", "ATK": 3.0},
                ],
            },
            {
                "name": "Tik-tik",
                "HP": 20.0,
                "ATK": 5.0,
                "DEF": 5.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Dark Essence", "type": "item"},
                    {"name": "Shadow Bow", "type": "weapon", "ATK": 3.5},
                ],
            },
        ],
        "Cave": [
            {
                "name": "Skeleton",
                "HP": 16.0,
                "ATK": 4.5,
                "DEF": 3.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Bone Fragment", "type": "item"},
                    {"name": "Ancient Sword", "type": "weapon", "ATK": 3.0},
                ],
            },
            {
                "name": "Cave Bat",
                "HP": 15.0,
                "ATK": 4.0,
                "DEF": 3.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Echo Crystal", "type": "item"},
                    {"name": "Sonic Blade", "type": "weapon", "ATK": 2.5},
                ],
            },
            {
                "name": "Goblin",
                "HP": 18.0,
                "ATK": 5.0,
                "DEF": 4.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Gold Nugget", "type": "item"},
                    {"name": "Goblin Sword", "type": "weapon", "ATK": 3.0},
                ],
            },
        ],
        "Swamp": [
            {
                "name": "Swamp Beast",
                "HP": 24.0,
                "ATK": 5.0,
                "DEF": 5.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Toxic Fang", "type": "item"},
                    {"name": "Poison Blade", "type": "weapon", "ATK": 4.0},
                ],
            },
            {
                "name": "Bog Creature",
                "HP": 20.0,
                "ATK": 4.5,
                "DEF": 4.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Cursed Gem", "type": "item"},
                    {"name": "Bog Staff", "type": "weapon", "ATK": 3.5},
                ],
            },
            {
                "name": "Mud Monster",
                "HP": 22.0,
                "ATK": 4.0,
                "DEF": 6.0,
                "EXP_DROP": 100,
                "DROPS": [
                    {"name": "Dark Shard", "type": "item"},
                    {"name": "Mud Hammer", "type": "weapon", "ATK": 3.0},
                ],
            },
        ],
    }

    # Bosses by area with a trigger kill count
    bosses = {
        "Forest": [
            {
                "name": "Big Boss",
                "HP": 50.0,
                "ATK": 8.0,
                "DEF": 5.0,
                "EXP_DROP": 500,
                "DROPS": [
                    {"name": "Forest Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
        "Mountains": [
            {
                "name": "Big Boss",
                "HP": 50.0,
                "ATK": 8.0,
                "DEF": 5.0,
                "EXP_DROP": 500,
                "DROPS": [
                    {"name": "Mountains Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
        "Cave": [
            {
                "name": "Big Boss",
                "HP": 50.0,
                "ATK": 8.0,
                "DEF": 5.0,
                "EXP_DROP": 500,
                "DROPS": [
                    {"name": "Cave Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
        "Swamp": [
            {
                "name": "Big Boss",
                "HP": 50.0,
                "ATK": 8.0,
                "DEF": 5.0,
                "EXP_DROP": 500,
                "DROPS": [
                    {"name": "Swamp Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
    }

    # Check if a boss should appear
    if area in bosses and bosses[area]:
        defeated_in_area = world_state["defeated_enemies"].get(area, [])
        boss_names = [boss["name"].lower() for boss in bosses[area]]
        non_boss_defeated = [
            name for name in defeated_in_area if name.lower() not in boss_names
        ]
        boss_candidates = []
        for boss in bosses[area]:
            if boss["name"] not in defeated_in_area and len(
                non_boss_defeated
            ) >= boss.get("trigger_kill_count", 3):
                boss_candidates.append(boss)
        if boss_candidates:
            boss = random.choice(boss_candidates)
            print(f"\nA mighty presence is felt... {boss['name']} appears!")
            print(
                f"Enemy Stats -> HP: {boss['HP']:.1f}, ATK: {boss['ATK']:.1f}, DEF: {boss['DEF']:.1f}"
            )
            return boss

    # Otherwise, proceed with a normal enemy encounter.
    if area in enemies:
        available_enemies = [
            enemy
            for enemy in enemies[area]
            if enemy["name"] not in world_state["defeated_enemies"].get(area, [])
        ]
        if not available_enemies:
            print(f"\nNo more enemies remain in the {area}!")
            return None
        enemy = random.choice(available_enemies)
        print(f"\nWhile in the {area}, you encounter a {enemy['name']}!")
        print(
            f"Enemy Stats -> HP: {enemy['HP']:.1f}, ATK: {enemy['ATK']:.1f}, DEF: {enemy['DEF']:.1f}"
        )
        return enemy
    else:
        print(f"\nThere are no enemies in the {area}.")
        return None


def calculate_damage(attacker, defender, weapon_bonus=0.0):
    """
    Calculate damage dealt by attacker to defender.
    Returns: (raw_damage, damage_reduction, final_damage, dice_roll)
    """
    # Base damage calculation with weapon bonus (if any)
    base_attack = attacker["ATK"] + weapon_bonus

    # Roll a dice (1-6) for a multiplier between 0.1 and 0.6
    dice_roll = random.randint(1, 6)
    multiplier = dice_roll * 0.1

    # Raw damage before defense reduction
    raw_damage = base_attack + (base_attack * multiplier)

    # Each point in DEF reduces raw damage by 10%
    damage_reduction = raw_damage * (defender["DEF"] / 10)

    # Final damage cannot be negative
    final_damage = max(0, raw_damage - damage_reduction)

    return raw_damage, damage_reduction, final_damage, dice_roll


def add_experience(player, amount):
    player["EXP"] = player.get("EXP", 0) + amount
    player["LVL"] = player.get("LVL", 1)

    while True:
        exp_needed = player["LVL"] * 100
        if player["EXP"] >= exp_needed:
            player["LVL"] += 1
            player["EXP"] -= exp_needed

            # Increase stats on level up
            player["max_HP"] += 5.0
            player["HP"] = player["max_HP"]
            player["ATK"] += 1.0
            player["DEF"] += 1.0

            print(f"\nLevel Up! You are now level {player['LVL']}!")
            print("Stats increased:")
            print(f"HP: +5.0 (Now {player['max_HP']:.1f})")
            print(f"ATK: +1.0 (Now {player['ATK']:.1f})")
            print(f"DEF: +1.0 (Now {player['DEF']:.1f})\n")
        else:
            print(f"EXP: {player['EXP']}/{exp_needed}")
            break
