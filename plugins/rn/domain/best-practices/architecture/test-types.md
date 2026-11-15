# Test types

Test strategy of [the architecture best practice](best-practice.md) gives each type of this list a
row: the tool and the criterion where the product runs it, or why not. Each type stands under its
common name. Its row names its test target, the parts, the architecture, or the product vision, by
the test level that tries it, says what it checks, and names the sources that list it. The
sources hold each type's full account, so this list links them and copies none.

The sources:

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
- Added: a type that teams run under its common name, added where the work needs it.

## Code quality

| Type | Test target | What it checks | Sources |
|---|---|---|---|
| Static analysis | Parts | Faults found without running the code, such as types that don't fit, import cycles, copied code, and calls to an interface the project forbids. | CTFL, CTAL-TTA, Fintan |
| Lint | Parts | Code against the project's coding rules and format. | Fintan |
| Complexity analysis | Parts | Each function within limits on its complexity, such as its nesting, branches, returns, arguments, and statements. | CTAL-TTA, Fintan |

## Test quality

| Type | Test target | What it checks | Sources |
|---|---|---|---|
| Code coverage | Parts | The share of lines and branches that the tests run. | CTFL, CTAL-TTA |
| Mutation testing | Parts | Whether the tests fail when a tool changes the code in small ways. | Added |
| Property-based testing | Parts | Whether the code keeps a stated property over many inputs that a tool generates. | Added |
| Traceability | Architecture | Whether each element of the architecture has a test, and each test names an element or a case one level up that exists. | CTFL |

## A prompt's evaluation

| Type | Test target | What it checks | Sources |
|---|---|---|---|
| Accuracy | Parts | The share of cases whose result is right. | Added |
| Fabrication | Parts | Whether the result states a thing that its input doesn't support. | Added |
| Precision and recall | Parts | Of what the prompt picks, the share that's right, and of what it should pick, the share it picks. | Added |
| Consistency over repeated runs | Parts | Whether each case passes on every one of k runs on the same model. | Added |
| Adversarial testing | Parts | Whether input made to mislead the model, such as an injected instruction, changes what it does. | CT-AI |
| Metamorphic testing | Parts | Whether a known change of the input changes the result as it must, where no one knows the single right result. | CT-AI |
| Drift testing | Parts | Whether the results move as the model or its data change over time. | CT-AI |

## What the product does

| Type | Test target | What it checks | Sources |
|---|---|---|---|
| Functional testing | Parts, architecture | What the product does against what its specification says. | CTFL, CTAL-TA, Fintan |
| Scenario testing | Product vision | A user's whole task, through every part it crosses, from start to end. | Fintan |
| Regression testing | Parts, architecture, product vision | Whether a change broke what worked before it. | SWEBOK, CTFL |
| Comparison with the old version | Product vision | Whether the new version gives what the old one gave for the same input, where the change must keep what it does. | Fintan, CT-AI |
| Interface and API testing | Architecture | Each interface between parts, or to a system outside, against its specification. | SWEBOK |
| Conformance and compliance testing | Product vision | The product against a standard or a regulation that it must follow. | SWEBOK |
| Usability testing | Product vision | Whether users reach their goal with ease, and whether every user can, accessibility among it. | SWEBOK, CTAL-TA, Fintan |
| Alpha and beta testing | Product vision | What real users meet in their own use, first at the maker's site, then at their own. | SWEBOK |

## How the product runs

| Type | Test target | What it checks | Sources |
|---|---|---|---|
| Performance testing | Product vision | Under normal and peak load: how fast the product responds, how much it handles, and what it uses. | CTAL-TTA, Fintan |
| Stress testing | Product vision | What the product does at and beyond the most load it can take. | Fintan |
| Volume testing | Product vision | What the product does with its data at the size it grows to. | Fintan |
| Long-run testing | Product vision | A fault that shows only after long running, such as a memory leak. | Fintan |
| Reliability and recovery testing | Architecture | Whether the product keeps working through a fault, and comes back from it. | CTAL-TTA, Fintan |
| Security testing | Architecture | Whether someone can use the product in a way it must refuse. | SWEBOK, CTAL-TTA, Fintan |
| Privacy testing | Architecture | Whether the product keeps personal data to the uses it allows. | SWEBOK |
| Installation testing | Product vision | Whether the product installs, updates, and uninstalls as its documentation says. | SWEBOK |
| Configuration testing | Product vision | Each combination of system, runtime, and settings that the product supports. | SWEBOK, Fintan |
| Data compatibility testing | Parts | Whether the product reads the data that another program or another version writes. | Fintan |
| Compatibility with a new version of what the product builds on | Architecture | Whether the product still works on each new version of a thing outside it, such as its host, by running the steps of each recorded run again and comparing what the real thing gives with what its double gives, as [a contract test](https://martinfowler.com/bliki/ContractTest.html) does. | Added |
| Migration testing | Product vision | Whether the data and the work move from the old system to the new one, and back where the move fails. | Fintan |
| Operation testing | Product vision | Whether the operators' procedures, such as backup, monitoring, and logs, work. | Fintan |
