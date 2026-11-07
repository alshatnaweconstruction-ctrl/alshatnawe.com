# alshatnawe.com: Bazaraki feed

Public repository that hosts the **Bazaraki XML import feed** and the ad photos that AdPilot publishes. It is not the
website source: the website lives in the private repository `alshatnawe`.

> **`main` is live.** Bazaraki imports `bazaraki.xml` from the `main` branch. Never force-push, never rename or move
> `bazaraki.xml`, and never remove or change an existing `external_id`: Bazaraki deletes ads that disappear from the
> feed.

## How it is updated

- **AdPilot** (a separate private repository) appends ads to `bazaraki.xml` and adds their photos under `photos/`. It
  pushes to `main` with a write deploy key (`adpilot-feed`). Its commits read `Add <ID> to the Bazaraki feed: additive
  +1/-0 (AdPilot)`.
- Human changes go through a pull request (see [`CONTRIBUTING.md`](CONTRIBUTING.md)).

## Layout

| Path | Content |
|---|---|
| `bazaraki.xml` | The live feed: `<root>` with one `<list-item>` per ad, keyed by `<external_id>`. |
| `photos/<service>/` | Photos used by the current ads (referenced by raw.githubusercontent.com URLs on `main`). |
| `ad-NNN/`, `ad-sv-NNN/`, `ad-ins-001/` | Photo sets (`01`-`05`) from the first feed versions. |
| `images/` | Image library by category (builders, tiling, renovation, ...). |
| `bazaraki_new.xml`, `bazaraki_backup_before_pastor.xml` | Older feed copies kept for reference. The import URL points at `bazaraki.xml` only. |
| `BazarakiSystem/` | Earlier Python tooling and notes for generating ads (legacy, not run by AdPilot). |
| `01.png`, `02.png`, `03.png` | Loose images from the first upload. |

The number of ads changes every time AdPilot publishes, so it is not written here. Count the `<list-item>` elements in
`bazaraki.xml` for the current figure.

## Checks before merging a feed change

There is no CI in this repository. [`CONTRIBUTING.md`](CONTRIBUTING.md) has two commands: the XML must parse, and no
`external_id` that is on `main` may disappear.

## Security

This repository is public. Nothing private goes here: no price sheets, inventories, client data or keys. See
[`SECURITY.md`](SECURITY.md).
