# Tabernacle app store for CasaOS and ZimaOS

A one-app store, so [Tabernacle](https://github.com/jalmena/tabernacle) can be
installed from the App Store on CasaOS and ZimaOS rather than pasted in by hand.

## Adding it

In CasaOS: **App Store → the three dots → Add Source**, and paste

```
https://raw.githubusercontent.com/jalmena/tabernacle-appstore/gh-pages/index.json
```

Tabernacle then appears in the store and updates when a new version is published
here.

Nothing here is required to run Tabernacle. Custom Install with the project's own
[`compose.yaml`](https://github.com/jalmena/tabernacle/blob/main/compose.yaml)
works just as well, and so does `docker compose up -d`.

## What is in here

```
Apps/Tabernacle/
  docker-compose.yml    the app, and its store metadata under x-casaos
  icon.svg  icon.png    the mark
  thumbnail.png         the store card
  screenshot-1..3.png   library, song sheet, chord page
store-config.json       who this store is
supported-languages.json  which locales the build may emit
```

`dist/` is build output and is not committed. Pushing a `v*` tag builds it and
deploys it to the `gh-pages` branch, which is what the URL above points at.

The compose file here is the store's, not the project's. It mounts
`/DATA/AppData/tabernacle/data`, which is where CasaOS puts app data, and it
carries the metadata the [v2 store
protocol](https://github.com/IceWhaleTech/CasaOS-AppStore/tree/main/docs) asks
for. The project's own `compose.yaml` mounts `./data` and is meant for a
checkout. Two audiences, two files; when the app's version changes, `image:` and
`x-casaos.version` change here.

## Publishing a new version

1. Update `image:` and `x-casaos.version` in `Apps/Tabernacle/docker-compose.yml`,
   and `x-casaos.update_at` and `release_notes` with it.
2. Refresh the assets from the project if the mark or the screenshots moved:
   they are copies of `assets/` there.
3. Tag and push. The workflow builds and deploys.

## Licence

The app definition and the assets are under the same licence as Tabernacle
itself, GPLv3. Tabernacle ships no song library and supplies, licenses or
distributes no musical work.
