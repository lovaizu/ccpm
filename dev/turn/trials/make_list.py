import json, re, sys
lists, items = [], []
for path in sys.argv[1:]:
    name = path.rsplit("/", 1)[1][:-3]
    opening, cur, fence, seen = "", None, False, False
    for line in open(path):
        if line.startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"(#{1,3}) (?:([BUF]-\d+): )?(.+)", line)
        if m:
            if m.group(1) == "##":
                seen = True
            cur = None
            if m.group(2):
                cur = {"id": f"{name} {m.group(2)}", "title": m.group(3).strip(), "text": ""}
                items.append(cur)
        elif cur is not None:
            cur["text"] += line
        elif not seen:
            opening += line
    lists.append({"checklist": name, "opening": opening.strip()})
for i in items:
    i["text"] = i["text"].strip()
print(json.dumps({"checklists": lists, "items": items}, indent=1, ensure_ascii=False))
