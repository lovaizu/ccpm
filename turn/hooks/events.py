"""The checks each entry of turn's hooks runs, in the order they run."""

from checks import (
    call_given,
    no_commit,
    read_in_given,
    read_whole,
    role_given,
    role_reply,
    run_returned,
    start_as_called,
    write_work_alone,
)

PRETOOLUSE = (
    call_given,
    start_as_called,
    role_given,
    write_work_alone,
    no_commit,
    read_in_given,
    read_whole,
    role_reply,
    run_returned,
)
SUBAGENTSTOP = (read_whole, role_reply, run_returned)
