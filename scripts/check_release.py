#!/usr/bin/env python3
"""Deterministic release check for the published scanner artifact.

Run from the repository root:

    python3 scripts/check_release.py --check

The check reads the allowlisted inventory in release-manifest.json. It
rejects a manifest payload path that is absolute, escaping, a backslash
path, a duplicate, a NUL byte or Git metadata before any hash or read.
The root .git exclusion below is a filesystem allowance for legitimate
clone and worktree metadata; a manifest payload path never names it. It
also rejects an invalid hash, type or schema, an unlisted file, a
missing file, a SHA-256 mismatch, a symlink, an executable-bit mismatch,
and an unreadable directory. A directory that cannot be listed fails the
check instead of being skipped; a readable empty directory passes.
"""

import hashlib
import json
import os
import re
import stat
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_NAME = "release-manifest.json"
ROOT_GIT_METADATA = ".git"
HEX64 = re.compile(r"[0-9a-f]{64}")


class WalkRefusal(Exception):
    """A directory below the release root could not be listed."""


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message):
    print("release check failed: " + message, file=sys.stderr)
    return 1


def git_metadata_component(value):
    return any(part == ".git" for part in value.split("/"))


def valid_relative_path(value):
    if not isinstance(value, str) or not value:
        return False
    if "\x00" in value:
        return False
    if "\\" in value or value.startswith("/"):
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    if value == MANIFEST_NAME:
        return False
    return all(part not in ("", ".", "..") for part in value.split("/"))


def walk_error(root):
    def on_error(error):
        name = getattr(error, "filename", "") or ""
        relative = (
            os.path.relpath(name, root).replace(os.sep, "/") if name else "."
        )
        raise WalkRefusal(
            "unreadable directory in the release inventory: " + relative
        )

    return on_error


def main(argv):
    if argv != ["--check"]:
        print("usage: check_release.py --check", file=sys.stderr)
        return 2
    if os.path.islink(ROOT):
        return fail("the release root is a symlink")
    manifest_path = os.path.join(ROOT, MANIFEST_NAME)
    if os.path.islink(manifest_path):
        return fail("the release manifest is a symlink")
    if not os.path.isfile(manifest_path):
        return fail("release manifest is missing")
    try:
        with open(manifest_path, encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, ValueError):
        return fail("release manifest is malformed")
    if not isinstance(manifest, dict):
        return fail("release manifest is malformed")
    schema = manifest.get("schema_version")
    if isinstance(schema, bool) or not isinstance(schema, int) or schema != 1:
        return fail("release manifest schema_version is not 1")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return fail("release manifest files list is empty")
    expected = {}
    for entry in files:
        if not isinstance(entry, dict):
            return fail("release manifest entry is malformed")
        path = entry.get("path")
        digest = entry.get("sha256")
        executable = entry.get("executable")
        if isinstance(path, str) and "\x00" in path:
            return fail("release manifest entry path contains a NUL byte")
        if not valid_relative_path(path):
            return fail("release manifest entry path is invalid")
        if git_metadata_component(path):
            return fail(
                "release manifest path names Git metadata: " + repr(path)
            )
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            return fail("release manifest entry hash is invalid")
        if not isinstance(executable, bool):
            return fail("release manifest entry executable flag is invalid")
        if path in expected:
            return fail("release manifest lists a duplicate path")
        expected[path] = entry

    try:
        for directory, subdirs, names in os.walk(
            ROOT, followlinks=False, onerror=walk_error(ROOT)
        ):
            at_root = os.path.abspath(directory) == os.path.abspath(ROOT)
            keep = []
            for name in subdirs:
                full = os.path.join(directory, name)
                relative = os.path.relpath(full, ROOT).replace(os.sep, "/")
                if os.path.islink(full):
                    return fail("symlink in the release: " + relative)
                if name == ROOT_GIT_METADATA:
                    if at_root:
                        continue
                    return fail(
                        "Git metadata below the release root: " + relative
                    )
                keep.append(name)
            subdirs[:] = keep
            for name in names:
                full = os.path.join(directory, name)
                relative = os.path.relpath(full, ROOT).replace(os.sep, "/")
                if os.path.islink(full):
                    return fail("symlink in the release: " + relative)
                if name == ROOT_GIT_METADATA:
                    if at_root:
                        continue
                    return fail(
                        "Git metadata below the release root: " + relative
                    )
                if relative == MANIFEST_NAME:
                    continue
                if relative not in expected:
                    return fail("unlisted file: " + relative)
    except WalkRefusal as exc:
        return fail(str(exc))

    for relative, entry in expected.items():
        full = os.path.join(ROOT, relative)
        if not os.path.isfile(full):
            return fail("missing file: " + relative)
        try:
            digest = sha256(full)
            mode = os.stat(full).st_mode
        except OSError as exc:
            return fail(
                "release payload is unreadable: " + relative
                + " (" + type(exc).__name__ + ")"
            )
        if digest != entry["sha256"]:
            return fail("hash mismatch: " + relative)
        if bool(mode & stat.S_IXUSR) != entry["executable"]:
            return fail("executable-bit mismatch: " + relative)

    print("release check passed: " + str(len(expected)) + " files", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
