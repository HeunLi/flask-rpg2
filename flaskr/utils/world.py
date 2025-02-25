import json


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


def load_player(filename="player_save.json"):
    """Load player data from a JSON file."""
    try:
        with open(filename, "r") as f:
            player = json.load(f)
        # Ensure the player has a gold key, add default if missing.
        if "gold" not in player:
            player["gold"] = 100  # or another default value
        print("\nPlayer progress loaded successfully!")
        return player
    except FileNotFoundError:
        print("\nNo saved player data found. Starting new game...")
        return None
    except Exception as e:
        print(f"\nError loading player progress: {e}")
        return None


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


def load_world(filename="world_save.json"):
    """Load world progress from a JSON file."""
    try:
        with open(filename, "r") as f:
            world_state = json.load(f)
        print("World progress loaded successfully!")
        return world_state
    except FileNotFoundError:
        # Initialize new world state
        return {
            "defeated_enemies": {},  # Format: {"area": ["enemy1", "enemy2", ...]}
            "visited_areas": [],
        }
    except Exception as e:
        print(f"Error loading world progress: {e}")
        return None


def update_world_state(world_state, area, enemy_name):
    """Update world state when an enemy is defeated."""
    if area not in world_state["defeated_enemies"]:
        world_state["defeated_enemies"][area] = []
    world_state["defeated_enemies"][area].append(enemy_name)

    if area not in world_state["visited_areas"]:
        world_state["visited_areas"].append(area)
