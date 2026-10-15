"""The content file's place in the session folder, and the task written as a CCS for turn."""

import json
import os


def content_file(session, document):
    path = os.path.normpath(document)
    if os.path.isabs(path) or path.split(os.sep)[0] == "..":
        raise ValueError(f"{document} is outside the repository; name a path from its top")
    return os.path.join(session, "content", os.path.splitext(path)[0] + ".content.md")


def write(args):
    for path in args.checklist + [args.content] + args.reference + args.opens:
        if not os.path.exists(path):
            raise ValueError(
                f"{path} does not exist; name it by its path from the top of the repository"
            )
    ccs = {
        "focal_entities": [{"deliverable": path} for path in args.deliverable]
        + [{"receiver": args.receiver}],
        "goal_orientation": ([{"use": args.use}] if args.use else [])
        + [{"acceptance": args.acceptance}],
        "retrieved_artifacts": [{"checklist": path} for path in args.checklist]
        + [{"content": args.content}]
        + [{"reference": path} for path in args.reference]
        + [{"receiver_opens": path} for path in args.opens],
        "constraints": [{"language": args.language}] if args.language else [],
        "predictive_cue": [],
        "uncertainty_signal": [],
        "semantic_gist": [],
        "relational_map": [],
        "episodic_trace": [],
    }
    folder = os.path.join(args.session, "tasks")
    os.makedirs(folder, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.deliverable[0]))[0]
    n = 1
    while os.path.exists(os.path.join(folder, f"{stem}-{n}.json")):
        n += 1
    path = os.path.join(folder, f"{stem}-{n}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(ccs, indent=1, ensure_ascii=False) + "\n")
    return f"in: {path}\nout: {os.path.join(folder, f'{stem}-{n}.back.json')}"
