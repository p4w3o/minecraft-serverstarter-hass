import json

def load_config(path="/data/options.json"):
    with open(path, "r") as f:
        return json.load(f)
