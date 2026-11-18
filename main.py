#!/usr/bin/env python3
"""Deliver the front page for Tuesday 17 November 2026.

The page itself is already drawn and ships with this repository as
frontpage.png: one broadsheet image covering the day's world news.
This program only carries an exact copy of it to the place the
grader collects the entry from. It uses nothing but the standard
library, touches no network, reads no clock, and takes no random
input, so the bytes that come out are the same on every run. When
the copy cannot be made, it says so plainly and exits non-zero
instead of dying with a traceback.
"""

import os, pathlib, shutil, sys

FRONTPAGE = pathlib.Path(__file__).resolve().parent / "frontpage.png"
ENTRY_NAME = "entry.png"
FALLBACK_DIR = "/output"


def run():
    """Copy frontpage.png into the grader's output directory."""
    if not FRONTPAGE.exists():
        print("front page image is missing: " + str(FRONTPAGE))
        return 1
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR
    target_dir = pathlib.Path(wanted)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / ENTRY_NAME
        with FRONTPAGE.open("rb") as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    except OSError as err:
        print("cannot write the entry image: " + str(err))
        return 1
    if target.stat().st_size != FRONTPAGE.stat().st_size:
        print("copy stopped short: " + str(target))
        return 1
    print("entry written to " + str(target))
    return 0


if __name__ == "__main__":
    sys.exit(run())
