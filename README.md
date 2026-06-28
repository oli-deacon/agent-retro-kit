# Agent Retro Kit

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Starter Kit](https://img.shields.io/badge/status-starter--kit-blue.svg)](#quick-start)
[![Agent-Agnostic](https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Codex%20%7C%20Aider-lightgrey.svg)](#what-makes-this-generic)

This is a portable, agent-agnostic operating kit for reviewing how coding agents perform in real work.

It is designed to work with Claude Code, Codex, Cursor agents, Aider, Copilot, Roo, or a mixed team where people use different agentic systems.

The goal is simple:

- collect lightweight evidence from real runs
- review patterns weekly
- choose 1-2 small experiments
- track whether those changes improve delivery quality and reduce avoidable rework

## Why this exists

Most teams using coding agents are learning from anecdotes:

- "that one prompt worked really well"
- "this model feels worse lately"
- "we shipped it, but it took forever"

This repo gives you a lightweight way to replace that with a repeatable operating loop:

1. log real runs
2. review patterns weekly
3. test small changes
4. keep what helps

The point is not to build a heavy analytics system. The point is to help a small team get better, faster, with evidence.

## Quick start

1. Clone this repo.
2. Run `./scripts/bootstrap-weekly-cycle.sh`.
3. Log a few real runs in [data/run-log.csv](data/run-log.csv), either manually or with [scripts/log-run.sh](scripts/log-run.sh).
4. At the end of the week, fill out the generated scorecard in `scorecards/`.
5. Run a 30-45 minute retro with the generated file in `retros/`.

If you only read one extra file, read [docs/claude-code.md](docs/claude-code.md) for a concrete operating pattern.

## Who this is for

This kit is most useful if:

- you or your team use coding agents in real delivery work
- you want to improve outcomes without guessing
- you do not have perfect telemetry
- you need something lightweight enough that people will actually maintain it

It is especially useful for teams using Claude Code, Codex, Aider, Cursor, or mixed agent workflows.

## What makes this generic

This kit does not depend on:

- Codex thread APIs
- a specific system prompt format
- a specific IDE or agent product
- full telemetry or perfect instrumentation

It works with:

- manual logging only
- CSV exports from another tool
- a small custom collector you write later
- mixed evidence from chat transcripts, git history, operator notes, and ticket outcomes

## Recommended use cases

Use this when you want to improve:

- acceptance without edit
- retry count
- costly "eventual success" runs
- verification discipline
- task framing quality
- tool usage quality
- operator workflow around agents

## Starter workflow

1. Use this folder as the repo root layout for a new repo.
2. Start with manual logging in [data/run-log.csv](data/run-log.csv).
3. Use [scripts/log-run.sh](scripts/log-run.sh) when a run ends or during weekly backfill.
4. Run [scripts/bootstrap-weekly-cycle.sh](scripts/bootstrap-weekly-cycle.sh) once per week to create the week files.
5. Refresh the generated scorecard from the recent rows.
6. Run one 30-45 minute retro using the generated retro file.
7. Record only 1-2 experiments for the next cycle.
8. Track durable changes in the decision log.

## Core ideas

- Measure delivery quality, not just whether code was produced.
- Treat costly success as a real signal, not a hidden win.
- Separate verification from implementation.
- Change one or two things at a time.
- Review the whole operating system around the agent, not only the prompt.

## Suggested repo structure

- [docs/claude-code.md](docs/claude-code.md)
- [docs/publishing.md](docs/publishing.md)
- [templates/weekly-retro-template.md](templates/weekly-retro-template.md)
- [templates/weekly-scorecard-template.md](templates/weekly-scorecard-template.md)
- [templates/experiment-backlog-template.md](templates/experiment-backlog-template.md)
- [templates/decision-log-template.md](templates/decision-log-template.md)
- [templates/complex-task-brief-template.md](templates/complex-task-brief-template.md)
- [data/run-log-schema.md](data/run-log-schema.md)
- [data/manual-log-template.md](data/manual-log-template.md)
- [data/run-log.csv](data/run-log.csv)
- `scorecards/`
- `retros/`
- `experiment-backlog.md`
- `decision-log.md`
- [examples/sample-weekly-scorecard.md](examples/sample-weekly-scorecard.md)
- [examples/sample-weekly-retro.md](examples/sample-weekly-retro.md)
- [scripts/bootstrap-weekly-cycle.sh](scripts/bootstrap-weekly-cycle.sh)
- [scripts/log-run.sh](scripts/log-run.sh)

## Operating model

Retros should inspect the whole operating system around the agent, not just the prompt.

For each repeated issue, classify whether the main cause was:

- prompt or instruction gap
- task framing
- missing context
- tool choice or tool access
- workflow or review loop
- reasoning quality
- environment or platform constraint

That keeps the team from overfitting on prompt tweaks when the cheaper fix is better task shaping or stronger verification.

## Minimal viable rollout

If your workplace tooling is locked down, start with this small process:

1. Log only important or messy runs for two weeks.
2. Review 15-30 runs once per week.
3. Choose the 3-5 most representative failures or costly successes.
4. Make only one workflow change and one prompt change at most.
5. Compare the next week against baseline.

## Data collection levels

### Level 1: Manual only

Use manual entry after meaningful runs. This is enough to start.

### Level 2: Semi-automated

Export transcript metadata from your tool and append rows automatically, leaving review fields blank.

### Level 3: Fully automated

Build a collector that creates run candidates from agent sessions, then use the weekly retro only for human review and experiment decisions.

## Practical guidance for Claude Code or similar tools

- Treat one user request or one implementation thread as one run.
- If a thread drifts into a materially different task, log a new run.
- Mark success separately from verification. "Code written" is not the same as "outcome confirmed."
- Treat heavy human cleanup as partial value, even when the final result shipped.
- Prefer reviewing the most expensive successes, not only obvious failures.

See [docs/claude-code.md](docs/claude-code.md) for a concrete operating pattern you can use at work.

## What to review every week

Do not just review obvious failures. Include:

- 1 clean success with low retries
- 1 costly success that technically shipped but took too long
- 1 partial or blocked run
- 1 run with heavy human cleanup
- 1 run that might reveal a task-framing or context problem

That mix gives better decisions than a failure-only retro.

## How to publish this

The easiest path is:

1. Copy these files into a new repo such as `agent-retro-kit`.
2. Commit the starter kit as-is.
3. Run `scripts/bootstrap-weekly-cycle.sh` after clone to seed the working files.
4. Add your own collector later if your work environment allows it.

See [docs/publishing.md](docs/publishing.md) for exact commands and the recommended GitHub setup.

Suggested first commit contents:

- this README
- `LICENSE`
- `docs/`
- `templates/`
- `data/run-log-schema.md`
- `data/manual-log-template.md`
- empty `data/run-log.csv`
- `scorecards/`
- `retros/`
- `experiment-backlog.md`
- `decision-log.md`
- `scripts/bootstrap-weekly-cycle.sh`
- `scripts/log-run.sh`

## Suggested repo description

Use this or adapt it:

> A lightweight, agent-agnostic retrospective kit for improving coding agent delivery quality with weekly scorecards, run logs, and experiment tracking.

## First customizations I would make for work

- rename `team_or_repo` to your team name if you track only one workspace
- add a `ticket_ref` column if work is organized around Jira or Linear
- add an `operator` column if multiple people use the kit
- add a `model` column if you compare Claude, GPT, Gemini, or internal models
- keep the review fields small so the process stays sustainable

## Repository conventions

- Keep `data/run-log.csv` lightweight and append-only.
- Store reviewed retros separately from raw run logs.
- Avoid collecting sensitive prompt contents if your company policy is strict.
- Prefer short factual summaries over transcript dumps.
- If you later automate collection, leave human review fields blank until review time.
