"""Each of rn's checks stops its breaking case and lets its passing case through.

Run from the plugin's parent directory: python3 -m unittest discover -s dev/tests/rn
"""
import json
import os
import re
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "rn")
CHECK = os.path.join(PLUGIN, "hooks", "check.py")

STEERING = """---
rn: 0.9.0
pr: https://github.com/you/repo/pull/1
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

A wrong type fails the build.

# Acceptance criteria

## Attractive quality

- A1: Code reproducing each bug fails the build

## Must-be quality

- M1: The app builds as before

# Assumptions

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
"""

VERIFICATION = """# verification

## Scenes

### A1: Code reproducing each bug fails the build

- A scene.

    Passes when it fails the build, and M1 holds.

## Machine checks
"""

SDIR = ".rn/20261003-typescript"


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.remote = os.path.join(self.tmp.name, "remote.git")
        self.dir = os.path.join(self.tmp.name, "work")
        self.data = os.path.join(self.tmp.name, "data")
        sh(self.tmp.name, "git", "init", "-q", "--bare", "-b", "main", self.remote)
        sh(self.tmp.name, "git", "clone", "-q", self.remote, self.dir)
        sh(self.dir, "git", "config", "user.name", "t")
        sh(self.dir, "git", "config", "user.email", "t@example.com")
        self.write("README.md", "app\n")
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", "init")
        sh(self.dir, "git", "push", "-qu", "origin", "main")
        sh(self.dir, "git", "remote", "set-head", "origin", "main")
        sh(self.dir, "git", "switch", "-qc", "session")
        self.write(f"{SDIR}/steering.md", STEERING)
        self.write("docs/verification.md", VERIFICATION)
        self.commit("rn: start\n\n● plan ── started → working out the plan")
        sh(self.dir, "git", "push", "-qu", "origin", "session")

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
        return p

    def commit(self, msg):
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", msg)

    def hook(self, event, **data):
        data.setdefault("cwd", self.dir)
        data.setdefault("session_id", "s1")
        env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data)
        r = subprocess.run(["python3", CHECK, event], input=json.dumps(data), cwd=self.dir,
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr

    def after_commit(self):
        return self.hook("post", tool_name="Bash", tool_input={"command": "git commit -F m"})


class Checks(unittest.TestCase):
    def setUp(self):
        self.r = Repo()

    def tearDown(self):
        self.r.tmp.cleanup()

    def post_write(self, rel):
        return self.r.hook("post", tool_name="Write",
                           tool_input={"file_path": os.path.join(self.r.dir, rel)})

    # Check 1
    def test_1_steering_form_passes(self):
        self.assertEqual(self.post_write(f"{SDIR}/steering.md")[0], 0)

    def test_1_bad_task_heading_stops(self):
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("### [ ] #2:", "### #2"))
        code, out = self.post_write(f"{SDIR}/steering.md")
        self.assertEqual(code, 2)
        self.assertIn("task heading", out)

    def test_1_repeated_task_id_stops(self):
        self.r.write(f"{SDIR}/steering.md", STEERING + "### [ ] #2: again\n")
        self.assertEqual(self.post_write(f"{SDIR}/steering.md")[0], 2)

    # Check 2
    def test_2_open_name_passes(self):
        self.r.write(f"{SDIR}/open/01-notes-design.md", "x\n")
        self.assertEqual(self.post_write(f"{SDIR}/open/01-notes-design.md")[0], 0)

    def test_2_open_bad_kind_stops(self):
        self.r.write(f"{SDIR}/open/01-evaluation-design.md", "x\n")
        code, out = self.post_write(f"{SDIR}/open/01-evaluation-design.md")
        self.assertEqual(code, 2)
        self.assertIn("01-evaluation-design.md", out)

    # Check 3
    def test_3_unknown_id_stops(self):
        self.r.write("docs/verification.md", VERIFICATION + "\n| a | A9 |\n")
        code, out = self.post_write("docs/verification.md")
        self.assertEqual(code, 2)
        self.assertIn("A9", out)

    def test_3_attractive_without_scene_stops(self):
        self.r.write("docs/verification.md", VERIFICATION.replace("### A1:", "### X:"))
        self.assertEqual(self.post_write("docs/verification.md")[0], 2)

    def test_3_criterion_without_task_stops_once_planned(self):
        st = STEERING + "### [ ] #3: move cart\n\nServes: A1\n"
        self.r.write(f"{SDIR}/steering.md", st)
        code, out = self.post_write(f"{SDIR}/steering.md")
        self.assertEqual(code, 2)
        self.assertIn("M1", out)
        self.r.write(f"{SDIR}/steering.md", st.replace("Serves: A1", "Serves: A1, M1"))
        self.assertEqual(self.post_write(f"{SDIR}/steering.md")[0], 0)

    # Check 4
    def test_4_decision_line_passes(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #3 cart ── decided: fix → #3 cart")
        self.assertEqual(self.r.after_commit()[0], 0)

    def test_4_decision_line_before_trailers_passes(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #3 cart ── decided: fix → #3 cart\n\n"
                      "Co-Authored-By: Claude <noreply@anthropic.com>")
        self.assertEqual(self.r.after_commit()[0], 0)

    def test_4_no_decision_line_stops(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a")
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("decision line", out)

    # Check 5
    def test_5_settled_item_whole_passes_and_cut_stops(self):
        body = "# Report\n\nDoing as written, the build failed at cart.ts:3.\n"
        self.r.write(f"{SDIR}/open/01-report-task-3.md", body)
        self.r.commit("rn: report\n\n● #3 cart ── report in → settle")
        os.remove(os.path.join(self.r.dir, SDIR, "open/01-report-task-3.md"))
        self.r.commit("rn: settle\n\n01-report-task-3.md:\n    # Report\n\n    Doing as written, the "
                      "build failed at cart.ts:3.\n\n● #3 cart ── purpose fulfilled → #4")
        self.assertEqual(self.r.after_commit()[0], 0)
        self.r.write(f"{SDIR}/open/02-report-task-4.md", body)
        self.r.commit("rn: report\n\n● #4 x ── report in → settle")
        os.remove(os.path.join(self.r.dir, SDIR, "open/02-report-task-4.md"))
        self.r.commit("rn: settle\n\n02-report-task-4.md: the build failed\n\n● #4 x ── done → #5")
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("02-report-task-4.md", out)

    # Check 6
    def test_6_sign_off_with_report_open_stops(self):
        self.r.write(f"{SDIR}/open/01-report-plan.md", "x\n")
        self.r.commit("rn: propose\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("01-report-plan.md", out)

    def test_6_sign_off_behind_default_branch_stops(self):
        sh(self.r.dir, "git", "switch", "-q", "main")
        self.r.write("b.txt", "b\n")
        self.r.commit("main moves")
        sh(self.r.dir, "git", "push", "-q", "origin", "main")
        sh(self.r.dir, "git", "switch", "-q", "session")
        self.r.write("c.txt", "c\n")
        self.r.commit("rn: propose\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("not merged", out)
        sh(self.r.dir, "git", "merge", "-q", "--no-edit", "origin/main")
        sh(self.r.dir, "git", "commit", "-q", "--allow-empty", "-m",
           "rn: propose\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        self.assertEqual(self.r.after_commit()[0], 0)

    def test_6_proposal_point_without_criterion_id_stops(self):
        body = ("rn: propose\n\n### What you get\n- Good A1: the build stops each bug, at a.ts:3\n"
                "- More: the key is unchecked, at b.ts:9\n\n"
                "● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        self.r.write("a.txt", "a\n")
        self.r.commit(body)
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("More: the key", out)
        sh(self.r.dir, "git", "commit", "-q", "--amend", "-m", body.replace("- More:", "- More M1:"))
        self.assertEqual(self.r.after_commit()[0], 0)

    # Check 7
    def test_7_sign_off_marked_without_ty_stops_and_with_ty_passes(self):
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("### [ ] #1:", "### [x] #1:"))
        self.r.commit("rn: approve\n\n● #1 Plan sign-off ── approved → #2 Design sign-off")
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("/rn:ty", out)
        self.r.hook("prompt", command_name="rn:ty")
        self.assertEqual(self.r.after_commit()[0], 0)

    def test_7_pause_without_dn_stops(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: pause\n\n● #3 cart ── half → paused at #3 cart")
        self.assertEqual(self.r.after_commit()[0], 2)

    def test_7_amending_a_typed_pause_passes_and_a_second_pause_stops(self):
        self.r.hook("prompt", command_name="rn:dn")
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: pause\n\n● #3 cart ── half → paused at #3 cart")
        self.assertEqual(self.r.after_commit()[0], 0)
        sh(self.r.dir, "git", "commit", "-q", "--amend", "-m",
           "rn: pause at #3\n\n● #3 cart ── half → paused at #3 cart")
        self.assertEqual(self.r.after_commit()[0], 0)
        self.r.write("b.txt", "b\n")
        self.r.commit("rn: pause\n\n● #3 cart ── more → paused at #3 cart")
        self.assertEqual(self.r.after_commit()[0], 2)

    def test_7_finishing_without_ty_stops_and_with_ty_passes(self):
        st = STEERING.replace("status: running", "status: finished") \
            .replace("### [ ] #1:", "### [x] #1:").replace("### [ ] #2:", "### [x] #2:")
        self.r.write(f"{SDIR}/steering.md", st)
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        code, out = self.r.after_commit()
        self.assertEqual(code, 2)
        self.assertIn("/rn:ty", out)
        self.r.hook("prompt", command_name="rn:ty")
        self.assertEqual(self.r.after_commit()[0], 0)

    # Checks 4–7 run between commit and push.
    def test_conductor_committing_and_pushing_in_one_command_stops(self):
        for cmd in ("git commit -m x && git push", "git commit -m x; git push -u origin session",
                    "git add -A\ngit commit -m x\ngit push"):
            code, out = self.r.hook("pre", tool_name="Bash", tool_input={"command": cmd})
            self.assertEqual(code, 2, cmd)
            self.assertIn("separate commands", out)
        for cmd in ("git commit -m x", "git push", "git add -A && git commit -F - <<'EOF'\n"
                    "rn: x\n\npush it later with git push\n\n● a ── b → c\nEOF"):
            self.assertEqual(self.r.hook("pre", tool_name="Bash", tool_input={"command": cmd})[0], 0,
                             cmd)

    # Check 12
    def test_12_conductor_starting_an_agent_in_the_background_stops(self):
        start = dict(tool_name="Agent", tool_input={"subagent_type": "rn:generator", "prompt": "x",
                                                    "run_in_background": True})
        code, out = self.r.hook("pre", **start)
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)
        start["tool_input"]["run_in_background"] = False
        self.assertEqual(self.r.hook("pre", **start)[0], 0)

    def test_12_conductor_continuing_an_agent_by_message_stops(self):
        code, out = self.r.hook("pre", tool_name="SendMessage",
                                tool_input={"to": "a1", "message": "carry on"})
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)

    # Check 8
    def test_8_unpushed_commit_blocks_stop(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        code, out = self.r.hook("stop")
        self.assertIn('"decision": "block"', out)
        sh(self.r.dir, "git", "push", "-q")
        code, out = self.r.hook("stop")
        self.assertEqual(out.strip(), "")

    def test_8_unpushed_commit_blocks_the_second_end_too(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        code, out = self.r.hook("stop", stop_hook_active=True)
        self.assertIn("not pushed", out)
        sh(self.r.dir, "git", "push", "-q")
        self.assertEqual(self.r.hook("stop", stop_hook_active=True)[1].strip(), "")

    def test_8_the_finishing_commit_must_be_pushed(self):
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("status: running", "status: finished"))
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        self.assertIn("not pushed", self.r.hook("stop")[1])
        sh(self.r.dir, "git", "push", "-q")
        self.assertEqual(self.r.hook("stop")[1].strip(), "")

    # Check 13
    def test_13_ending_a_turn_with_nothing_for_the_user_stops_once(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: agree\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        code, out = self.r.hook("stop")
        self.assertIn('"decision": "block"', out)
        self.assertIn("go on", out)
        code, out = self.r.hook("stop", stop_hook_active=True)
        self.assertEqual(out.strip(), "")

    def test_13_ending_a_turn_at_a_stop_or_a_question_passes(self):
        for line in ("● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off",
                     "● #1 Plan sign-off ── approved → #2 Design sign-off",
                     "● #3 cart ── half → paused at #3 cart"):
            self.r.write("a.txt", line + "\n")
            self.r.commit("rn: x\n\n" + line + "\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
            sh(self.r.dir, "git", "push", "-q")
            self.assertEqual(self.r.hook("stop")[1].strip(), "", line)
        self.r.write(f"{SDIR}/open/01-notes-question.md", "Which way?\n")
        self.r.commit("rn: ask\n\n● design ── question written → asking the user")
        sh(self.r.dir, "git", "push", "-q")
        self.assertEqual(self.r.hook("stop")[1].strip(), "")

    # Check 14
    def test_14_ending_a_turn_in_another_language_stops_even_the_second_time(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        sh(self.r.dir, "git", "push", "-q")
        english = "Which word should come before the code? I recommend A, since it matches the screen."
        for active in (False, True):
            code, out = self.r.hook("stop", last_assistant_message=english, stop_hook_active=active)
            self.assertIn('"decision": "block"', out)
            self.assertIn("Japanese", out)

    def test_14_ending_a_turn_in_the_conversation_language_passes(self):
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
        sh(self.r.dir, "git", "push", "-q")
        for text in ("`src/account` を TypeScript にすることで、何を得たいですか？ "
                     "推奨は A です。`DISPLAY_NAME_KEY` を設定しないとアプリは起動しません。",
                     "── typescript: 型の誤りがビルドで止まる ──\n✅ #1 Plan sign-off\n"
                     "👉 #2 Design sign-off ── PR で読んで /rn:ty で承認、/rn:gm で修正依頼\n\n"
                     "メールだけで登録したユーザーにも、ちゃんとした名前を出します。",
                     "OK"):
            self.assertEqual(self.r.hook("stop", last_assistant_message=text)[1].strip(), "", text)

    def test_14_text_quoted_from_the_record_does_not_count(self):
        st = STEERING.replace("### [ ] #2: Design sign-off",
                              "### [x] #2: Design sign-off\n### [ ] #3: Apply the discount before "
                              "the coupon\n\nServes: A1, M1")
        self.r.write(f"{SDIR}/steering.md", st)
        self.r.commit("rn: pause\n\n● #3 Apply the discount before the coupon ── half → paused at #3 "
                      "Apply the discount before the coupon")
        sh(self.r.dir, "git", "push", "-q")
        paused = ("── typescript: A wrong type fails the build. ──\n"
                  "✅ #1 Plan sign-off / #2 Design sign-off\n"
                  "👉 #3 Apply the discount before the coupon ── ここで一時停止\n\n"
                  "● #3 Apply the discount before the coupon ── half → paused at #3 Apply the discount "
                  "before the coupon\n\n次: /clear してから /rn:up")
        self.assertEqual(self.r.hook("stop", last_assistant_message=paused)[1].strip(), "")
        bullets = "前回の承認からの変更:\n" + "".join(
            f"- ● #{n} Apply the discount before the coupon ── half → paused at #{n} Apply the "
            "discount before the coupon\n" for n in range(3, 9)) + "確認してください。"
        self.assertEqual(self.r.hook("stop", last_assistant_message=bullets)[1].strip(), "")
        english = paused.replace("ここで一時停止", "paused here").replace(
            "次: /clear してから /rn:up", "Next: clear the conversation, then take it up again.")
        self.assertIn("Japanese", self.r.hook("stop", last_assistant_message=english)[1])

    # After a summary
    def test_after_compact_the_record_is_read_again(self):
        code, out = self.r.hook("compact", source="compact")
        self.assertEqual(code, 0)
        self.assertIn(f"{SDIR}/steering.md", out)
        self.assertIn("open/", out)
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        self.assertEqual(self.r.hook("compact", source="compact")[1].strip(), "")

    # Check 9
    def test_9_subagent_commit_stops(self):
        for agent in ("rn:generator", "rn:first-user", "general-purpose"):
            code, _ = self.r.hook("pre", agent_type=agent, tool_name="Bash",
                                  tool_input={"command": "git commit -m x"})
            self.assertEqual(code, 2, agent)
        code, _ = self.r.hook("pre", tool_name="Bash", tool_input={"command": "git commit -m x"})
        self.assertEqual(code, 0)

    def test_9_and_11_only_git_run_on_the_sessions_repository_counts(self):
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("rn:generator", "rn:first-user"):
            for cmd in (f"cd {clone} && git commit -qam try", f"git -C {clone} log -3",
                        "grep -rn 'git push' docs", "rg 'git log' README.md"):
                code, _ = self.r.hook("pre", agent_type=agent, agent_id="f3", tool_name="Bash",
                                      tool_input={"command": cmd})
                self.assertEqual(code, 0, (agent, cmd))
            for cmd in (f"cd {clone} && git log; cd {self.r.dir} && git commit -m x",
                        f"git -C {self.r.dir} commit -m x"):
                code, _ = self.r.hook("pre", agent_type=agent, agent_id="f3", tool_name="Bash",
                                      tool_input={"command": cmd})
                self.assertEqual(code, 2, (agent, cmd))

    # Check 10
    def test_10_first_user_writes_only_its_report(self):
        fu = dict(agent_type="rn:first-user", agent_id="f1", tool_name="Write")
        mine = os.path.join(self.r.dir, SDIR, "open/03-report-task-3.md")
        code, _ = self.r.hook("pre", tool_input={"file_path": os.path.join(self.r.dir, "src.ts")}, **fu)
        self.assertEqual(code, 2)
        self.assertEqual(self.r.hook("pre", tool_input={"file_path": mine}, **fu)[0], 0)
        self.assertEqual(self.r.hook("pre", tool_input={"file_path": mine}, **fu)[0], 0)
        other = os.path.join(self.r.dir, SDIR, "open/04-report-task-4.md")
        self.assertEqual(self.r.hook("pre", tool_input={"file_path": other}, **fu)[0], 2)

    # Check 11
    def test_11_first_user_reads_no_makers_account(self):
        fu = dict(agent_type="rn:first-user", agent_id="f2")
        notes = os.path.join(self.r.dir, SDIR, "open/01-notes-task-3.md")
        self.assertEqual(self.r.hook("pre", tool_name="Read", tool_input={"file_path": notes},
                                     **fu)[0], 2)
        self.assertEqual(self.r.hook("pre", tool_name="Bash", tool_input={"command": "git log -3"},
                                     **fu)[0], 2)
        for name in ("01-notes-question.md", "03-notes-proposal.md"):
            given = os.path.join(self.r.dir, SDIR, "open", name)
            self.assertEqual(self.r.hook("pre", tool_name="Read", tool_input={"file_path": given},
                                         **fu)[0], 0, name)
        readme = os.path.join(self.r.dir, "README.md")
        self.assertEqual(self.r.hook("pre", tool_name="Read", tool_input={"file_path": readme},
                                     **fu)[0], 0)

    # No session: nothing is checked.
    def test_no_session_passes(self):
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        self.assertEqual(self.r.hook("stop")[0], 0)
        self.assertEqual(self.r.after_commit()[0], 0)


class Agents(unittest.TestCase):
    def front(self, name):
        text = open(os.path.join(PLUGIN, "agents", name)).read()
        return text.split("---")[1]

    def test_first_user_skips_claude_md(self):
        self.assertRegex(self.front("first-user.md"), r"(?m)^omitClaudeMd: true$")

    def test_generator_has_no_agent_tool(self):
        self.assertRegex(self.front("generator.md"), r"(?m)^disallowedTools: .*\bAgent\b")


if __name__ == "__main__":
    unittest.main()
