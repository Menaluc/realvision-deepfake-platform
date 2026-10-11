# AIDD Workflow

This document defines the AIDD (AI-Driven Development) workflow to use for the RealVision Deepfake Platform.

The purpose is to ensure that development is iterative, reviewable, testable, and understandable.

---

# Planning: Steps 1–4

## Step 01 — Scope the Feature

Break the work into a small, AI-digestible feature chunk.

The chunk should be:
- small enough to review and test
- large enough to deliver meaningful progress
- limited to one clear goal

Before continuing, define:
- what is being built
- what is explicitly not part of this chunk
- which files or components are likely involved

---

## Step 02 — Gather Context

Before planning or coding, inspect the relevant project context.

Understand:
- current behavior
- relevant files
- dependencies
- constraints
- existing tests
- known bugs or limitations
- existing ML behavior that must be preserved

Use relevant documentation, architecture decisions, examples, and existing code.

Do not modify code during this step.

---

## Step 03 — Create Plan

Create a concrete implementation plan before writing code.

The plan should include:
- technical requirements
- product behavior
- files to create or modify
- data/request flow
- edge cases
- failure points
- tricky integrations
- tests that should be added or updated
- relevant engineering concepts or patterns

Highlight anything uncertain or risky.

Do not start implementation yet.

---

## Step 04 — Iterate on Plan

Review and refine the plan before implementation.

Check:
- Is the scope still small enough?
- Are responsibilities clear?
- Are there simpler alternatives?
- Are edge cases covered?
- Are there unnecessary abstractions?
- Are there missing tests?
- Does the plan preserve existing behavior where required?

Continue refining until the plan is approved.

---

# Building & Reviewing: Steps 5–8

## Step 05 — Build

Implement only the approved plan.

Rules:
- Do not expand scope silently.
- Do not introduce unrelated refactors.
- Do not add dependencies unless required and approved.
- Keep changes small and understandable.
- Preserve ML behavior unless a change was explicitly approved.

---

## Step 06 — Checkpoint & Stage

Bring the code to a runnable state.

Before continuing:
- the application should run
- relevant tests should pass
- temporary/debug code should be removed
- changes should be staged for review

This step is the checkpoint before deeper review.

---

## Step 07 — Run Static Checks

Run all applicable automated checks.

Examples:
- linting
- formatting
- type checks
- unit tests
- API tests
- integration tests where relevant

Also perform an AI reflection/review pass focused on:
- suspicious logic
- duplicated code
- weak error handling
- edge cases
- unnecessary complexity

Do not automatically fix every finding. Classify and explain them first.

---

## Step 08 — Manual Review

The developer manually reviews the changes.

Check:
- logic
- data flow
- error handling
- edge cases
- resource cleanup
- security implications
- API contract
- readability
- test coverage
- whether the implementation still matches the approved plan

The developer should also be able to explain:
- what changed
- why it changed
- which engineering principles were used
- what alternatives existed
- what trade-offs were accepted

If issues are found, return to the appropriate earlier step.

---

# Evolving: Steps 9–12

## Step 09 — Repeat Cycle

Once the current feature chunk is complete, return to Step 01 for the next chunk.

Do not combine multiple unfinished chunks into one large change.

The development loop is:

Scope
→ Context
→ Plan
→ Refine
→ Build
→ Check
→ Review
→ Repeat

---

## Step 10 — Bug Bash

After a meaningful set of features is complete, perform a focused manual testing session.

Actively search for:
- edge cases
- unexpected input
- invalid states
- broken navigation
- API failures
- concurrency issues
- cleanup problems
- confusing error messages
- regressions in existing ML behavior

Document the issues found before fixing them.

---

## Step 11 — Red Queen Phase

Perform an adversarial AI code review.

The goal is to challenge the implementation, not confirm it.

Review for:
- hidden assumptions
- race conditions
- brittle code
- security weaknesses
- incorrect error handling
- poor boundaries
- unnecessary coupling
- untested behavior
- maintainability issues
- performance risks

For every finding classify it as:
- confirmed bug
- likely bug
- risk
- design limitation
- technical debt
- acceptable MVP trade-off

If recurring patterns appear, update the project's working rules or development guide.

---

## Step 12 — Human PR Review

Create a pull request for the completed feature or milestone.

The final human review should confirm:
- the feature matches its scope
- tests pass
- architecture was not changed silently
- documentation is updated where needed
- known trade-offs are documented
- the developer understands the implementation

Only then is the feature considered complete.

---

# Workflow Principle

AI assists with:
- investigation
- planning
- implementation
- testing
- review

The human remains responsible for:
- scope
- architectural decisions
- approval
- understanding
- validation
- final review

The goal is not maximum coding speed.

The goal is controlled, explainable, high-quality development.
