#!/usr/bin/env bash
# Build dist/ the way the release workflow does, so it can be looked at before
# it is published. Downloads the build engine from the same pinned action the
# workflow uses, because that engine is the protocol's only implementation.
set -euo pipefail

ref=${ACTION_REF:-v1.1.2}
raw=https://raw.githubusercontent.com/IceWhaleTech/build-appstore-action/$ref
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
work=${WORK_DIR:-$root/.cache/build}

mkdir -p "$work"
for f in scripts/build_appstore.py requirements.txt; do
	[ -f "$work/$(basename "$f")" ] || curl -fsSL "$raw/$f" -o "$work/$(basename "$f")"
done

[ -d "$work/venv" ] || python3 -m venv "$work/venv"
"$work/venv/bin/pip" install -q -r "$work/requirements.txt"

rm -rf "$root/dist"
"$work/venv/bin/python" "$work/build_appstore.py" \
	--source "$root" --output "$root/dist" \
	--base-url "${BASE_URL:-https://cdn.jsdelivr.net/gh/jalmena/jalmena-appstore@gh-pages}" \
	--cache-file "$root/.cache/build_appstore/image-size-cache.json" \
	--digest-cache-file "$root/.cache/build_appstore/image-digest-cache.json"

# The zip for CasaOS, which subscribes to an archive rather than to store.json.
# It ships next to the v2 output so one branch serves both kinds of client, under
# the store's own name and under the historical name existing installations follow.
(cd "$root" && zip -qr dist/appstore.zip Apps category-list.json && cp dist/appstore.zip dist/tabernacle-appstore.zip)
echo "dist/appstore.zip $(du -h "$root/dist/appstore.zip" | cut -f1)"
