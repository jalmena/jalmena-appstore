# Tabernacle app store for CasaOS and ZimaOS

A one-app store, so [Tabernacle](https://github.com/jalmena/tabernacle) can be
installed from the App Store on CasaOS and ZimaOS rather than pasted in by hand.

## Adding it

In CasaOS: **App Store → the three dots → Add Source**, and paste

```
https://raw.githubusercontent.com/jalmena/tabernacle-appstore/gh-pages/tabernacle-appstore.zip
```

On ZimaOS, or any client that speaks version 2 of the protocol, the same store is
also served as JSON:

```
https://raw.githubusercontent.com/jalmena/tabernacle-appstore/gh-pages/index.json
```

Tabernacle then appears in the store, and updates when a new version is published
here. CasaOS decides whether to re-download by comparing the archive's size, so
the archive is served from `raw.githubusercontent.com`, which sends a real
`Content-Length`; GitHub's own `archive/refs/heads/main.zip` does not, and a store
subscribed to it would never notice a new version.

Nothing here is required to run Tabernacle. Custom Install with the project's own
[`compose.yaml`](https://github.com/jalmena/tabernacle/blob/main/compose.yaml)
works just as well, and so does `docker compose up -d`.

## What is in here

```
Apps/Tabernacle/
  docker-compose.yml    the app, and its store metadata under x-casaos
  icon.svg              the mark
  thumbnail.png         the store card
  screenshot-1..3.png   library, song sheet, chord page
category-list.json        the one category this store uses
store-config.json         who this store is
supported-languages.json  which locales the build may emit (English only)
scripts/build.sh          build dist/ locally, the way the release does
```

`dist/` is build output and is not committed. Pushing a `v*` tag builds it and
deploys it to the `gh-pages` branch, which is what both URLs above point at.
`./scripts/build.sh` produces the same thing locally, so it can be looked at
before it is published.

The compose file here is the store's, not the project's. It mounts
`/DATA/AppData/tabernacle/data`, which is where CasaOS puts app data, and it
carries the metadata the [v2 store
protocol](https://github.com/IceWhaleTech/CasaOS-AppStore/tree/main/docs) asks
for. The project's own `compose.yaml` mounts `./data` and is meant for a
checkout. Two audiences, two files; when the app's version changes, `image:` and
`x-casaos.version` change here.

Two details of that file are deliberate and easy to undo by accident:

- **Locale keys are lowercase** (`en_us`, not `en_US`). CasaOS looks up
  `en_us` literally, and the v2 build normalises lowercase to `en_US` on its way
  into `index.json`. Written this way, one file serves both.
- **Everything shown to whoever installs is English.** CasaOS falls back to
  `en_us` when it has no entry for the reader's language, so one language here
  is one language everywhere, rather than a card that reads Spanish on one
  machine and English on the next. The application itself still speaks
  nineteen.
- **The web interface is published on 8440**, because A440 is the note
  everything tunes to and because nothing else claims it: no app in the CasaOS
  store or the BigBear store publishes it, and IANA has it unassigned. Inside
  the container Tabernacle listens on 8080.
- **Assets are absolute URLs.** A v2 build resolves a bare `thumbnail.png`
  against its base URL; CasaOS, reading the compose straight out of the archive,
  has no base URL to resolve it against.

The `icon.png` CasaOS shows is generated from `icon.svg` during the build. It is
not committed, so there is one mark and not two that can drift apart.

## Publishing a new version

1. Update `image:` and `x-casaos.version` in `Apps/Tabernacle/docker-compose.yml`,
   and `x-casaos.update_at` and `release_notes` with it.
2. Refresh the assets from the project if the mark or the screenshots moved:
   they are copies of `assets/` there.
3. Run `./scripts/build.sh` and look at `dist/`.
4. Tag and push. The workflow builds and deploys.

## Licence

The app definition and the assets are under the same licence as Tabernacle
itself, GPLv3. Tabernacle ships no song library and supplies, licenses or
distributes no musical work.
