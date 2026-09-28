# Maintaining a useful contributor queue

## Goals and limits

The roadmap provides entry points at different experience levels. It does not turn
every proposed feature into a commitment. In particular, asynchronous jobs, new
providers, public-user identity, and ECS infrastructure need architectural decisions.
Do not promote those proposals simply to increase the count of available issues.

## A first-contribution issue is ready when

- Its gap still exists on current `main` and no open PR already owns the same work.
- A contributor can identify a small output and verify it without a paid service.
- Acceptance criteria describe observable behavior, not copying an implementation.
- References resolve, commands identify the relevant package, and dependencies are explicit.
- It does not need a broad refactor, authentication redesign, or infrastructure account.

Use `good first issue` only with `difficulty:beginner` and `status:ready`. A contributor
may be new to this repository but experienced in security; do not assume every newcomer
should receive the beginner label, or label sensitive designs as easy.

## Keep contributions independent

Prefer a separate page, example directory, or focused regression file. If several
issues need the same runtime function changed, coordinate their scopes before people
start. Avoid extracting abstractions solely to give every issue a different file.

When a shared interface really must change:

1. Agree and document the contract.
2. Land the smallest compatibility-preserving foundation on `main`.
3. Update references and mock targets in dependent issues.
4. Promote only tasks that can now branch directly from `main`.

Dependencies in this catalog are implementation prerequisites. Related design
discussions may proceed in parallel, but no beginner should need to rebase through
several unfinished feature branches.

## Triage workflow

1. Confirm the proposed problem with synthetic data or source evidence.
2. Search existing issues and PRs; merge overlapping scope instead of opening duplicates.
3. Give the issue one area, one difficulty, and one status.
4. For design work, record the decision required and its compatibility impact.
5. When someone volunteers, acknowledge the intended scope and offer a focused check.
6. Review against the acceptance criteria, not undocumented additional requirements.
7. Close with the fixing PR or a clear explanation if superseded or not planned.

The catalog publisher preserves existing comments and assignees. After publication,
GitHub is the live source of truth; do not regenerate bodies over contributor discussion.

## Review habits

- Separate essential correctness feedback from optional style suggestions.
- Explain why a change is needed and point to a concrete example or existing pattern.
- Credit useful reproductions, documentation work, and partial investigation.
- Require regression evidence for behavior fixes, but avoid tests that merely repeat code.
- Do not demand unrelated cleanup as the price of merging a focused contribution.
- Keep tests model-free unless a clearly marked integration check is intentional.

## Backlog maintenance

Regularly sample ready issues for stale paths, already-implemented behavior, and
competing PRs. Close duplicate or unsupported proposals; a smaller accurate queue is
better than preserving the initial count forever. Replenish it from actual user needs,
test gaps, measured performance, and reviewed operational findings.

Useful signals include setup blockers, time to first useful response, successful
first PRs, stale ready issues, and merge conflicts caused by shared-file tasks. Do not
optimize for raw issue count or demand deadlines from volunteers.
