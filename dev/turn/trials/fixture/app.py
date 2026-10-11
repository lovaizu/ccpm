"""The tasks app: lists the tasks kept in var/tasks.json."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "var", "tasks.json")

if not os.environ.get("TASKS_API_TOKEN"):
    sys.exit("error: TASKS_API_TOKEN is not set")
if not os.path.exists(DATA):
    sys.exit(f"error: {DATA} not found")
with open(DATA) as f:
    tasks = json.load(f)
print(f"tasks app running: {len(tasks)} tasks")
