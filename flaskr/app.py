from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random  # Make sure to import random for random.choice
import random
import time
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
        player["max_HP"] = player["HP"]
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

# -------------------------------------------
# Enemy encounter logic (copy of your logic)
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
        non_boss_defeated = [name for name in defeated_in_area if name.lower() not in boss_names]
        boss_candidates = []
        for boss in bosses[area]:
            if boss["name"] not in defeated_in_area and len(non_boss_defeated) >= boss.get("trigger_kill_count", 3):
                boss_candidates.append(boss)
        if boss_candidates:
            boss = random.choice(boss_candidates)
            print(f"\nA mighty presence is felt... {boss['name']} appears!")
            print(f"Enemy Stats -> HP: {boss['HP']:.1f}, ATK: {boss['ATK']:.1f}, DEF: {boss['DEF']:.1f}")
            return boss

    # Otherwise, proceed with a normal enemy encounter.
    if area in enemies:
        available_enemies = [
            enemy for enemy in enemies[area]
            if enemy["name"] not in world_state["defeated_enemies"].get(area, [])
        ]
        if not available_enemies:
            print(f"\nNo more enemies remain in the {area}!")
            return None
        enemy = random.choice(available_enemies)
        print(f"\nWhile in the {area}, you encounter a {enemy['name']}!")
        print(f"Enemy Stats -> HP: {enemy['HP']:.1f}, ATK: {enemy['ATK']:.1f}, DEF: {enemy['DEF']:.1f}")
        return enemy
    else:
        print(f"\nThere are no enemies in the {area}.")
        return None

# -------------------------------------------
# -----------------------
# Helper Function Definitions
# -----------------------

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

def update_world_state(world_state, area, enemy_name):
    """Update world state when an enemy is defeated."""
    if area not in world_state.get("defeated_enemies", {}):
        world_state["defeated_enemies"] = world_state.get("defeated_enemies", {})
        world_state["defeated_enemies"][area] = []
    world_state["defeated_enemies"][area].append(enemy_name)

    # Ensure visited_areas is a list and update if necessary
    if "visited_areas" not in world_state:
        world_state["visited_areas"] = []
    if area not in world_state["visited_areas"]:
        world_state["visited_areas"].append(area)

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

    save_player(player)

def save_world(world_state, filename="world_save.json"):
    """Save world progress to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(world_state, f, indent=4)
        print("World progress saved successfully!")
        return True
    except Exception as e:
        print(f"Error saving world progress: {e}")
        return False

def save_player(player, filename="player_save.json"):
    """Save player data to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(player, f, indent=4)
        print("\nPlayer progress saved successfully!")
        return True
    except Exception as e:
        print(f"\nError saving player progress: {e}")
        return False
# ... BATTLE HERE ...
@app.route('/battle/attack', methods=['POST'])
def battle_attack():
    """
    Endpoint to process an attack action in battle.
    Uses the helper functions to calculate damage, update the world state,
    award experience, and save progress.
    """
    # Retrieve the current battle state from session
    player = session.get('player_class')
    enemy = session.get('enemy')
    # Ensure world_state has keys for defeated_enemies and visited_areas
    world_state = session.get('world_state', {"defeated_enemies": {}, "visited_areas": []})
    area = session.get('battle_area')

    if not (player and enemy and area):
        return jsonify({'error': 'Battle state not found'}), 400

    # Calculate player's attack damage.
    weapon_bonus = player["equipped_weapon"]["ATK"] if player.get("equipped_weapon") else 0.0
    raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(player, enemy, weapon_bonus)
    enemy["HP"] -= final_damage
    message = f"You attacked {enemy['name']} for {final_damage:.1f} damage! "

    # Check if enemy is defeated.
    if enemy["HP"] <= 0:
        message += f"{enemy['name']} is defeated!"
        update_world_state(world_state, area, enemy["name"])

        # Process enemy drop (weapon or item)
        drop = random.choice(enemy["DROPS"])
        if drop["type"] == "weapon":
            player["inventory"]["weapons"].append({
                "name": drop["name"],
                "ATK": drop["ATK"]
            })
            message += f" Enemy dropped a {drop['name']} (Weapon, ATK: {drop['ATK']}). "
        else:
            player["inventory"]["items"].append({"name": drop["name"]})
            message += f" Enemy dropped a {drop['name']} (Item). "

        add_experience(player, enemy["EXP_DROP"])
        save_world(world_state)
        save_player(player)

        # Remove enemy from session to indicate battle over
        session.pop('enemy', None)
        session['player_class'] = player
        session['world_state'] = world_state
        return jsonify({
            'message': message,
            'battle_over': True,
            'player': player,
            'enemy': enemy  # Optionally, send minimal enemy data
        })

    # Process enemy's counterattack.
    if enemy["name"].lower() == "big boss":
        boss_action = random.choice(["attack", "heal"])
        if boss_action == "attack":
            raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(enemy, player)
            player["HP"] -= final_damage
            message += f"{enemy['name']} counterattacked for {final_damage:.1f} damage! "
        else:
            heal_amount = enemy["max_HP"] * 0.2  # Boss heals 20% of its max HP
            old_hp = enemy["HP"]
            enemy["HP"] = min(enemy["HP"] + heal_amount, enemy["max_HP"])
            message += f"{enemy['name']} healed for {enemy['HP'] - old_hp:.1f} HP! "
    else:
        raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(enemy, player)
        player["HP"] -= final_damage
        message += f"{enemy['name']} counterattacked for {final_damage:.1f} damage! "

    # Check if the player has been defeated.
    if player["HP"] <= 0:
        message += " You have been defeated!"
        save_world(world_state)
        save_player(player)
        session.pop('enemy', None)
        session['player_class'] = player
        session['world_state'] = world_state
        return jsonify({
            'message': message,
            'battle_over': True,
            'player': player,
            'enemy': enemy
        })

    # Update session with new state and return the battle status.
    session['player_class'] = player
    session['enemy'] = enemy
    session['world_state'] = world_state
    return jsonify({
        'message': message,
        'battle_over': False,
        'player': player,
        'enemy': enemy
    })


@app.route('/battle/defend', methods=['POST'])
def battle_defend():
    player = session.get('player_class')
    enemy = session.get('enemy')
    world_state = session.get('world_state', {"defeated_enemies": {}})
    area = session.get('battle_area')
    
    if not (player and enemy and area):
        return jsonify({'error': 'Battle state not found'}), 400

    temp_def_bonus = player["DEF"] * 0.5
    player["DEF"] += temp_def_bonus
    message = "You brace yourself and boost your defense! "

    # Enemy attacks while you are defending
    raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(enemy, player)
    player["HP"] -= final_damage
    message += f"{enemy['name']} attacked for {final_damage:.1f} damage! "

    # Remove temporary defense bonus
    player["DEF"] -= temp_def_bonus

    if player["HP"] <= 0:
        message += " You have been defeated!"
        session.pop('enemy', None)
        session['player_class'] = player
        session['world_state'] = world_state
        return jsonify({
            'message': message,
            'battle_over': True,
            'player': player,
            'enemy': enemy
        })

    session['player_class'] = player
    session['enemy'] = enemy
    session['world_state'] = world_state
    return jsonify({
        'message': message,
        'battle_over': False,
        'player': player,
        'enemy': enemy
    })

@app.route('/battle/run', methods=['POST'])
def battle_run():
    player = session.get('player_class')
    enemy = session.get('enemy')
    world_state = session.get('world_state', {"defeated_enemies": {}})
    area = session.get('battle_area')
    
    if not (player and enemy and area):
        return jsonify({'error': 'Battle state not found'}), 400

    run_chance = random.random()
    message = ""
    if run_chance > 0.5:
        message = "You successfully escaped the battle!"
        session.pop('enemy', None)
        session['player_class'] = player
        session['world_state'] = world_state
        return jsonify({
            'message': message,
            'battle_over': True,
            'player': player,
            'enemy': enemy
        })
    else:
        message = "Escape failed! As you try to run, "
        raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(enemy, player)
        player["HP"] -= final_damage
        message += f"{enemy['name']} attacked you for {final_damage:.1f} damage! "
        
        if player["HP"] <= 0:
            message += " You have been defeated!"
            session.pop('enemy', None)
            session['player_class'] = player
            session['world_state'] = world_state
            return jsonify({
                'message': message,
                'battle_over': True,
                'player': player,
                'enemy': enemy
            })

    session['player_class'] = player
    session['enemy'] = enemy
    session['world_state'] = world_state
    return jsonify({
        'message': message,
        'battle_over': False,
        'player': player,
        'enemy': enemy
    })

#--------------------------------------------

# -------------------------------------------
# ... INVENTORY HERE ...

@app.route('/inventory', methods=['GET'])
def inventory():
    player = session.get('player_class')
    if player:
        return jsonify({
            "gold": player.get("gold", 0),
            "HP": player.get("HP"),
            "max_HP": player.get("max_HP"),
            "equipped_weapon": player.get("equipped_weapon"),
            "weapons": player["inventory"]["weapons"],
            "items": player["inventory"]["items"]
        })
    return jsonify({"error": "Player not found"}), 404

@app.route('/inventory/equip', methods=['POST'])
def equip_weapon():
    player = session.get('player_class')
    if not player:
        return jsonify({'error': 'Player not found'}), 404

    weapon_index = request.form.get('weapon_index')
    try:
        idx = int(weapon_index) - 1
        weapons = player["inventory"]["weapons"]
        if idx < 0 or idx >= len(weapons):
            return jsonify({'error': 'Invalid weapon index'}), 400
        player["equipped_weapon"] = weapons[idx]
        session['player_class'] = player
        return jsonify({'message': f"You have equipped {weapons[idx]['name']}."})
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400

@app.route('/inventory/use', methods=['POST'])
def use_item():
    player = session.get('player_class')
    if not player:
        return jsonify({'error': 'Player not found'}), 404

    item_index = request.form.get('item_index')
    try:
        idx = int(item_index) - 1
        items = player["inventory"]["items"]
        if idx < 0 or idx >= len(items):
            return jsonify({'error': 'Invalid item index'}), 400
        item = items.pop(idx)
        if item["name"] in ["Small Potion", "Health Potion"]:
            heal_amount = player["max_HP"] * item["heal"]
            old_hp = player["HP"]
            player["HP"] = min(player["HP"] + heal_amount, player["max_HP"])
            session['player_class'] = player
            return jsonify({'message': f"You used a {item['name']} and restored {player['HP'] - old_hp:.1f} HP."})
        else:
            return jsonify({'error': 'Item effect not implemented.'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400


# ... rest of your app routes ...
# -------------------------------------------
@app.route('/')
def home():
    return render_template('game/home.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        # Retrieve form data
        player_name = request.form.get('player_name')
        player_class_choice = request.form.get('player_class')
        
        # Generate class-specific data
        player_class_data = get_class_data(player_class_choice)
        
        # Save both name and class data in session for persistence
        session['player_name'] = player_name
        session['player_class'] = player_class_data
        
        return redirect(url_for('game'))
    return render_template('game/start.html')

@app.route('/game')
def game():
    player_name = session.get('player_name', 'Adventurer')
    player_class = session.get('player_class')
    return render_template('game/game.html', player_name=player_name, player_class=player_class)
    
@app.route('/battle')
def battle():
    # Get the chosen location from the query string, e.g., /battle?location=Forest
    location = request.args.get('location', None)
    enemy = None
    if location:
        # Use a simple world state from session to track defeated enemies.
        world_state = session.get("world_state", {"defeated_enemies": {}})
        if location not in world_state["defeated_enemies"]:
            world_state["defeated_enemies"][location] = []
        enemy = encounter_enemies(location, world_state)
        session["world_state"] = world_state  # Update session state if necessary
        
        # Save enemy and area in session for the battle actions
        if enemy:
            session['enemy'] = enemy
            session['battle_area'] = location
    return render_template('game/battle.html', location=location, enemy=enemy)

if __name__ == '__main__':
    app.run(debug=True)
