import json
def load_module_config(module):
    print(f"Loading config file for {module}")
    with open(f"configs/{module}.json", "r") as f:
        return json.loads(f.read())