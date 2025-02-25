from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random  # Make sure to import random for random.choice

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
