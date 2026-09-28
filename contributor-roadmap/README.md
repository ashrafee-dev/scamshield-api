# Contributor roadmap

This is a 300-item **opportunity backlog**, not a promise to implement every proposal.
Entries have stable IDs and are published as GitHub issues. Existing issues are reused
where their remaining work matches; resolved requests are audited separately.

## Find work

- **status:ready**: a narrow change against current `main`, with acceptance criteria.
- **status:design-needed**: a proposal; agree scope and compatibility before coding.
- **status:blocked**: a named dependency or decision must be resolved first.
- **difficulty:beginner** / **intermediate** / **advanced**: expected experience, not urgency.
- **good first issue** is reserved for ready, beginner-sized, locally verifiable work.

Use the generated [issue index](INDEX.md) or GitHub area labels. Start with
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

1. Reproduce or verify the gap on `main` before labelling work ready.
2. Check existing issues and PRs. Reuse a relevant issue rather than splitting its
   acceptance criteria across competing tickets.
3. Keep first contributions limited to a small output, usually their own test, guide,
   or example. Do not impose estimates or deadlines on volunteers.
4. Keep architecture/security work out of the newcomer queue. A design proposal may
   be closed as not planned; it is not a pre-approved implementation specification.
5. After a refactor, update affected paths and recheck dependencies before promoting tasks.
6. Refresh the ready queue regularly; stale or unsupported ideas should be archived.
7. Treat GitHub issues as the live discussion source. The catalog is the creation/audit
   snapshot; never bulk-overwrite contributor comments or later maintainer edits.

## Areas

The catalog spans contributor experience, text contracts, authentication/configuration,
audio, WebSockets, privacy filtering, provider integration, quality evaluation,
observability, client examples, documentation, testing infrastructure, architecture,
deployment, and asynchronous jobs. Growth-oriented tracks start as design proposals;
they are not requirements for the current synchronous API.

## Publishing and audit

`catalog.json` contains explicit scopes and acceptance criteria for all 300 entries.
`existing-audit.json` records the reconciliation of older issues against the source
revision. `published.json` and `INDEX.md` map stable catalog IDs to GitHub URLs.
The publisher uses bounded sequential requests, checkpoints every write, and checks
stable markers before creating issues. It defaults to local validation; publishing
requires `--publish`. It does not touch the unrelated EKS learning-project prompt.

```bash
# Local-only validation and publisher safeguard tests:
uv run python contributor-roadmap/publish.py
uv run pytest contributor-roadmap/test_publisher.py -q
```

Only maintainers should publish or resume a batch. On resume, the publisher looks
for stable markers on GitHub, including closed issues, and leaves already published
bodies alone. Never remove those markers to force a new issue. An API error stops
the run; inspect it before retrying rather than repeatedly issuing writes.
