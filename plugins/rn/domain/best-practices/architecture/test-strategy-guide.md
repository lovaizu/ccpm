# Test strategy guide

This guide is the base of the Test strategy of [the architecture best practice](best-practice.md).
It lists the test types that teams run, by the test target each tries. An architecture picks from
it only the types that its product's purpose needs, since a row for every type decides nothing.

Each type is a quality or a benchmark:

- A quality passes or fails by a criterion set before anyone writes a case. One that fails stops
  the change.
- A benchmark measures a value, and a person decides from it. It sets no criterion.

Each type names the sources that list it. The sources hold each type's full account, so this guide
links them and copies none:

- [SWEBOK](https://www.computer.org/education/bodies-of-knowledge/software-engineering/v4): the
  Guide to the Software Engineering Body of Knowledge v4.0, its knowledge area Software Testing.
- [CTFL](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/),
  [CTAL-TA](https://istqb.org/certifications/test-analyst),
  [CTAL-TTA](https://istqb.org/certifications/certified-tester-advanced-level-technical-test-analyst-ctal-tta/),
  [CT-AI](https://istqb.org/certifications/certified-tester-ai-testing-ct-ai/): the syllabi of the
  International Software Testing Qualifications Board (ISTQB) for the Foundation Level, the Test
  Analyst, the Technical Test Analyst, and AI Testing v2.0, with its
  [glossary](https://glossary.istqb.org) for each term.
- [Fintan](https://fintan.jp/page/1456/): the テスト種別カタログ (test type catalog) of TIS,
  under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Added: a type that teams run under its common name, which none of these lists.

## Rules for every test

- Regression\
  Every unit, integration, and end-to-end test runs again on each change, so that a change that
  breaks what worked shows at once. Regression testing, as SWEBOK and CTFL name it, is this rerun,
  not a type of its own.
- A prompt\
  A test whose path runs a prompt is a benchmark, as the model's result varies from run to run, and
  a criterion would pass or fail by chance. It runs each case several times and measures the share
  of runs that are right, or the precision and recall where the prompt picks items. It measures
  again on each new version of the model, as CT-AI's drift testing does.

## Parts

Unit tests try each part against its contract.

| Type | Kind | What it checks or measures | Recommended criterion | Sources |
|---|---|---|---|---|
| Unit testing | Quality | Each part against its contract. | Every case passes. | CTFL, CTAL-TA, Fintan |
| Static analysis | Quality | Faults found without running the code, such as types that don't fit, import cycles, copied code, and calls to an interface the project forbids. | 0 findings. | CTFL, CTAL-TTA, Fintan |
| Lint | Quality | The code against the project's coding rules and format. | 0 findings. | Fintan |
| Complexity analysis | Quality | Each function within limits on its complexity, such as its nesting, branches, returns, arguments, and statements. | Per function, cyclomatic complexity 10 as [NIST SP 500-235](https://www.nist.gov/publications/structured-testing-software-testing-methodology-using-cyclomatic-complexity-metric) recommends, cognitive complexity 15 as [SonarQube](https://docs.sonarsource.com/sonarqube-server/latest/user-guide/code-metrics/metrics-definition/) sets, and pylint's defaults of 6 returns, 12 branches, 5 arguments, and 50 statements at most. | CTAL-TTA, Fintan |
| Code coverage | Quality | The share of lines and branches that the tests run. | 100% of lines and branches. | CTFL, CTAL-TTA |
| Mutation testing | Quality | Whether the tests fail when a tool changes the code in small ways. | 0 surviving mutants. | Added |
| Property-based testing | Quality | Whether the code keeps a stated property over many inputs that a tool generates. | 0 counterexamples. | Added |
| Data compatibility testing | Quality | Whether the product reads the data that another program or another version writes. | Each kind of data that each earlier version writes reads without loss. | Fintan |

## Architecture

Integration tests try the parts joined against each element of the architecture.

| Type | Kind | What it checks or measures | Recommended criterion | Sources |
|---|---|---|---|---|
| Integration testing | Quality | The parts joined, against each element of the architecture, each interface between them and to a system outside among it. | Every case passes. | SWEBOK, CTFL, Fintan |
| Traceability | Quality | Whether each element of the architecture has a test, and each test names an element or a case one level up that exists. | Every element has a test, and every test names one that exists. | CTFL |
| Reliability and recovery testing | Quality | Whether the product keeps working through a fault, and comes back from it. | The product goes on from each fault that the architecture names, with no work lost. | CTAL-TTA, Fintan |
| Security testing | Quality | Whether someone can use the product in a way it must refuse, an instruction injected into a prompt's input among it. | Each use the product must refuse is refused. | SWEBOK, CTAL-TTA, CT-AI, Fintan |
| Privacy testing | Quality | Whether the product keeps personal data to the uses it allows. | No personal data reaches a use the product doesn't allow. | SWEBOK |
| Compatibility with a new version of what the product builds on | Quality | Whether the product still works on each new version of a thing outside it, such as its host, by running the steps of each recorded run again and comparing what the real thing gives with what its double gives, as [a contract test](https://martinfowler.com/bliki/ContractTest.html) does. | Each recorded step gives on the real thing what it gives on the double. | Added |

## Product

End-to-end (E2E) tests try the product in real use against each key result of the product vision.

| Type | Kind | What it checks or measures | Recommended criterion | Sources |
|---|---|---|---|---|
| Scenario testing | Quality | A user's whole task, through every part it crosses, from start to end, as the E2E test runs it. | Every case passes. | Fintan |
| Back-to-back testing | Quality | Whether the new version gives what the old one gave for the same input, where the change must keep what it does. | Each input gives the old version's result. | Fintan, CT-AI |
| Conformance and compliance testing | Quality | The product against a standard or a regulation that it must follow. | The standard's validator, or its checklist, finds 0 faults. | SWEBOK |
| Installation testing | Quality | Whether the product installs, updates, and uninstalls as its documentation says. | The documented commands install, update, and uninstall on a fresh system. | SWEBOK |
| Configuration testing | Quality | Each combination of system, runtime, and settings that the product supports. | Every case passes on each supported combination. | SWEBOK, Fintan |
| Migration testing | Quality | Whether the data and the work move from the old system to the new one, and back where the move fails. | All the data moves, and the move back restores the old system. | Fintan |
| Operation testing | Quality | Whether the operators' procedures, such as backup, monitoring, and logs, work. | Each procedure works as written. | Fintan |
| Performance testing | Benchmark | Under normal and peak load: how fast the product responds, how much it handles, and what it uses. | None | CTAL-TTA, Fintan |
| Stress testing | Benchmark | What the product does at and beyond the most load it can take. | None | Fintan |
| Volume testing | Benchmark | What the product does with its data at the size it grows to. | None | Fintan |
| Long-run testing | Benchmark | A fault that shows only after long running, such as a memory leak. | None | Fintan |
| Usability testing | Benchmark | Whether users reach their goal with ease, and whether every user can, accessibility among it. | None | SWEBOK, CTAL-TA, Fintan |
| Alpha and beta testing | Benchmark | What real users meet in their own use, first at the maker's site, then at their own. | None | SWEBOK |
