import random


def encounter_enemies(area, world_state):
    """Randomly selects an enemy for the given area, including bosses if conditions are met."""
    """Meet enemy only when the area hasn't been cleared yet."""
    # Regular enemies by area
    enemies = {
        "Forest": [
            {
                "name": "Diwata",
                "HP": 18,
                "ATK": 5,
                "DEF": 4,
                "EXP_DROP": 100,
                "MAX_HP": 18,
                "DROPS": [
                    {"name": "Herbs", "type": "item"},
                    {"name": "Nature Staff", "type": "weapon", "ATK": 3},
                ],
            },
            {
                "name": "Kapri",
                "HP": 20,
                "ATK": 4,
                "DEF": 5,
                "EXP_DROP": 100,
                "MAX_HP": 20,
                "DROPS": [
                    {"name": "Mystic Acorn", "type": "item"},
                    {"name": "Wooden Sword", "type": "weapon", "ATK": 3},
                ],
            },
            {
                "name": "Tikbalang",
                "HP": 22,
                "ATK": 6,
                "DEF": 3,
                "EXP_DROP": 100,
                "MAX_HP": 22,
                "DROPS": [
                    {"name": "Lucky Feather", "type": "item"},
                    {"name": "Hoof Blade", "type": "weapon", "ATK": 4},
                ],
            },
        ],
        "Mountains": [
            {
                "name": "Manananggal",
                "HP": 25,
                "ATK": 5,
                "DEF": 4,
                "EXP_DROP": 100,
                "MAX_HP": 25,
                "DROPS": [
                    {"name": "Bat Wing", "type": "item"},
                    {"name": "Cursed Dagger", "type": "weapon", "ATK": 4},
                ],
            },
            {
                "name": "Tyanak",
                "HP": 18,
                "ATK": 6,
                "DEF": 4,
                "EXP_DROP": 100,
                "MAX_HP": 18,
                "DROPS": [
                    {"name": "Demonic Doll", "type": "item"},
                    {"name": "Tiny Blade", "type": "weapon", "ATK": 3},
                ],
            },
            {
                "name": "Tik-tik",
                "HP": 20,
                "ATK": 5,
                "DEF": 5,
                "EXP_DROP": 100,
                "MAX_HP": 20,
                "DROPS": [
                    {"name": "Dark Essence", "type": "item"},
                    {"name": "Shadow Bow", "type": "weapon", "ATK": 4},
                ],
            },
        ],
        "Cave": [
            {
                "name": "Skeleton",
                "HP": 16,
                "ATK": 5,
                "DEF": 3,
                "EXP_DROP": 100,
                "MAX_HP": 16,
                "DROPS": [
                    {"name": "Bone Fragment", "type": "item"},
                    {"name": "Ancient Sword", "type": "weapon", "ATK": 3},
                ],
            },
            {
                "name": "Cave Bat",
                "HP": 15,
                "ATK": 4,
                "DEF": 3,
                "EXP_DROP": 100,
                "MAX_HP": 15,
                "DROPS": [
                    {"name": "Echo Crystal", "type": "item"},
                    {"name": "Sonic Blade", "type": "weapon", "ATK": 3},
                ],
            },
            {
                "name": "Goblin",
                "HP": 18,
                "ATK": 5,
                "DEF": 4,
                "EXP_DROP": 100,
                "MAX_HP": 18,
                "DROPS": [
                    {"name": "Gold Nugget", "type": "item"},
                    {"name": "Goblin Sword", "type": "weapon", "ATK": 3},
                ],
            },
        ],
        "Swamp": [
            {
                "name": "Swamp Beast",
                "HP": 24,
                "ATK": 5,
                "DEF": 5,
                "EXP_DROP": 100,
                "MAX_HP": 24,
                "DROPS": [
                    {"name": "Toxic Fang", "type": "item"},
                    {"name": "Poison Blade", "type": "weapon", "ATK": 4},
                ],
            },
            {
                "name": "Bog Creature",
                "HP": 20,
                "ATK": 5,
                "DEF": 4,
                "EXP_DROP": 100,
                "MAX_HP": 20,
                "DROPS": [
                    {"name": "Cursed Gem", "type": "item"},
                    {"name": "Bog Staff", "type": "weapon", "ATK": 4},
                ],
            },
            {
                "name": "Mud Monster",
                "HP": 22,
                "ATK": 4,
                "DEF": 6,
                "EXP_DROP": 100,
                "MAX_HP": 22,
                "DROPS": [
                    {"name": "Dark Shard", "type": "item"},
                    {"name": "Mud Hammer", "type": "weapon", "ATK": 3},
                ],
            },
        ],
    }

    bosses = {
        "Forest": [
            {
                "name": "Big Boss",
                "HP": 50,
                "ATK": 8,
                "DEF": 5,
                "EXP_DROP": 500,
                "MAX_HP": 50,
                "DROPS": [
                    {"name": "Forest Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
        "Mountains": [
            {
                "name": "Big Boss",
                "HP": 50,
                "ATK": 8,
                "DEF": 5,
                "EXP_DROP": 500,
                "MAX_HP": 50,
                "DROPS": [
                    {"name": "Mountains Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
        "Cave": [
            {
                "name": "Big Boss",
                "HP": 50,
                "ATK": 8,
                "DEF": 5,
                "EXP_DROP": 500,
                "MAX_HP": 50,
                "DROPS": [
                    {"name": "Cave Boss Trophy", "type": "item"},
                ],
                "trigger_kill_count": 3,
            }
        ],
        "Swamp": [
            {
                "name": "Big Boss",
                "HP": 50,
                "ATK": 8,
                "DEF": 5,
                "EXP_DROP": 500,
                "MAX_HP": 50,
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


def calculate_damage(attacker, defender, weapon_bonus=0):
    base_attack = attacker["ATK"] + weapon_bonus
    dice_roll = random.randint(1, 6)
    multiplier = dice_roll * 0.1

    raw_damage = base_attack + (base_attack * multiplier)

    damage_reduction = raw_damage * (defender["DEF"] / 10)

    final_damage = int(round(max(1, raw_damage - damage_reduction)))

    return raw_damage, damage_reduction, final_damage


def add_drops(player, enemy):
    drop = random.choice(enemy["DROPS"])
    if drop["type"] == "weapon":
        player["inventory"]["weapons"].append(
            {"name": drop["name"], "ATK": drop["ATK"]}
        )
        print(f"\nThe enemy dropped a {drop['name']} (Weapon, ATK: {drop['ATK']})!")
    else:
        player["inventory"]["items"].append({"name": drop["name"]})
        print(f"\nThe enemy dropped a {drop['name']} (Item)!")


def add_experience(player, amount):
    player["EXP"] = player.get("EXP", 0) + amount
    player["LVL"] = player.get("LVL", 1)

    while True:
        exp_needed = player["LVL"] * 100
        if player["EXP"] >= exp_needed:
            player["LVL"] += 1
            player["EXP"] -= exp_needed

            # Increase stats on level up
            player["MAX_HP"] += 5.0
            player["HP"] = player["MAX_HP"]
            player["MAX_HP"] += 5.0
            player["HP"] = player["MAX_HP"]
            player["ATK"] += 1.0
            player["DEF"] += 1.0

            print(f"\nLevel Up! You are now level {player['LVL']}!")
            print("Stats increased:")
            print(f"HP: +5.0 (Now {player['MAX_HP']:.1f})")
            print(f"ATK: +1.0 (Now {player['ATK']:.1f})")
            print(f"DEF: +1.0 (Now {player['DEF']:.1f})\n")
        else:
            print(f"EXP: {player['EXP']}/{exp_needed}")
            break
