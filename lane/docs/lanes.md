# lane's lanes

Each lane lane can lay, under the action it watches, so you can tell what `lane:up` proposes for
your plugin's steps and what each hook tells your subagent.

The sentence is what the step says and what the subagent is told on a drift, with what the lane
takes put in where it shows `<...>`; the hook tells it when the subagent does what the last column
says.

What a lane takes is fixed in the step, such as `CHANGELOG.md`, or given for each run, written
`{<name>}`: the value under that name in the JSON the subagent starts from, its prompt or what the
script it first runs prints. Write only `{work}`. holds a subagent to the files its run's `work`
names, whichever they are.

| Action | Lane | Sentence | Told when the subagent |
|---|---|---|---|
| begin | start_with | First run `<script>`. | begins with anything else |
| read | read_only | Read only `<input>`. | reads anything else |
| read | read_whole | Read `<input>` to its end. | leaves a part of it unread |
| write | write_only | Write only `<output>`. | writes anything else |
| write | in_form | Write `<output>` in the form of `<form>`. | writes it out of that form |
| run | hands_off | Do not run `<commands>`. | runs one of them |
| test | test_after | After changing `<output>`, pass `<test>`. | goes on with a change not yet passed |
| hand on | as_printed | Hand on `<input>` as it is. | hands on something else |
| hand on | follow_next | Take the next move `<script>` printed. | takes another move |
| wait | wait_for | Do not go on until `<approval>`. | goes on without it |
| end | end_when | End only once `<output>` is made. | ends before |
| end | every_item | Answer every item of `<input>`. | leaves an item unanswered |

read_only lets the subagent read, beside its inputs, the form each of its in_form lanes names: its
step tells it to write in that form, and the form, a file of your plugin, holds nothing of the
project's work.

follow_next reads the next move your script prints as the tool call itself, one JSON line
`{"tool": ..., "input": {...}}` last in its output; a script printing its move in a form of its own
gets no follow_next.
