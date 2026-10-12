import json, re, subprocess, sys
# Usage: python3 check_form.py <form.json> <checklist>...
form = json.load(open(sys.argv[1]))
ids = [i["id"] for i in json.loads(subprocess.run(
    [sys.executable, __file__.replace("check_form.py", "make_list.py"), *sys.argv[2:]],
    capture_output=True, text=True, check=True).stdout)["items"]]
lines = len(open(form["document"]).read().split("\n"))
got = {e["id"]: e for e in form["items"]}
bad = [f"{i}: not filled" for i in ids if i not in got]
bad += [f"{i}: not in the list" for i in got if i not in ids]
for i, e in got.items():
    if not isinstance(e.get("met"), bool) or not e.get("note"):
        bad.append(f"{i}: met or note missing")
    for a, b in re.findall(r"(\d+)(?:-(\d+))?", e.get("lines", "")) or [("0", "")]:
        if not 1 <= int(a) <= int(b or a) <= lines:
            bad.append(f"{i}: lines {e.get('lines')!r} not in the document")
bad += [f"{i}: not met" for i, e in got.items() if e.get("met") is False]
print("\n".join(bad) or f"all {len(ids)} items filled and met")
sys.exit(1 if bad else 0)
