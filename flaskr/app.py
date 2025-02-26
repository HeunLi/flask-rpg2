from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import os

# Utils
from utils.world import (
    save_player,
    save_world,
    load_player,
    load_world,
    update_world_state,
)
from utils.game_logic import get_class_data
from utils.battle import calculate_damage, add_experience, encounter_enemies, add_drops

app = Flask(__name__)
app.secret_key = "your_secret_key"

global player
player = {}

SHOP_ITEMS = [
    {"name": "Iron Sword", "ATK": 5.0, "cost": 50, "type": "weapon"},
    {"name": "Health Potion", "heal": 0.5, "cost": 30, "type": "item"},
]


@app.route("/merchant/buy_items")
def merchant_buy_items():
    """Return the list of items available for purchase."""
    return jsonify(SHOP_ITEMS)


@app.route("/merchant/buy", methods=["POST"])
def merchant_buy():
    player = load_player()
    item_index = request.form.get("item_index")
    try:
        idx = int(item_index) - 1
        if idx < 0 or idx >= len(SHOP_ITEMS):
            return jsonify({"error": "Invalid item selection."}), 400
        selected = SHOP_ITEMS[idx]
        if player["gold"] >= selected["cost"]:
            player["gold"] -= selected["cost"]
            if selected["type"] == "weapon":
                player["inventory"]["weapons"].append(
                    {"name": selected["name"], "ATK": selected["ATK"]}
                )
            elif selected["type"] == "item":
                player["inventory"]["items"].append({"name": selected["name"]})
            save_player(player)
            return jsonify({"message": f"Purchased {selected['name']}!"})
        else:
            return jsonify({"error": "Not enough gold!"}), 400
    except ValueError:
        return jsonify({"error": "Invalid input."}), 400


@app.route("/merchant/sell", methods=["POST"])
def merchant_sell():
    player = load_player()
    sell_type = request.form.get("sell_type")  # expects 'weapon' or 'item'
    item_index = request.form.get("item_index")
    if sell_type not in ["weapon", "item"]:
        return jsonify({"error": "Invalid sell type."}), 400
    try:
        idx = int(item_index) - 1
        if sell_type == "weapon":
            items = player["inventory"]["weapons"]
            if idx < 0 or idx >= len(items):
                return jsonify({"error": "Invalid selection."}), 400
            sold_item = items.pop(idx)
            player["gold"] += 10  # fixed sell price for weapons
            save_player(player)
            return jsonify({"message": f"Sold {sold_item['name']} for 10 gold."})
        elif sell_type == "item":
            items = player["inventory"]["items"]
            if idx < 0 or idx >= len(items):
                return jsonify({"error": "Invalid selection."}), 400
            sold_item = items.pop(idx)
            player["gold"] += 5  # fixed sell price for items
            save_player(player)
            return jsonify({"message": f"Sold {sold_item['name']} for 5 gold."})
    except ValueError:
        return jsonify({"error": "Invalid input."}), 400


@app.route("/")
def home():
    player = load_player()
    return render_template("game/home.html", player=player)


@app.route("/start", methods=["GET", "POST"])
def start():
    player = load_player()

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
    world = load_world()

    if player is None:
        return redirect(url_for("start"))

    if not player["HP"] > 0:
        return render_template("game/game_over.html")

    # reset current battle state to empty everytime were back at game.html
    world["current_battle"] = {}
    save_world(world)

    return render_template("game/game.html", player=player)


@app.route("/reset-game", methods=["POST", "GET"])
def reset_game():
    try:
        # Delete save files if they exist
        if os.path.exists("player_save.json"):
            os.remove("player_save.json")
        if os.path.exists("world_save.json"):
            os.remove("world_save.json")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/explore")
def explore():
    location = request.args.get("location", None)
    enemy = None

    player = load_player()
    world_state = load_world()

    if location not in ["Forest", "Cave", "Swamp", "Mountains"]:
        return redirect(url_for("game/game.html", player=player))

    # encounter enemy only if you haven't cleared the area
    enemy = encounter_enemies(location, world_state)
    print(enemy)

    # added back the 30% chance of encountering an enemy
    if random.random() < 0.3:
        if enemy is not None:
            world_state["current_battle"] = {"enemy": enemy, "area": location}
            save_world(world_state)
            return redirect(url_for("battle", location=location, enemy=enemy))

    # image for location
    location_image = f"images/{location.lower()}.webp"

    # if enemy is none meaning area is cleared
    if enemy is None:
        return render_template(
            "game/explore.html",
            player=player,
            location=location,
            cleared_area=True,
            location_image=location_image,
        )

    # if location not in defeated_enemies meaning location has not been visited then we init it with an empty defeated enemy list
    if location not in world_state["defeated_enemies"]:
        world_state["defeated_enemies"][location] = []

    return render_template(
        "game/explore.html",
        player=player,
        location=location,
        cleared_area=False,
        location_image=location_image,
    )


@app.route("/sleep", methods=["POST"])
def sleep():
    player = load_player()

    if int(player["HP"]) == int(player["MAX_HP"]):
        return jsonify(
            {
                "message": "HP is Full, Cannot Sleep!",
                "healed": 0,
                "current_hp": player["HP"],
                "max_hp": player["MAX_HP"],
            }
        )

    heal_amount = player["MAX_HP"] * 0.05
    old_hp = player["HP"]
    player["HP"] = int(round(min(player["HP"] + heal_amount, player["MAX_HP"])))
    healed = player["HP"] - old_hp

    save_player(player)

    return jsonify(
        {
            "message": "You slept and restored some HP",
            "healed": round(healed, 1),
            "current_hp": round(player["HP"], 1),
            "max_hp": round(player["MAX_HP"], 1),
        }
    )


# -------------------------------------------
# ... BATTLE ENDPOINTS ......................
# --------------------------------------------
@app.route("/battle")
def battle():
    location = request.args.get("location", None)
    player = load_player()
    enemy = None
    
    if location:
        world_state = load_world()
        if location not in world_state["defeated_enemies"]:
            world_state["defeated_enemies"][location] = []

        # Use the enemy from current_battle if it exists
        current_battle = world_state.get("current_battle", {})
        if current_battle and current_battle.get("area") == location:
            enemy = current_battle.get("enemy")
        else:
            enemy = encounter_enemies(location, world_state)
            if enemy:
                world_state["current_battle"] = {"enemy": enemy, "area": location}
                save_world(world_state)

    return render_template("game/battle.html", location=location, enemy=enemy, player=player)


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
    raw_damage, damage_reduction, final_damage = calculate_damage(
        player, enemy, weapon_bonus
    )
    enemy["HP"] -= final_damage
    message = f"You attacked {enemy['name']} for {final_damage} damage!"

    # Handle enemy defeat
    if enemy["HP"] <= 0:
        enemy["HP"] = 0  # Ensure enemy HP does not go negative
        message += f" {enemy['name']} is defeated!"
        update_world_state(world_state, area, enemy["name"])
        
        # Add drop logic
        add_drops(player, enemy)

        add_experience(player, enemy["EXP_DROP"])
        
        # Save progress
        save_world(world_state)
        save_player(player)

        # Remove enemy from battle state
        world_state.pop("current_battle", None)

        return jsonify(
            {
                "message": message,
                "battle_over": True,  # Mark battle as over
                "player": player,
                "enemy": enemy,
            }
        )

    # Process enemy counter-attack
    raw_damage, damage_reduction, final_damage = calculate_damage(enemy, player)
    player["HP"] -= final_damage
    message += f" {enemy['name']} counterattacked for {final_damage:.1f} damage!"

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

    temp_def_bonus = int(player["DEF"] * 0.5)  # Convert to integer
    player["DEF"] += temp_def_bonus
    message = "You brace yourself and boost your defense! "

    # Enemy attacks while you are defending
    raw_damage, damage_reduction, final_damage = calculate_damage(enemy, player)
    final_damage = int(final_damage)
    player["HP"] -= final_damage
    message += f"{enemy['name']} attacked for {final_damage} damage! "

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
    raw_damage, damage_reduction, final_damage = calculate_damage(enemy, player)
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
                "MAX_HP": player.get("MAX_HP"),
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
            heal_amount = int(player["MAX_HP"] * item["heal"])  # Convert to integer
            heal_amount = int(player["MAX_HP"] * item["heal"])
            old_hp = player["HP"]
            player["HP"] = min(player["HP"] + heal_amount, player["MAX_HP"])
            player["HP"] = min(player["HP"] + heal_amount, player["MAX_HP"])
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
