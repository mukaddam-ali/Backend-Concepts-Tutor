# CI/CD Pipelines

CI/CD automates the process of getting code from a developer's commit to running safely in production, replacing manual, error-prone deployment steps with a repeatable pipeline.

## Continuous Integration (CI)

CI means automatically building and testing every code change as soon as it's pushed, rather than waiting until a big batch of changes is ready.

A typical CI pipeline, triggered on every push or pull request, runs:

1. **Build**: compile the code / install dependencies, catching broken builds immediately.
2. **Lint**: check code style and catch common mistakes automatically.
3. **Test**: run the automated test suite (unit tests, integration tests) to catch regressions before they reach other developers.

The goal is fast feedback: a developer finds out within minutes if their change broke something, instead of discovering it days later when it's tangled up with other changes.

## Continuous Delivery / Deployment (CD)

CD picks up after CI succeeds and handles getting the change out to users.

- **Continuous Delivery**: every change that passes CI is automatically packaged and made ready to deploy, but a human still clicks a button to actually release it to production.
- **Continuous Deployment**: goes one step further — every change that passes CI is automatically deployed to production with no manual approval step at all.

## Common pipeline stages

A full pipeline often looks like: `commit → build → test → deploy to staging → run more tests against staging → deploy to production`. Staging is a production-like environment used to catch issues that only show up in a "real" environment (e.g. configuration differences, third-party service integration) before they reach actual users.

## Deployment strategies used within CD

- **Rolling deployment**: new instances are brought up and old ones taken down gradually, so there's no moment where the whole service is down.
- **Blue-green deployment**: a full second copy ("green") of the production environment is deployed and tested, then traffic is switched over from the old copy ("blue") all at once — makes rollback fast, since you just switch back.
- **Canary deployment**: the new version is rolled out to a small percentage of traffic first, monitored for errors, and only rolled out further if it looks healthy — limits the blast radius of a bad deploy.

## Why this matters for backend engineers

CI/CD turns deployment from a risky, manual, occasional event into a routine, low-stakes, frequent one. Combined with good automated tests, it's what makes it safe to ship small changes often, rather than large, infrequent, high-risk releases.
