# Lanes

Each lane lane can lay, under the action it watches. The sentence is what the step says and what
the subagent is told on a drift, with what the lane takes put in where it shows `<...>`; the hook
tells it when the subagent does what the last column says.

## begin

| Lane | Sentence | Told when the subagent |
|---|---|---|
| start_with | First run `<script>`. | begins with anything else |

## read

| Lane | Sentence | Told when the subagent |
|---|---|---|
| read_only | Read only `<input>`. | reads anything else |
| read_whole | Read `<input>` to its end. | leaves a part of it unread |

## write

| Lane | Sentence | Told when the subagent |
|---|---|---|
| write_only | Write only `<output>`. | writes anything else |
| in_form | Write `<output>` in `<form>`. | writes it out of that form |

## run

| Lane | Sentence | Told when the subagent |
|---|---|---|
| hands_off | Do not run `<commands>`. | runs one of them |

## test

| Lane | Sentence | Told when the subagent |
|---|---|---|
| test_after | After changing `<output>`, pass `<test>`. | goes on with a change not yet passed |

## hand on

| Lane | Sentence | Told when the subagent |
|---|---|---|
| as_printed | Hand on `<input>` as it is. | hands on something else |
| follow_next | Take the next move `<script>` printed. | takes another move |

## wait

| Lane | Sentence | Told when the subagent |
|---|---|---|
| wait_for | Do not go on until `<approval>`. | goes on without it |

## end

| Lane | Sentence | Told when the subagent |
|---|---|---|
| end_when | End only once `<output>` is made. | ends before |
| every_item | Answer every item of `<input>`. | leaves an item unanswered |
