#!/usr/bin/env python3
"""Lint every app definition under Apps/ against the CasaOS v1 and ZimaOS v2 store conventions.

Checks: compose name and x-casaos id patterns and uniqueness, allowed category, lowercase locale keys,
semantic version, quoted port_map matching a published port of the main service, unique host ports across
apps, pinned image tags (no latest), absolute asset URLs that exist in this repository when they point here,
and supported architectures. Exit code 1 on any finding. `--print-images` lists the pinned images instead.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*(?:\.[a-z0-9]+(?:[._-][a-z0-9]+)*)+$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")  # SemVer 2.0, prereleases included
LOCALE_RE = re.compile(r"^[a-z]{2}_[a-z]{2}$")
CATEGORIES = {"Media", "Productivity", "Home", "Networking", "AI", "Finance", "Social", "Developer", "Others"}
ARCHS = {"amd64", "arm64"}
LOCALISED = ("title", "tagline", "description", "release_notes")
THIS_REPO_RAW = "https://raw.githubusercontent.com/jalmena/jalmena-appstore/main/"


def findings_for(app_dir: Path, seen_names: dict, seen_ids: dict, seen_ports: dict) -> list[str]:
    out: list[str] = []
    compose_path = app_dir / "docker-compose.yml"
    data = yaml.safe_load(compose_path.read_text())
    name = data.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name):
        out.append(f"{compose_path}: top-level name {name!r} must match {NAME_RE.pattern}")
    elif name in seen_names:
        out.append(f"{compose_path}: name {name!r} already used by {seen_names[name]}")
    else:
        seen_names[name] = str(compose_path)

    x = data.get("x-casaos") or {}
    app_id = x.get("id")
    if not isinstance(app_id, str) or not ID_RE.match(app_id):
        out.append(f"{compose_path}: x-casaos.id {app_id!r} must be lowercase reverse-domain with two or more segments")
    elif app_id in seen_ids:
        out.append(f"{compose_path}: id {app_id!r} already used by {seen_ids[app_id]}")
    else:
        seen_ids[app_id] = str(compose_path)
    if "store_app_id" in x:
        out.append(f"{compose_path}: do not write x-casaos.store_app_id (deprecated; CasaOS derives it from name)")

    if x.get("category") not in CATEGORIES:
        out.append(f"{compose_path}: category {x.get('category')!r} not in {sorted(CATEGORIES)}")
    if not isinstance(x.get("version"), str) or not SEMVER_RE.match(x["version"]):
        out.append(f"{compose_path}: x-casaos.version {x.get('version')!r} must be a quoted semantic version")
    for arch in x.get("architectures") or []:
        if arch not in ARCHS:
            out.append(f"{compose_path}: unsupported architecture {arch!r}")

    for key in LOCALISED:
        value = x.get(key)
        if isinstance(value, dict):
            for locale in value:
                if not LOCALE_RE.match(str(locale)):
                    out.append(f"{compose_path}: {key} locale key {locale!r} must be lowercase like en_us")
    tips = (x.get("tips") or {}).get("before_install")
    if isinstance(tips, dict):
        for locale in tips:
            if not LOCALE_RE.match(str(locale)):
                out.append(f"{compose_path}: tips.before_install locale key {locale!r} must be lowercase like en_us")

    services = data.get("services") or {}
    main = x.get("main")
    if main not in services:
        out.append(f"{compose_path}: x-casaos.main {main!r} is not a service")
    else:
        image = services[main].get("image", "")
        if ":" not in image.rsplit("/", 1)[-1] or image.endswith(":latest"):
            out.append(f"{compose_path}: main image {image!r} must be pinned to an exact tag")
        host_ports = set()
        for port in services[main].get("ports") or []:
            if isinstance(port, dict):
                host_ports.add(str(port.get("published")))
            else:
                host_ports.add(str(port).split(":")[0])
        port_map = x.get("port_map")
        if not isinstance(port_map, str):
            out.append(f"{compose_path}: port_map must be a quoted string")
        elif port_map not in host_ports:
            out.append(f"{compose_path}: port_map {port_map!r} is not a published host port of {main!r} ({sorted(host_ports)})")
        for hp in host_ports:
            if hp in seen_ports and seen_ports[hp] != str(compose_path):
                out.append(f"{compose_path}: host port {hp} already published by {seen_ports[hp]}")
            seen_ports.setdefault(hp, str(compose_path))
    index = x.get("index")
    if not isinstance(index, str) or not index.startswith("/"):
        out.append(f"{compose_path}: index {index!r} must start with /")

    urls = [x.get("icon"), x.get("thumbnail"), *(x.get("screenshot_link") or [])]
    for url in urls:
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            out.append(f"{compose_path}: asset URL {url!r} must be absolute")
        elif url.startswith(THIS_REPO_RAW):
            rel = url[len(THIS_REPO_RAW):]
            if not (ROOT / rel).is_file():
                out.append(f"{compose_path}: asset {rel} referenced but not present in the repository")
    return out


def main() -> int:
    apps = sorted(p for p in (ROOT / "Apps").iterdir() if (p / "docker-compose.yml").is_file())
    if "--print-images" in sys.argv:
        for app in apps:
            data = yaml.safe_load((app / "docker-compose.yml").read_text())
            for service in (data.get("services") or {}).values():
                if service.get("image"):
                    print(service["image"])
        return 0
    categories = {c["name"] for c in json.loads((ROOT / "category-list.json").read_text())}
    findings: list[str] = []
    names: dict = {}
    ids: dict = {}
    ports: dict = {}
    for app in apps:
        findings.extend(findings_for(app, names, ids, ports))
        data = yaml.safe_load((app / "docker-compose.yml").read_text())
        category = (data.get("x-casaos") or {}).get("category")
        if category not in categories:
            findings.append(f"{app}: category {category!r} missing from category-list.json")
    for f in findings:
        print(f"FAIL {f}")
    print(f"{len(apps)} app(s) checked, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
