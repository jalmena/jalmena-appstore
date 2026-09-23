# jalmena store

A personal app store for CasaOS and ZimaOS. Each application lives in its own
repository; this one holds the definitions that let them be installed from the
App Store rather than pasted in by hand.

## Apps

| App | What it is | Repository |
| --- | --- | --- |
| [Tabernacle](Apps/Tabernacle/) | Your sacred repository of guitar tabs: a self-hosted songbook whose songs are plain text files in a directory you own | [jalmena/tabernacle](https://github.com/jalmena/tabernacle) |
| neVus | Longitudinal tracking of moles and skin marks on your own server. Because "I think it was smaller" is not data. Arrives with its first release | [jalmena/nevus](https://github.com/jalmena/nevus) |

## Adding the store

In CasaOS: **App Store → the three dots → Add Source**, and paste

```
https://raw.githubusercontent.com/jalmena/jalmena-appstore/gh-pages/appstore.zip
```

The address existing installations were given,
`https://raw.githubusercontent.com/jalmena/tabernacle-appstore/gh-pages/tabernacle-appstore.zip`,
keeps working: GitHub serves the renamed repository under its old name, and the
archive is published under both file names. Nothing needs re-adding.

On ZimaOS 1.7 or later, or any client that speaks version 2 of the protocol,
add the store manifest instead:

```
https://cdn.jsdelivr.net/gh/jalmena/jalmena-appstore@gh-pages/store.json
```

Apps then appear in the store and update when a new version is published here.
CasaOS decides whether to re-download the archive by comparing its size, so it
is served from `raw.githubusercontent.com`, which sends a real
`Content-Length`; GitHub's own `archive/refs/heads/main.zip` does not, and a
store subscribed to it would never notice a new version.

Nothing here is required to run any of the apps. Custom Install with each
project's own compose file works just as well, and so does `docker compose up -d`.

## What is in here

```
Apps/<App>/
  docker-compose.yml    the app, and its store metadata under x-casaos
  icon.svg              the mark
  thumbnail.png         the store card
  screenshot-*.png      what the app looks like
category-list.json        the categories this store uses
store-config.json         who this store is
store-icon.svg            the store's own mark
supported-languages.json  which locales the build may emit (English only)
scripts/lint_apps.py      the conventions below, as a check
scripts/build.sh          build dist/ locally, the way the deploy does
```

`dist/` is build output and is not committed. Every merge into `main` builds it
and deploys it to the `gh-pages` branch, which is what both addresses above
point at; the `gh-pages` history, one commit per deploy naming the source
commit, is the release log. `./scripts/build.sh` produces the same output
locally, so it can be looked at before it is published.

## Conventions

The lint in `scripts/lint_apps.py` enforces these on every pull request.

- **The compose `name` is the app's identity for CasaOS** (lowercase, unique
  across every store a user subscribes to, never renamed once published) and
  **`x-casaos.id` is its identity for ZimaOS** (reverse-domain,
  `io.github.jalmena.<app>`). `store_app_id` is never written; CasaOS derives it.
- **Locale keys are lowercase** (`en_us`, not `en_US`). CasaOS looks up `en_us`
  literally, and the v2 build normalises lowercase to `en_US` on its way into
  the index, so one spelling serves both.
- **Everything shown to whoever installs is English.** CasaOS falls back to
  `en_us` when it has no entry for the reader's language, so one language here
  is one language everywhere.
- **Images are pinned to an exact version**, never `latest`. CasaOS shows
  "update available" when the main service's tag changes; `x-casaos.version`,
  `update_at` and `release_notes` change with it.
- **Asset URLs are absolute.** A v2 build resolves a bare `thumbnail.png`
  against its base URL; CasaOS, reading the compose straight out of the archive,
  has no base URL to resolve it against.
- **Host ports are unique across the store** and chosen not to collide with the
  official and BigBear stores; `port_map` is the quoted host port; `index` is `/`.
- **Categories** come from the fixed list the v2 format accepts (`Media`,
  `Productivity`, `Home`, `Networking`, `AI`, `Finance`, `Social`, `Developer`,
  `Others`); there is no Health category, so neVus lives under `Others`.
- **The store's `store_id` never changes**, even when its display name does.

## Publishing a new version of an app

1. Update `image:` and `x-casaos.version` in `Apps/<App>/docker-compose.yml`,
   and `x-casaos.update_at` and `release_notes` with them.
2. Refresh the assets from the project if the mark or the screenshots moved.
3. Run `./scripts/build.sh` and look at `dist/`.
4. Open a pull request. Validation lints, builds and checks that the pinned
   image exists. Merging into `main` deploys.

## Adding a new app

Copy the shape of `Apps/Tabernacle/`, pick a `name`, an `id` and a free host
port, keep every asset URL absolute and pointing at this repository's `main`
branch, and open a pull request. The lint says what is missing.

## Licence

Each app folder carries the licence of its application (Tabernacle: GPLv3;
neVus: AGPL-3.0-only). The store tooling, this README and the store's own mark
are under GPLv3, as before. No app definition here supplies, licenses or
distributes any content of its own.
