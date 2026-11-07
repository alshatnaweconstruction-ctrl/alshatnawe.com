# Security policy

## Reporting a vulnerability

Do **not** open a public issue for a security problem.

Report it privately to the repository owner, @alshatnaweconstruction-ctrl (through the contact details on the owner's GitHub profile; this repository is public, so never post details in an issue). Include what is affected, how to reproduce it,
and the impact you expect. You will get an answer as soon as the owner has reviewed it.

## Scope

This policy covers the public Bazaraki feed (`bazaraki.xml`), the photos, and the legacy tooling in `BazarakiSystem/`.

## Secrets

- Secrets live only in GitHub Secrets or in the hosting provider's settings, never in the repository.
- If a secret is ever committed, treat it as leaked: revoke and rotate it first, then remove it from the files.
  Removing it from history alone is not enough.

## Supported versions

Only the current `main` branch is supported.
