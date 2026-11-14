# The report of a check of the code that fails, sourced by check.sh and quality.sh: it says what
# the check is for, before the findings and again in short after them, so that whoever mends the
# code, a person, the developer's subagent, or ci-fix.sh's, changes the design for its maintainer
# and doesn't only change the code until the finding goes away. The prose checks of
# lovaizu/repofiles report the same way, as an agent given no such text swapped the words of each
# finding, and one given it rewrote most of them from the facts, as Issue #17 of lovaizu/checks
# found.

# Runs the command after $1 and, where it fails, prints its output between the text of the kind $1:
# design, for a check of how the code is laid out, or tests, for a check of how well the tests
# catch faults. It gives the command's exit code.
held() {
  kind=$1
  shift
  out=$("$@" 2>&1) && {
    [ -z "$out" ] || printf '%s\n' "$out"
    return 0
  }
  code=$?
  case "$kind" in
    design)
      cat <<'EOF'
The checks found code that its maintainer may find hard to change. Each finding
marks a design to rethink, not a number to lower. Find the decision held in the
wrong place, or the function that does more than one thing, as
plugins/rn/domain/best-practices/refactor-code/best-practice.md asks, and change
the design there. Keep every behavior. Don't split a function, pack arguments,
add noqa or a type ignore, or raise a limit only to clear a finding: code that
clears it and reads worse is worse than the finding.

EOF
      ;;
    tests)
      cat <<'EOF'
The checks found code that the tests may let break unseen. Each finding marks a
design to rethink, not a test to add. First ask whether the part needs the code,
and remove what no case of the tests calls for, as
plugins/rn/domain/best-practices/code/best-practice.md says of the faults that
the tests catch. Tighten a test only for a case that the tests already name. A
new case goes back to the design of the test cases, never into a test written
to clear a finding.

EOF
      ;;
  esac
  printf '%s\n\n' "$out"
  case "$kind" in
    design)
      echo "Change the design for its maintainer. Don't change code only to clear a finding."
      ;;
    tests)
      echo "Mend the design or the code. Don't add a test only to clear a finding."
      ;;
  esac
  return "$code"
}
