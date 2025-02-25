from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random

# Utils
from utils.world import (
    save_player,
    save_world,
    load_player,
    update_world_state,
)
from utils.game_logic import get_class_data
from utils.battle import calculate_damage, add_experience, encounter_enemies

app = Flask(__name__)
app.secret_key = "your_secret_key"

global player
player = {}


@app.route("/")
def home():
    return render_template("game/home.html", player=player)


@app.route("/start", methods=["GET", "POST"])
def start():
    if player:
        return redirect(url_for("game"))

    if request.method == "POST":
        # Retrieve form data
        player_name = request.form.get("player_name")
        player_class_choice = request.form.get("player_class")
        player_class_data = get_class_data(player_class_choice)

        # save player to file with username
        player_class_data["username"] = player_name
        save_player(player_class_data)

        # Save both name and class data in session for persistence
        session["player_name"] = player_name
        session["player_class"] = player_class_data

        return redirect(url_for("game"))
    return render_template("game/start.html")


@app.route("/game")
def game():
    player = load_player()
    return render_template("game/game.html", player=player)


# -------------------------------------------
# ... BATTLE ENDPOINTS ...
# --------------------------------------------


@app.route("/battle")
def battle():
    # Get the chosen location from the query string, e.g., /battle?location=Forest
    location = request.args.get("location", None)
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
            session["enemy"] = enemy
            session["battle_area"] = location
    return render_template("game/battle.html", location=location, enemy=enemy)


@app.route("/battle/attack", methods=["POST"])
def battle_attack():
    """
    Endpoint to process an attack action in battle.
    Uses the helper functions to calculate damage, update the world state,
    award experience, and save progress.
    """
    # Retrieve the current battle state from session
    player = session.get("player_class")
    enemy = session.get("enemy")
    # Ensure world_state has keys for defeated_enemies and visited_areas
    world_state = session.get(
        "world_state", {"defeated_enemies": {}, "visited_areas": []}
    )
    area = session.get("battle_area")

    if not (player and enemy and area):
        return jsonify({"error": "Battle state not found"}), 400

    # Calculate player's attack damage.
    weapon_bonus = (
        player["equipped_weapon"]["ATK"] if player.get("equipped_weapon") else 0.0
    )
    raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
        player, enemy, weapon_bonus
    )
    enemy["HP"] -= final_damage
    message = f"You attacked {enemy['name']} for {final_damage:.1f} damage! "

    # Check if enemy is defeated.
    if enemy["HP"] <= 0:
        message += f"{enemy['name']} is defeated!"
        update_world_state(world_state, area, enemy["name"])

        # Process enemy drop (weapon or item)
        drop = random.choice(enemy["DROPS"])
        if drop["type"] == "weapon":
            player["inventory"]["weapons"].append(
                {"name": drop["name"], "ATK": drop["ATK"]}
            )
            message += f" Enemy dropped a {drop['name']} (Weapon, ATK: {drop['ATK']}). "
        else:
            player["inventory"]["items"].append({"name": drop["name"]})
            message += f" Enemy dropped a {drop['name']} (Item). "

        add_experience(player, enemy["EXP_DROP"])
        save_world(world_state)
        save_player(player)

        # Remove enemy from session to indicate battle over
        session.pop("enemy", None)
        session["player_class"] = player
        session["world_state"] = world_state
        return jsonify(
            {
                "message": message,
                "battle_over": True,
                "player": player,
                "enemy": enemy,  # Optionally, send minimal enemy data
            }
        )

    # Process enemy's counterattack.
    if enemy["name"].lower() == "big boss":
        boss_action = random.choice(["attack", "heal"])
        if boss_action == "attack":
            raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
                enemy, player
            )
            player["HP"] -= final_damage
            message += (
                f"{enemy['name']} counterattacked for {final_damage:.1f} damage! "
            )
        else:
            heal_amount = enemy["max_HP"] * 0.2  # Boss heals 20% of its max HP
            old_hp = enemy["HP"]
            enemy["HP"] = min(enemy["HP"] + heal_amount, enemy["max_HP"])
            message += f"{enemy['name']} healed for {enemy['HP'] - old_hp:.1f} HP! "
    else:
        raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
            enemy, player
        )
        player["HP"] -= final_damage
        message += f"{enemy['name']} counterattacked for {final_damage:.1f} damage! "

    # Check if the player has been defeated.
    if player["HP"] <= 0:
        message += " You have been defeated!"
        save_world(world_state)
        save_player(player)
        session.pop("enemy", None)
        session["player_class"] = player
        session["world_state"] = world_state
        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )

    # Update session with new state and return the battle status.
    session["player_class"] = player
    session["enemy"] = enemy
    session["world_state"] = world_state
    return jsonify(
        {"message": message, "battle_over": False, "player": player, "enemy": enemy}
    )


@app.route("/battle/defend", methods=["POST"])
def battle_defend():
    player = session.get("player_class")
    enemy = session.get("enemy")
    world_state = session.get("world_state", {"defeated_enemies": {}})
    area = session.get("battle_area")

    if not (player and enemy and area):
        return jsonify({"error": "Battle state not found"}), 400

    temp_def_bonus = player["DEF"] * 0.5
    player["DEF"] += temp_def_bonus
    message = "You brace yourself and boost your defense! "

    # Enemy attacks while you are defending
    raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
        enemy, player
    )
    player["HP"] -= final_damage
    message += f"{enemy['name']} attacked for {final_damage:.1f} damage! "

    # Remove temporary defense bonus
    player["DEF"] -= temp_def_bonus

    if player["HP"] <= 0:
        message += " You have been defeated!"
        session.pop("enemy", None)
        session["player_class"] = player
        session["world_state"] = world_state
        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )

    session["player_class"] = player
    session["enemy"] = enemy
    session["world_state"] = world_state
    return jsonify(
        {"message": message, "battle_over": False, "player": player, "enemy": enemy}
    )


@app.route("/battle/run", methods=["POST"])
def battle_run():
    player = session.get("player_class")
    enemy = session.get("enemy")
    world_state = session.get("world_state", {"defeated_enemies": {}})
    area = session.get("battle_area")

    if not (player and enemy and area):
        return jsonify({"error": "Battle state not found"}), 400

    run_chance = random.random()
    message = ""
    if run_chance > 0.5:
        message = "You successfully escaped the battle!"
        session.pop("enemy", None)
        session["player_class"] = player
        session["world_state"] = world_state
        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )
    else:
        message = "Escape failed! As you try to run, "
        raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
            enemy, player
        )
        player["HP"] -= final_damage
        message += f"{enemy['name']} attacked you for {final_damage:.1f} damage! "

        if player["HP"] <= 0:
            message += " You have been defeated!"
            session.pop("enemy", None)
            session["player_class"] = player
            session["world_state"] = world_state
            return jsonify(
                {
                    "message": message,
                    "battle_over": True,
                    "player": player,
                    "enemy": enemy,
                }
            )

    session["player_class"] = player
    session["enemy"] = enemy
    session["world_state"] = world_state
    return jsonify(
        {"message": message, "battle_over": False, "player": player, "enemy": enemy}
    )


# -------------------------------------------
# ... INVENTORY HERE ...
# --------------------------------------------


@app.route("/inventory", methods=["GET"])
def inventory():
    player = session.get("player_class")
    if player:
        return jsonify(
            {
                "gold": player.get("gold", 0),
                "HP": player.get("HP"),
                "max_HP": player.get("max_HP"),
                "equipped_weapon": player.get("equipped_weapon"),
                "weapons": player["inventory"]["weapons"],
                "items": player["inventory"]["items"],
            }
        )
    return jsonify({"error": "Player not found"}), 404


@app.route("/inventory/equip", methods=["POST"])
def equip_weapon():
    player = session.get("player_class")
    if not player:
        return jsonify({"error": "Player not found"}), 404

    weapon_index = request.form.get("weapon_index")
    try:
        idx = int(weapon_index) - 1
        weapons = player["inventory"]["weapons"]
        if idx < 0 or idx >= len(weapons):
            return jsonify({"error": "Invalid weapon index"}), 400
        player["equipped_weapon"] = weapons[idx]
        session["player_class"] = player
        return jsonify({"message": f"You have equipped {weapons[idx]['name']}."})
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400


@app.route("/inventory/use", methods=["POST"])
def use_item():
    player = session.get("player_class")
    if not player:
        return jsonify({"error": "Player not found"}), 404

    item_index = request.form.get("item_index")
    try:
        idx = int(item_index) - 1
        items = player["inventory"]["items"]
        if idx < 0 or idx >= len(items):
            return jsonify({"error": "Invalid item index"}), 400
        item = items.pop(idx)
        if item["name"] in ["Small Potion", "Health Potion"]:
            heal_amount = player["max_HP"] * item["heal"]
            old_hp = player["HP"]
            player["HP"] = min(player["HP"] + heal_amount, player["max_HP"])
            session["player_class"] = player
            return jsonify(
                {
                    "message": f"You used a {item['name']} and restored {player['HP'] - old_hp:.1f} HP."
                }
            )
        else:
            return jsonify({"error": "Item effect not implemented."}), 400
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400


if __name__ == "__main__":
    player = load_player()
    app.run(debug=True)
