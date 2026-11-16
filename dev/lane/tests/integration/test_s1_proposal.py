"""The integration cases of S1, a proposal: up, lay.py, and the lane types joined through the double
of Claude Code, on each path of S1's sequence, each kind of data it hands on, and each decision of
lay.py that it shows."""

from __future__ import annotations

import glob
import json
import os

import pytest
import walkthrough as w
from claude_code import Conversation


def propose_part(b: w.Bench, c: Conversation) -> dict:
    """The person types /lane:up changelog, and up reads the types; gives what lay.py types gave."""
    called = c.type("/lane:up changelog")
    assert not called.blocked, called.said
    return w.types(b, c)


def up_reads(b: w.Bench, c: Conversation) -> dict:
    """The person types /lane:up changelog, and up reads the types and the Steps; gives the
    walkthrough's Proposal, for the case to change before up hands it to lay.py print."""
    propose_part(b, c)
    assert c.bash(b.lay_py("steps", "changelog")).exit_code == 0
    return w.walkthrough_proposal()


@pytest.mark.supports("S1", "Lane type", "lane types")
def test_types_give_each_lane_type_and_the_form_of_a_proposal(b: w.Bench) -> None:
    """Given: Lane's copy, whose lanes/ holds each lane type.
    When: up runs lay.py types.
    Then: it gives each lane type the README and S2 name, each with its sentence, the steps it
    suits, what it allows, and each value it takes by the name its module's ARGS gives, and the
    Proposal's form from lanes.schema.json."""
    c = w.converse(b)
    given = propose_part(b, c)
    args = {each["name"]: set(each["args"]) for each in given["types"]}
    assert args["routes"] == args["ends_by_result"] == set()
    assert args["gives_shown"] == args["lays_after_reply"] == set()
    assert (args["run_only"], args["write_only"]) == ({"commands"}, {"paths"})
    assert args["ends_checked"] == {"command"}
    for each in given["types"]:
        assert set(each) == {"name", "sentence", "suits", "allows", "args"}
        assert each["sentence"] and each["suits"] and each["allows"]
    path = os.path.join(b.lane, "hooks", "lane", "domain", "lanes.schema.json")
    with open(path, encoding="utf-8") as f:
        schema = json.load(f)
    assert given["proposal"]["properties"] == schema["definitions"]["proposal"]["properties"]


@pytest.mark.supports("S1", "Step", "Role", "lay.py")
def test_steps_give_each_step_of_each_role(b: w.Bench) -> None:
    """Given: changelog as the walkthrough gives it, with no Lane laid.
    When: up runs lay.py steps changelog.
    Then: it gives each Step of write, writer, and reviewer by its file and number, its text as
    written, and no notes."""
    c = w.converse(b)
    propose_part(b, c)
    ran = c.bash(b.lay_py("steps", "changelog"))
    assert ran.exit_code == 0
    given = json.loads(ran.output)
    steps = {(s["role"], s["file"], s["number"]): s["text"] for s in given["steps"]}
    assert steps[("write", "skills/write/SKILL.md", 1)] == "Have the entries written and reviewed."
    assert steps[("writer", "agents/writer.md", 2)] == (
        "Read the commits since then with `git log --oneline`."
    )
    assert steps[("reviewer", "agents/reviewer.md", 3)].startswith("Give `more`")
    assert len(steps) == 8
    assert given["notes"] == []


@pytest.mark.supports("S1", "lay.py")
def test_a_proposal_that_cant_stand_goes_back_to_up(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal with a Lane of a type that no lane type has.
    When: up hands it to lay.py print.
    Then: lay.py print exits 1, naming the Lane, keeps no Proposal, and shows no ID."""
    c = w.converse(b)
    proposal = up_reads(b, c)
    proposal["lanes"][2]["type"] = "run_once"
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 1
    assert "run_once" in printed.output
    assert "ID:" not in printed.output
    # lane/ holds up's own run record too, as Lane is the plugin of up's Run.
    assert not glob.glob(os.path.join(b.env["TMPDIR"], "lane", "*-changelog")), "no Proposal kept"


@pytest.mark.supports("S1", "lay.py")
def test_a_lane_on_a_step_that_isnt_there_goes_back_to_up(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal with a Lane on writer's step 9, which agents/writer.md
    doesn't hold.
    When: up hands it to lay.py print.
    Then: lay.py print exits 1, naming the Step."""
    c = w.converse(b)
    proposal = up_reads(b, c)
    proposal["lanes"][2]["step"] = 9
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 1
    assert "agents/writer.md" in printed.output and "9" in printed.output


@pytest.mark.supports("S1", "lay.py", "Lane")
def test_a_role_with_no_end_on_its_last_step_goes_back_to_up(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal without reviewer's Lane of ends_by_result on its step 2,
    though a Route starts reviewer.
    When: up hands it to lay.py print.
    Then: lay.py print exits 1, naming reviewer and ends_by_result, and shows no ID."""
    c = w.converse(b)
    proposal = up_reads(b, c)
    proposal["lanes"] = [x for x in proposal["lanes"] if x["role"] != "reviewer"]
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 1
    assert "reviewer" in printed.output and "ends_by_result" in printed.output
    assert "ID:" not in printed.output


@pytest.mark.supports("S1", "lay.py", "Lane")
def test_a_skill_with_no_end_on_its_last_step_goes_back_to_up(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal without write's Lane of ends_by_result on its step 1.
    When: up hands it to lay.py print.
    Then: lay.py print exits 1, naming write and ends_by_result."""
    c = w.converse(b)
    proposal = up_reads(b, c)
    proposal["lanes"] = [
        x for x in proposal["lanes"] if (x["role"], x["type"]) != ("write", "ends_by_result")
    ]
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 1
    assert "write" in printed.output and "ends_by_result" in printed.output


@pytest.mark.supports("S1", "lay.py", "user")
def test_a_file_that_cant_carry_the_proposal_goes_to_the_user(tmp_path: object) -> None:
    """Given: changelog whose agents/reviewer.md doesn't set `background: true`.
    When: up hands the walkthrough's Proposal to lay.py print.
    Then: lay.py print exits 3, naming agents/reviewer.md and what to fix in it."""
    files = dict(w.FILES, **{"agents/reviewer.md": w.REVIEWER.replace("background: true\n", "")})
    b = w.bench(str(tmp_path), files)
    c = w.converse(b)
    printed = w.print_proposal(b, c, up_reads(b, c))
    assert printed.exit_code == 3
    assert "agents/reviewer.md" in printed.output and "background: true" in printed.output


@pytest.mark.supports("S1", "lay.py")
def test_a_route_command_the_model_may_call_goes_to_the_user(tmp_path: object) -> None:
    """Given: changelog with a command skill approve, which a Route waits for, whose SKILL.md
    doesn't set `disable-model-invocation: true`.
    When: up hands lay.py print the walkthrough's Proposal with reviewer's `good` waiting for
    approve.
    Then: lay.py print exits 3, naming skills/approve/SKILL.md."""
    approve = "---\nname: approve\ndescription: Approves the entries.\n---\n\n## Steps\n\n1. Go.\n"
    b = w.bench(str(tmp_path), dict(w.FILES, **{"skills/approve/SKILL.md": approve}))
    c = w.converse(b)
    proposal = up_reads(b, c)
    proposal["routes"][3]["moves"] = [{"wait": "approve"}]
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 3
    assert "skills/approve/SKILL.md" in printed.output


@pytest.mark.supports("S1", "lay.py")
def test_an_adapter_the_proposal_doesnt_name_goes_to_the_user(tmp_path: object) -> None:
    """Given: changelog whose hooks/adapters/ holds text.py.
    When: up hands lay.py print the walkthrough's Proposal, which names no adapter.
    Then: lay.py print exits 3, naming hooks/adapters/text.py."""
    adapter = {"hooks/adapters/text.py": "print('{}')\n"}
    b = w.bench(str(tmp_path), dict(w.FILES, **adapter))
    c = w.converse(b)
    printed = w.print_proposal(b, c, up_reads(b, c))
    assert printed.exit_code == 3
    assert "hooks/adapters/text.py" in printed.output


@pytest.mark.supports("S1", "lay.py")
def test_a_steps_file_two_roles_share_goes_to_the_user(tmp_path: object) -> None:
    """Given: changelog whose writer and reviewer both name steps.md by `${CLAUDE_PLUGIN_ROOT}/` as
    the file of their Steps.
    When: up hands lay.py print the walkthrough's Proposal.
    Then: lay.py print exits 3, naming steps.md."""
    body = "Your steps are in `${CLAUDE_PLUGIN_ROOT}/steps.md`.\n"
    writer = w.WRITER.split("## Steps")[0] + body
    reviewer = w.REVIEWER.split("## Steps")[0] + body
    files = dict(w.FILES, **{"agents/writer.md": writer, "agents/reviewer.md": reviewer})
    files["steps.md"] = "## Steps\n\n1. Read.\n2. Write.\n3. Reply.\n4. End.\n"
    b = w.bench(str(tmp_path), files)
    c = w.converse(b)
    printed = w.print_proposal(b, c, up_reads(b, c))
    assert printed.exit_code == 3
    assert "steps.md" in printed.output


@pytest.mark.supports("S1", "lay.py")
def test_a_route_after_a_command_the_model_may_call_goes_to_the_user(tmp_path: object) -> None:
    """Given: changelog with a command skill pause, which a Route goes after, whose SKILL.md
    doesn't set `disable-model-invocation: true`.
    When: up hands lay.py print the walkthrough's Proposal with a Route of write after pause that
    starts no more.
    Then: lay.py print exits 3, naming skills/pause/SKILL.md."""
    pause = "---\nname: pause\ndescription: Pauses the run.\n---\n\n## Steps\n\n1. Stop.\n"
    b = w.bench(str(tmp_path), dict(w.FILES, **{"skills/pause/SKILL.md": pause}))
    c = w.converse(b)
    proposal = up_reads(b, c)
    after = {"skill": "write", "after": {"command": "pause"}, "moves": [{"no_more": "paused"}]}
    proposal["routes"].append(after)
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 3
    assert "skills/pause/SKILL.md" in printed.output


@pytest.mark.supports("S1", "Step", "lay.py")
def test_a_steps_file_a_skill_and_its_command_share_is_the_skills(tmp_path: object) -> None:
    """Given: changelog whose skill write and command approve, which write's Route waits for, both
    name write-steps.md by `${CLAUDE_PLUGIN_ROOT}/` as the file of their Steps.
    When: up hands lay.py print the walkthrough's Proposal with write's Lanes on write-steps.md,
    reviewer's `good` waiting for approve, and a Route after approve that starts no more.
    Then: lay.py print exits 0, shows the Route after approve as the person typing it, and shows
    write-steps.md's step 1 once, under write's Routes."""
    body = "Your steps are in `${CLAUDE_PLUGIN_ROOT}/write-steps.md`.\n"
    write = w.WRITE.split("## Steps")[0] + body
    front = "---\nname: approve\ndescription: A.\ndisable-model-invocation: true\n---\n\n"
    files = dict(
        w.FILES, **{"skills/write/SKILL.md": write, "skills/approve/SKILL.md": front + body}
    )
    files["write-steps.md"] = "## Steps\n\n1. Have the entries written and reviewed.\n"
    b = w.bench(str(tmp_path), files)
    c = w.converse(b)
    proposal = up_reads(b, c)
    for lane in proposal["lanes"][:2]:
        lane["file"] = "write-steps.md"
    proposal["routes"][3]["moves"] = [{"wait": "approve"}]
    after = {"skill": "write", "after": {"command": "approve"}, "moves": [{"no_more": "good"}]}
    proposal["routes"].append(after)
    printed = w.print_proposal(b, c, proposal)
    assert printed.exit_code == 0, printed.output
    routes = printed.output.split("\n\n")[0].split("\n")
    assert routes[-1] == "  the person types approve  start no more", "the Route after approve"
    write_block = printed.output.split("\n\n")[1]
    assert write_block.startswith("1. Have the entries written and reviewed."), "write's step 1"
    assert printed.output.count("Have the entries written and reviewed.") == 1, "shown once"


@pytest.mark.supports("S1", "guard", "Run")
def test_what_print_showed_is_kept_in_ups_run(b: w.Bench) -> None:
    """Given: the person typed /lane:up changelog.
    When: lay.py print shows the walkthrough's Proposal, and its PostToolUse reaches the guard.
    Then: up's Run, called by a person, holds what lay.py print showed with the Proposal's ID."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    run = next(r for r in w.where(b.lane, b, c.session_id).runs if r.skill == "up")
    assert run.by == "person"
    assert run.shown[-1].proposal_id == pid
    assert run.shown[-1].words.rstrip("\n") == printed.output.rstrip("\n")
