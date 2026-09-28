# Contributor roadmap

This is a 300-item **opportunity backlog**, not a promise to implement every proposal.
Entries are published as GitHub issues and organized with labels and milestones.
GitHub is the source of truth for status, scope, discussion, and ownership.

## Find work

- **status:ready**: a narrow change against current `main`, with acceptance criteria.
- **status:design-needed**: a proposal; agree scope and compatibility before coding.
- **status:blocked**: a named dependency or decision must be resolved first.
- **difficulty:beginner** / **intermediate** / **advanced**: expected experience, not urgency.
- **good first issue** is reserved for ready, beginner-sized, locally verifiable work.

Use GitHub search and the area labels below. Start with
[CONTRIBUTING.md](../CONTRIBUTING.md). An issue's scope describes its intended changes;
referenced files are reading material, not permission to refactor everything nearby.

Initial audit: **135 ready items**, including **95 beginner items**, and **165 design
proposals**. These are opportunities, not 300 confirmed bugs. Readiness can change
after discussion or a merged PR. Check the live GitHub labels before starting.

| Choose an area | Typical contribution |
| --- | --- |
| [Onboarding](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aonboarding) | Platform walkthroughs and learning guides |
| [Text contracts](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Atext) | Focused request and response regressions |
| [Authentication](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aauth) | Credential/configuration tests; reviewed security designs |
| [Audio](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aaudio) | Upload, decoder, and model-lifecycle cases |
| [WebSockets](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Awebsocket) | Clip lifecycle and connection behavior |
| [Privacy](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aprivacy) | Synthetic filtering regressions and policy review |
| [Provider integration](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aprovider) | Bounded failure and output-validation behavior |
| [Evaluation](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aquality) | Synthetic quality-measurement proposals |
| [Observability](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aobservability) | Operational decisions and runbooks |
| [Clients](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aclients) | Isolated backend examples and request collections |
| [Documentation](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Adocs) | Diagrams, accessibility, and reference accuracy |
| [Test tooling](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Atesting) | Deterministic fixtures and opt-in integration checks |
| [Architecture](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Aarchitecture) | Reviewed boundaries, lifecycle, and compatibility |
| [Deployment](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Adeployment) | ECS and delivery proposals grounded in current artifacts |
| [Async jobs](https://github.com/ashrafee-dev/scamshield-api/labels/area%3Ajobs) | Future design discussions, not approved core features |

## Maintainer rules

See the [maintainer playbook](MAINTAINERS.md) for triage, review, and dependency handling.

1. Reproduce or verify the gap on `main` before labelling work ready.
2. Check existing issues and PRs. Reuse a relevant issue rather than splitting its
   acceptance criteria across competing tickets.
3. Keep first contributions limited to a small output, usually their own test, guide,
   or example. Do not impose estimates or deadlines on volunteers.
4. Keep architecture/security work out of the newcomer queue. A design proposal may
   be closed as not planned; it is not a pre-approved implementation specification.
5. After a refactor, update affected paths and recheck dependencies before promoting tasks.
6. Refresh the ready queue regularly; stale or unsupported ideas should be archived.
7. Treat GitHub issues as the only live roadmap source. Never bulk-overwrite contributor
   comments or later maintainer edits.

## Areas

The roadmap spans contributor experience, text contracts, authentication/configuration,
audio, WebSockets, privacy filtering, provider integration, quality evaluation,
observability, client examples, documentation, testing infrastructure, architecture,
deployment, and asynchronous jobs. Growth-oriented tracks start as design proposals;
they are not requirements for the current synchronous API.

## Live roadmap views

- [All roadmap issues](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+label%3Acontributor-roadmap)
- [Ready work](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3Acontributor-roadmap+label%3Astatus%3Aready)
- [Ready beginner work](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22+label%3Astatus%3Aready)
- [Design discussions](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3Acontributor-roadmap+label%3Astatus%3Adesign-needed)

Maintain the roadmap through normal GitHub issue editing and triage. Do not regenerate
or overwrite issue bodies from repository data. Close stale, duplicated, completed,
or unsupported proposals with a clear explanation rather than preserving a target count.
