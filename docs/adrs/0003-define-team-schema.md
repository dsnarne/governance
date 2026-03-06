# 3. define team schema

Date: 2026-03-05

## Status

Accepted

## Context

The [schemas](../../meta/schemas/) are used to validate the TOML files in
the `contributors/` and `teams/` directories, allowing us to enforce consistency.

The contributor schema is rather simple and straightforward, but the team schema
is more complex and requires this ADR to explain the reasoning behind the design.

## Decision

The [team schema](../../meta/schemas/team.schema.json) and its
[documentation](../../docs/schemas/team.md) explains the current design well,
so here we will discuss why we didn't choose some alternatives.

### Alternative 1: Have each team have more than one projects

In Tech, some teams have more than one project,
most notably the ScottyLabs AI team and the internal tooling team. Therefore,
we could have a `projects` directory with the current team schema and then have
each team in the `teams/` directory maintain a `projects` array. This allows
each team to have more than one website and other resources defined.

However, in Labrador, since each team is working from scratch and needs to deploy
as soon as possible, it makes more sense to have each team have a single project.
Therefore, there is no need to define a `projects` directory.

### Alternative 2: Features list

We could have a `features` list for each team that defines the features that the
team wants to enable. However, it is harder to validate and most teams should use
most of the features. Therefore, this feature list adds more noise than value and
we just have a single `create-oidc-clients` field. If there are more boolean fields
like it in the future, we might want to reconsider adding a features list.

_Note: a field named `ready_to_deploy` would make more sense to give a team more
resources (e.g. Railway) when it is ready to deploy._

### Alternative 3: Using `role` instead of `title` for contributors list

We could use a `role` field for the `contributors` array instead of a `title` field.
However, `title` is more appropriate because the field is just a "title".
A member’s role during development shouldn’t be limited by what they put down here!

Also the word "role" is just harder to pronounce than "title"...

## Consequences

A well‑considered schema design reduces the need for future code changes.
