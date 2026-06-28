# Complex Task Brief Template

Use this brief when a request is broad enough that scope, finish line, or verification might drift during implementation. Also use it when an investigation may change deployment, authentication, persistence, data contracts, integrations, or another platform-level architecture.

Keep it short. The point is to sharpen execution, not add ceremony.

## Brief

- Goal: What user-visible or system-visible outcome are we trying to produce?
- In scope: What is definitely included in this slice?
- Out of scope: What is explicitly not part of this slice?
- Finish line: What would make us comfortable calling this done today?
- Verification plan: How will we verify the outcome before closeout?
- Smallest viable first slice: What is the narrowest version we can safely deliver or test first?
- Integration preflight: Which auth paths, downstream contracts, permissions, environments, or side effects should we confirm before implementation starts?
- Known constraints: What plan-tier, cadence, timezone, permission, runtime, environment, tool, policy, or product limits might block verification or delivery?

## Example prompt stub

Use or adapt this shape before broader feature implementation:

```text
Goal:

In scope for this pass:

Out of scope for this pass:

Finish line for this pass:

Verification plan:

Smallest viable first slice:

Integration preflight:

Known constraints or blockers:
```

## Notes

- Use this for broad feature work and architecture-sensitive investigations, not routine bugfixes or small ops changes.
- Confirm platform limits or live contracts from authoritative docs or current configuration before selecting an architecture.
- If the verification plan is weak, fix that before implementation starts.
- If a constraint is likely to block verification, make that explicit up front so the run can end as clearly blocked rather than ambiguously partial.
