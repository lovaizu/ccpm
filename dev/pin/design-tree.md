# Design tree

Goal: The user has the work made from their plan be what they mean, with no point of it left for the maker to guess.
- Grounds: dev/pin/product-vision.md:18-19 before this tree, O1: "The person has every point of their plan settled as they mean it before any work starts, asked only what is theirs."; asked why until no further end showed (D2).

- **product-vision/Q1** Listing whom to build for, does the developer find every role that comes to the product with an end of its own?
  - **D1 Who comes to Pin with an end of their own?**: One role, the user: one whose plan it is, such as a feature or a document, a person or an AI that settles a plan for a person, as both are after the same: the work made as the person means it. The AI that makes the work afterwards is after that work, which the user is after, so it is no role of Pin's. (reasoning)
    - Grounds: product-vision/best-practice.json Q1 thinking: "Cut the roles by that end, not by who or what takes them: a person and an AI that want the same are one role."
    - Grounds: dev/pin/product-vision.md:3-10 before this tree named two users, the person and the maker AI; the maker AI "wants the work's design settled with that person before it builds", the person's end reached on their behalf.
    - Grounds: dev/plugin-best-practice.md, Where the orchestrator runs: an AI calls a plugin by its skill in its own main conversation, which can ask the person, so no AI stands between Pin and the person.
    - Also serves: product-vision/Q2
- **product-vision/Q2** Reading an objective, does the developer see what its role gets from the product?
  - **D2 The user's objective: the end they are after, with the role as its subject**: O1: The user has the work made from their plan be what they mean, with no point of it left for the maker to guess. Settling the points before the work starts, and asking the user only what is theirs, is how Pin reaches it, so it goes to the concept and the key results. (reasoning)
    - Grounds: product-vision/best-practice.json Q2 steps: "Ask why of each part of the objective until no further end shows, and write that end. Move a part that says how to Concept"
    - Grounds: dev/pin/product-vision.md:18-19 before this tree: "settled as they mean it before any work starts, asked only what is theirs."
    - Also serves: product-vision/Q3
    - Also builds on: D1
- **product-vision/Q3** Weighing a piece of work, does the developer see which one objective it brings closer, or that it brings none closer?
- **product-vision/Q4** After a change, does the developer see from the key results whether to keep it?
  - **D3 How do success and failure of O1 show in what the user does?**: O1 fails on a point of the plan where the work needs it and the design the user confirmed does not hold it or holds it open; where the design holds it otherwise than the user means, so the work is redone; where the user is asked it while it is not theirs, so they leave it to Pin or tell Pin a fact Pin could have found; where the user settles it apart from Pin, such as in a chat with the AI that makes the work; and where a point the user's AI settled is asked again or settled otherwise. It succeeds where the work needs no point the design lacks and the user changes none. (reasoning)
    - Grounds: dev/pin/product-vision.md:20-31 and :35-43 before this tree: the four ways a point went wrong, and a point the maker AI settled settled otherwise or asked again.
    - Grounds: product-vision/best-practice.json Q4 steps: "List how success or failure would show in what the role does or feels"
    - Also builds on: D2
  - **D4 O1's key results**: KR1.1: of the points of the plan that the work needs or that are put to the user, the share that goes wrong in a way of D3; lower is better. KR1.2: the time from the user's first request to the design they confirm, the user's own time answering included; shorter is better. (reasoning)
    - Grounds: dev/pin/product-vision.md:20-32 before this tree: KR1.1 and KR1.2.
    - Grounds: product-vision/best-practice.json Q4 thinking: "KR.1 how well, and KR.2 how soon."
    - Also builds on: D3
- **product-vision/Q5** Weighing the product against what its roles do today, does the developer see why it meets each objective where that way does not?
  - **D5 What sets Pin apart from what its user does today, and makes it meet O1: at most five ideas, each with the present way it beats**: Pin instead of having an AI start from the request and ask as questions occur, or write a plan up front that fills each gap with an assumption: (1) From the goal down: every point is found as what must hold for the goal and what makes it hold, so none the work needs is missed and none serves nothing. (2) Facts found, decisions asked: Pin finds each fact itself and shows it to confirm, settles what follows from the goal and the facts, and asks the user only a decision where two ways serve equally or one is hard to undo, with a recommendation. (3) One point at a time, in order: each message holds one point, asked once what it builds on is settled. (4) The whole confirmed: the user sees every point in one short line with who settled it, so they and Pin mean the same before the work starts. (5) Kept in a file: each answer is written to the design tree before the next message, checked to hold together, so a stopped run goes on and the maker reads the design from it. (reasoning)
    - Grounds: plugins/pin/README.md:22-45 before this tree: the present way and the five ideas.
    - Grounds: Riskiest assumption: a person asked one point at a time stays with Pin to the end of a plan of real size; the ux trials check it by KR1.2 and by runs left unfinished.
    - Grounds: product-vision/best-practice.json Q5 steps: "Stop once at most five ideas stand out"
    - Also builds on: D2, D4
- **product-vision/Q6** Changing how the product works inside while its roles see the same, does the developer find the product vision still true?
  - **D6 What does the product vision show, and what does it leave to the README and the architecture?**: Only what the user does, sees and receives: their request, each point put to them, the design shown, and the design tree. Pin's roles, its check and Lane are not named. (reasoning)
    - Grounds: product-vision/best-practice.json Q6 thinking: "The product vision says only what the roles are after, do, see and receive, and nothing of how the product works inside."
    - Also builds on: D1
