"""Creates var/tasks.json with the sample tasks."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(HERE, "var"), exist_ok=True)
with open(os.path.join(HERE, "var", "tasks.json"), "w") as f:
    json.dump([{"title": "Write the setup guide"}, {"title": "Review the API"}], f)
print("created var/tasks.json")
