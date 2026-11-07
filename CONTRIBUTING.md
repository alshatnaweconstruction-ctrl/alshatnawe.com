# Contributing

## Branches

There is no branch history to copy here: AdPilot commits feed changes straight to `main`. For human changes use the same prefixes as the other repositories of this account: `feat/`, `fix/`, `docs/`, `chore/` plus a short kebab-case topic (for example `docs/feed-readme`).

Snapshot branches (`backup/*`, `it-backup/*`, `upload-wip-*`, `wip-upload-*`) are archives. Do not open pull requests
from them or commit to them.

## Pull requests

- One topic per pull request. Fill in the pull request template.
- **Squash-merge** into `main`. The squash commit title says what changed, in the imperative.
- Tests and checks must pass **before** merge (see below). Do not merge a red pull request.
- Ask the owner, @alshatnaweconstruction-ctrl, to review anything that touches production, money, legal text or company facts.

## Tests and checks

This repository has no CI. Before a feed change is merged:

```bash
# 1. the feed is well-formed XML
python -c "import xml.etree.ElementTree as E; E.parse('bazaraki.xml'); print('XML OK')"
# 2. no external_id that is on main disappears (Bazaraki deletes ads that leave the feed)
git show origin/main:bazaraki.xml > /tmp/main_feed.xml
python -c "import re,sys; ids=lambda p: set(re.findall(r'<external_id>([^<]+)</external_id>', open(p,encoding='utf-8').read())); gone=ids('/tmp/main_feed.xml')-ids('bazaraki.xml'); print('removed:', sorted(gone)); sys.exit(1 if gone else 0)"
```

## Rules

- **No secrets** in the repository: no tokens, keys, passwords or `.env` files. Use GitHub Secrets.
- **No client personal data**: no names, phone numbers, ID/passport numbers, home addresses or bank details. Use
  initials or project codes.
- Do not invent prices, quantities, measurements or regulations. Mark anything unverified as "needs checking".
- **`main` is live.** Bazaraki imports `bazaraki.xml` from `main`. Never force-push, never rename or move `bazaraki.xml`, never remove or change an existing `external_id`.
- AdPilot pushes to `main` every time it publishes an ad. Merge a pull request between AdPilot runs (it runs at minutes 7 and 37 of each hour, UTC); a rejected AdPilot push is retried on the next run.
- This repository is **public**. Nothing private goes here: no price sheets, no inventories, no client data, no keys.
- Company facts (name, registration number, phone, licences, addresses) must match the company's official records. Do not attribute this business to any other company, and do not add another company's name or registration number.

## Labels

- `type: bug | feature | docs | chore | security | test`
- `area: ...` (which part of the repository)
- `priority: P0 | P1 | P2 | P3` (P0 = live system broken or data at risk)
- `status: needs-owner | blocked | in-progress`
