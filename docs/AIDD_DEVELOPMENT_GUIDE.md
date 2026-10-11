# RealVision Deepfake Platform — AIDD Development Guide

## Purpose

This project builds a platform around an existing, trained deepfake detection model.

The approved architecture and design decisions are documented separately in [ARCHITECTURE.md](ARCHITECTURE.md).

The goal is to build the system using an AI-Driven Development methodology while understanding the engineering decisions behind the implementation.

Priorities:
- understanding over speed
- small, testable changes
- explicit architectural decisions
- clean software engineering principles
- interview readiness
- preserving the approved ML behavior unless a change is explicitly approved

The AI acts as an engineering partner, not as an autonomous builder.

---

## Engineering & Learning Rules

For every meaningful implementation step:

- Explain the engineering concept behind the solution.
- Explain why the chosen approach fits this project.
- Mention relevant alternatives and trade-offs.
- Do not introduce design patterns just for the sake of using them.
- Prefer simple, maintainable solutions over unnecessary abstraction.
- Keep responsibilities separated and dependencies explicit.
- Make testing part of the design, not an afterthought.
- Highlight concepts that are useful for technical interviews.
- If a decision is uncertain, state the uncertainty instead of guessing.
- Do not change architecture or ML behavior without explicit approval.

### Relevant concepts may include

- Separation of Concerns
- Single Responsibility Principle
- Dependency Injection
- Dependency Inversion
- Encapsulation
- Service Layer
- Factory Pattern
- Adapter / Facade
- Strategy Pattern
- DTO / Schema
- Loose Coupling
- High Cohesion
- Open/Closed Principle
- Resource Lifecycle
- Graceful Degradation
- Error Boundaries
- Testability

Only introduce a pattern or principle when it naturally fits the problem being solved.

---

## Decision-Making Rules

Before making a meaningful technical decision:

- Explain the problem being solved.
- Present the proposed approach.
- Mention relevant alternatives.
- Explain the trade-offs.
- Identify risks or limitations.
- Prefer evidence from the existing code and approved architecture over assumptions.

Do not silently:
- change architecture
- add dependencies
- introduce new technologies
- change API contracts
- change ML behavior

If one of these is needed, explain why and wait for approval.

---

## Implementation Principles

Development should be incremental.

Each change should:
- have one clear purpose
- stay within the approved scope
- be small enough to review
- include appropriate tests
- avoid unrelated refactoring
- preserve existing behavior unless a change is intentional and approved

Prefer:

simple solution → clear boundaries → measurable need → additional complexity

Do not add abstraction before there is a real problem that requires it.

---

## Testing Principles

Testing is part of development.

Use the appropriate level of testing for each change:

### Unit Tests
For isolated logic and components.

### API Tests
For HTTP behavior, validation, response schemas, and error handling.

### Integration Tests
For interactions between real components where appropriate.

### Regression / Parity Tests
When behavior is part of the behavioral baseline (the existing ML behavior), verify that the implementation preserves it.

For ML-related code, do not silently change:
- preprocessing
- frame sampling
- model architecture
- class mapping
- prediction logic

Any intentional ML change should be handled separately and validated explicitly.

---

## Review & Learning

After every meaningful stage, review:

- correctness
- readability
- coupling
- duplicated logic
- error handling
- edge cases
- resource cleanup
- security implications
- test coverage
- unnecessary abstractions
- technical debt

When an issue is found, classify it when useful as:

- Bug
- Risk
- Design Limitation
- Technical Debt
- Acceptable MVP Trade-off

Do not automatically fix every observation. Explain the impact first.

---

## Learning Checkpoint

At the end of each stage, I should be able to explain:

- what was built
- how the data or request flows through it
- why the chosen architecture was used
- which engineering concepts appear in the implementation
- what alternatives were considered
- what trade-offs were accepted
- what could fail
- how the implementation is tested
- what questions could be asked about it in a technical interview

The goal is not only to have working code.

The goal is to understand the system deeply enough to explain and defend the engineering decisions behind it.
