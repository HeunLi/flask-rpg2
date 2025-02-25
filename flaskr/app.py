from flask import Flask, render_template, request, redirect, url_for, jsonify
import random

# Utils
from utils.world import (
    save_player,
    save_world,
    load_player,
    load_world,
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
    location = request.args.get("location", None)
    enemy = None
    if location:
        world_state = load_world()
        if location not in world_state["defeated_enemies"]:
            world_state["defeated_enemies"][location] = []

        enemy = encounter_enemies(location, world_state)

        if enemy:
            world_state["current_battle"] = {"enemy": enemy, "area": location}
            save_world(world_state)

    return render_template("game/battle.html", location=location, enemy=enemy)


@app.route("/battle/attack", methods=["POST"])
def battle_attack():
    player = load_player()
    world_state = load_world()

    current_battle = world_state.get("current_battle", {})
    enemy = current_battle.get("enemy")
    area = current_battle.get("area")

    if not (player and enemy and area):
        return jsonify({"error": "Battle state not found"}), 400

    # Calculate damage
    weapon_bonus = player.get("equipped_weapon", {}).get("ATK", 0.0)
    raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
        player, enemy, weapon_bonus
    )
    enemy["HP"] -= final_damage
    message = f"You attacked {enemy['name']} for {final_damage:.1f} damage! "

    # Handle enemy defeat
    if enemy["HP"] <= 0:
        message += f"{enemy['name']} is defeated!"
        update_world_state(world_state, area, enemy["name"])

        # Process drops
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
        world_state.pop("current_battle", None)  # Clear battle state
        save_world(world_state)
        save_player(player)

        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )

    # Process enemy counter-attack
    if enemy["name"].lower() == "big boss":
        # Boss logic here...
        pass
    else:
        raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
            enemy, player
        )
        player["HP"] -= final_damage
        message += f"{enemy['name']} counterattacked for {final_damage:.1f} damage! "

    # Check player defeat
    if player["HP"] <= 0:
        message += " You have been defeated!"
        world_state.pop("current_battle", None)
        save_world(world_state)
        save_player(player)
        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )

    # Update battle state
    world_state["current_battle"]["enemy"] = enemy
    save_world(world_state)
    save_player(player)

    return jsonify(
        {"message": message, "battle_over": False, "player": player, "enemy": enemy}
    )


@app.route("/battle/defend", methods=["POST"])
def battle_defend():
    player = load_player()
    world_state = load_world()

    current_battle = world_state.get("current_battle", {})
    enemy = current_battle.get("enemy")
    area = current_battle.get("area")

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
        world_state.pop("current_battle", None)
        save_world(world_state)
        save_player(player)
        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )

    world_state["current_battle"]["enemy"] = enemy
    save_world(world_state)
    save_player(player)
    return jsonify(
        {"message": message, "battle_over": False, "player": player, "enemy": enemy}
    )


@app.route("/battle/run", methods=["POST"])
def battle_run():
    player = load_player()
    world_state = load_world()

    current_battle = world_state.get("current_battle", {})
    enemy = current_battle.get("enemy")
    area = current_battle.get("area")

    if not (player and enemy and area):
        return jsonify({"error": "Battle state not found"}), 400

    run_chance = random.random()
    message = ""

    if run_chance > 0.5:
        message = "You successfully escaped the battle!"
        world_state.pop("current_battle", None)
        save_world(world_state)
        save_player(player)
        return jsonify(
            {"message": message, "battle_over": True, "player": player, "enemy": enemy}
        )

    message = "Escape failed! As you try to run, "
    raw_damage, damage_reduction, final_damage, dice_roll = calculate_damage(
        enemy, player
    )
    player["HP"] -= final_damage
    message += f"{enemy['name']} attacked you for {final_damage:.1f} damage! "

    if player["HP"] <= 0:
        message += " You have been defeated!"
        world_state.pop("current_battle", None)
        save_world(world_state)
        save_player(player)
        return jsonify(
            {
                "message": message,
                "battle_over": True,
                "player": player,
                "enemy": enemy,
            }
        )

    world_state["current_battle"]["enemy"] = enemy
    save_world(world_state)
    save_player(player)
    return jsonify(
        {"message": message, "battle_over": False, "player": player, "enemy": enemy}
    )


# -------------------------------------------
# ... INVENTORY HERE ...
# --------------------------------------------


@app.route("/inventory", methods=["GET"])
def inventory():
    player = load_player()
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
    player = load_player()
    if not player:
        return jsonify({"error": "Player not found"}), 404

    weapon_index = request.form.get("weapon_index")
    try:
        idx = int(weapon_index) - 1
        weapons = player["inventory"]["weapons"]
        if idx < 0 or idx >= len(weapons):
            return jsonify({"error": "Invalid weapon index"}), 400
        player["equipped_weapon"] = weapons[idx]
        save_player(player)
        return jsonify({"message": f"You have equipped {weapons[idx]['name']}."})
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400


@app.route("/inventory/use", methods=["POST"])
def use_item():
    player = load_player()
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
            save_player(player)
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
