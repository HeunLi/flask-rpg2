from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"


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


@app.route("/")
def home():
    return render_template("game/home.html")


@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        # Retrieve form data
        player_name = request.form.get("player_name")
        player_class_choice = request.form.get("player_class")

        # Generate class-specific data
        player_class_data = get_class_data(player_class_choice)

        # Save both name and class data in session for persistence
        session["player_name"] = player_name
        session["player_class"] = player_class_data

        return redirect(url_for("game"))
    return render_template("game/start.html")


@app.route("/game")
def game():
    player_name = session.get("player_name", "Adventurer")
    player_class = session.get("player_class")
    return render_template(
        "game/game.html", player_name=player_name, player_class=player_class
    )


@app.route("/battle")
def battle():
    # Get the chosen location from the query string, e.g., /battle?location=Forest
    location = request.args.get("location", None)
    return render_template("game/battle.html", location=location)


if __name__ == "__main__":
    app.run(debug=True)
