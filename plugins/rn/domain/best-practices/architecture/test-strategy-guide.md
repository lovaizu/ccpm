# Test strategy guide

This guide is the base of the Test strategy of [the architecture best practice](best-practice.md).
It lists the checks that teams run, grouped by the test target they test. An architecture picks
only the checks that its product's purpose needs, since a row for every check decides nothing.

Each check runs as a quality or as a benchmark:

- A quality passes or fails by a criterion set before anyone writes a case. If it fails, the
  change stops.
- A benchmark measures a value, and a person decides from it. It has no criterion.

Each row says when to pick the check: always, or on a condition that the product meets.

Each row names the sources that list the check. The sources explain each check in full, so this
guide links them and copies nothing:

- [SWEBOK](https://www.computer.org/education/bodies-of-knowledge/software-engineering/v4): the
  Guide to the Software Engineering Body of Knowledge v4.0, its knowledge area Software Testing.
- [CTFL](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/),
  [CTAL-TA](https://istqb.org/certifications/test-analyst),
  [CTAL-TTA](https://istqb.org/certifications/certified-tester-advanced-level-technical-test-analyst-ctal-tta/),
  [CT-AI](https://istqb.org/certifications/certified-tester-ai-testing-ct-ai/): the syllabi of the
  International Software Testing Qualifications Board (ISTQB) for the Foundation Level, the Test
  Analyst, the Technical Test Analyst, and AI Testing v2.0, with its
  [glossary](https://glossary.istqb.org) for each term.
- [ISO/IEC 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010): the product
  quality model of the International Organization for Standardization (ISO), whose quality
  characteristics the rows of reliability and security follow, read through the ISO 25000 portal.
- [Fintan](https://fintan.jp/page/1456/): the テスト種別カタログ (test type catalog) of TIS,
  under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Added: a check that teams run under its common name but that none of these sources lists.

## Rules for every test

- Regression\
  Every unit, integration, and end-to-end test runs again on each change, so that a change that
  breaks what worked shows at once. This rerun is what SWEBOK and CTFL call regression testing, so
  it has no row of its own.
- Prompts\
  A test that runs a prompt is a benchmark. The model's result varies from run to run, so a
  criterion would pass or fail by chance. The test runs each case several times and measures the
  share of runs that are right. Where the prompt picks items, it measures precision and recall. It
  measures again on each new version of the model, as CT-AI's drift testing does.

## Parts

Unit tests test each part against its contract.

| Check | Kind | When to pick | What it checks or measures | Recommended criterion | Sources |
|---|---|---|---|---|---|
| Lint | Quality | Always. | The code against the project's coding rules and format. | 0 findings. | Fintan |
| Static analysis | Quality | Always. | Faults found without running the code, such as mismatched types, import cycles, copied code, and calls to an interface that the project forbids. | 0 findings. | CTFL, CTAL-TTA, Fintan |
| Complexity analysis | Quality | Always. | The complexity of each function, such as its nesting, branches, returns, arguments, and statements. | Each limit at the default of the tool that checks it, such as a cognitive complexity of 15 in [SonarQube](https://docs.sonarsource.com/sonarqube-server/latest/user-guide/code-metrics/metrics-definition/). | CTAL-TTA, Fintan |
| Unit testing | Quality | Always. | Each part against its contract. | Every case passes. | CTFL, CTAL-TA, Fintan |
| Code coverage | Quality | Always. | The share of statements and branches that the tests run. | 100% statement (C0) and branch (C1) coverage. | CTFL, CTAL-TTA |
| Property-based testing | Quality | Always. | Whether the code keeps a stated property over many inputs that a tool generates. | 0 counterexamples. | Added |
| Mutation testing | Quality | Always. | Whether the tests fail when a tool makes small changes to the code. | 0 surviving mutants. | Added |
| Characterization testing | Quality | When the work changes existing code that no specification describes. | What a part does now, recorded as its expected result before the change. | Every case passes. | Added, from [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/) by Michael Feathers |
| Data compatibility testing | Quality | When the product reads data that another program or an earlier version wrote. | Whether the product reads that data. | The product reads, without loss, each kind of data that each earlier version wrote. | Fintan |

## Architecture

Integration tests test the joined parts against each element of the architecture.

| Check | Kind | When to pick | What it checks or measures | Recommended criterion | Sources |
|---|---|---|---|---|---|
| Integration testing | Quality | Always. | The joined parts against each element of the architecture, including each interface between two parts or to an outside system. | Every case passes. | SWEBOK, CTFL, Fintan |
| Reliability testing | Quality | When a fault or an interruption must not lose data or state, beyond what the user stories already promise. | Fault tolerance and recoverability, as ISO/IEC 25010 defines them: whether the product works as intended despite faults, and recovers the data directly affected. | The product recovers from each fault that the architecture names, with no data lost. | ISO/IEC 25010, CTAL-TTA, Fintan |
| Security testing | Quality | When some data or operation must be open only to those authorized, such as with several users or with public access. | Security, as ISO/IEC 25010 defines it: whether the product defends against attack, and gives each user or system only the access that its authorization allows. | Each attack and each access beyond authorization that the architecture names is refused. | ISO/IEC 25010, SWEBOK, CTAL-TTA, CT-AI, Fintan |
| Privacy testing | Quality | When the product handles personal data. | Whether the product uses personal data only as it allows. | No personal data reaches a use that the product doesn't allow. | SWEBOK |
| Contract testing | Quality | When the tests use a double of an outside thing that the product doesn't control, such as its host. | Whether the double gives what the real thing gives. The steps of each recorded run run again on each new version of the real thing. | For each recorded step, the real thing gives the same result as the double. | Added, from [ContractTest](https://martinfowler.com/bliki/ContractTest.html) by Martin Fowler |
| Traceability | Quality | Always. | Whether each element of the architecture has a test, and each test names an existing element or case one level up, which a script checks by name. Whether each test checks what its element says, such as each branch of a sequence, which a review checks by reading. | The script finds 0 faults, and the review finds 0 tests that miss what their element says. | CTFL |

## Product

End-to-end (E2E) tests test the product in real use against each key result of the product vision.

| Check | Kind | When to pick | What it checks or measures | Recommended criterion | Sources |
|---|---|---|---|---|---|
| Scenario testing | Quality | Always. | A user's whole task from start to end, through every part that it crosses, as the E2E test runs it. | Every case passes. | Fintan |
| Installation testing | Quality | Always. | Whether the product installs, updates, and uninstalls as its documentation says. | The documented commands install, update, and uninstall the product on a fresh system. | SWEBOK |
| Configuration testing | Quality | When the product supports more than one system, runtime, or setting. | The product on each combination of system, runtime, and settings that it supports. | Every case passes on each supported combination. | SWEBOK, Fintan |
| Back-to-back testing | Quality | When a change replaces a version and must keep its behavior. | Whether the new version gives the old version's result for the same input. | Each input gives the old version's result. | Fintan, CT-AI |
| Conformance and compliance testing | Quality | When the product must follow a standard or a regulation. | The product against that standard or regulation. | The standard's validator or checklist finds 0 faults. | SWEBOK |
| Migration testing | Quality | When the product takes over data or work from an old system. | Whether the data and the work move from the old system to the new one, and back if the move fails. | All the data moves, and moving back restores the old system. | Fintan |
| Operation testing | Quality | When operators run the product, such as with backups and monitoring. | Whether the operators' procedures work. | Each procedure works as written. | Fintan |
| Performance testing | Benchmark | When someone decides by how fast the product runs or what it uses. | Response time, throughput, and resource use at normal load and at peak load. | None | CTAL-TTA, Fintan |
| Stress testing | Benchmark | When someone decides by how much load the product takes. | The most load that the product takes before it fails, and how it fails. | None | Fintan |
| Volume testing | Benchmark | When the product's data grows, and someone decides by how it copes. | Response time and resource use with the data at the size it grows to. | None | Fintan |
| Long-run testing | Benchmark | When the product runs for a long time in one process. | Memory and other resource use over a long run, where a leak shows. | None | Fintan |
| Usability testing | Benchmark | When someone decides by how easily users reach their goal. | The time users take to reach their goal, how many reach it, and how satisfied they are, accessibility included. | None | SWEBOK, CTAL-TA, Fintan |
| Alpha and beta testing | Benchmark | When real users can try a release. | What real users report from their own use, first at the maker's site and then at theirs. | None | SWEBOK |
