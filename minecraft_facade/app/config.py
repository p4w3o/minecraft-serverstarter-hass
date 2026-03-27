import json

def load_config(path="/data/options.json"):
    with open(path) as f:
        return json.load(f)
