"""Verify the browser track's Climb Notes against the notebooks they derive from.

Why this exists
---------------
The browser track and the notebook track set the same tasks and mint the same
completion code, so they must also *teach* the same things — style guide rule 6
("a learner who moves from the site to a notebook should not feel they changed
teachers"). They drifted anyway: the browser track shipped twelve graded tasks
carrying 772 words of prose against the notebooks' 14,942, and the only place it
ever explained the Hadamard gate was hint rung 2 of task 01-1 — reachable only by
declaring yourself stuck. Recovery had become first delivery.

`website/assets/data/lessons.json` fixes that by giving the browser track a
narrative spine. This script is what stops it drifting again. It is a *checker*,
not a generator: rewriting notebook prose for the web is editorial work, and a
script that pretended to do it would produce confident nonsense. So the prose is
authored, and the machine enforces the two invariants that actually matter:

  1. **Derivation still holds.** Each beat names the notebook section it came
     from and a few anchor phrases. If a notebook is rewritten and those phrases
     vanish, the beat is now telling a story its source no longer tells.

  2. **Concept before task** (style guide rule 10). Every concept a task
     `requires` must appear in the `teaches` list of a beat that renders
     *before* it. This is the rule whose absence let the original problem
     through review, and it is the reason this file is wired into CI.

Usage
-----
    python tools/build_lessons.py          # report; exit 1 if anything is wrong
    python tools/build_lessons.py --quiet  # exit code only

`tests/test_lessons.py` calls `verify()` directly.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LESSONS = REPO / "website" / "assets" / "data" / "lessons.json"
MODULES = REPO / "website" / "assets" / "data" / "modules.json"
LABTASKS = REPO / "website" / "assets" / "js" / "labtasks.js"


def _notebook_text(rel: str) -> str:
    """All source of a notebook, flattened, for anchor-phrase checking."""
    nb = json.loads((REPO / rel).read_text(encoding="utf-8"))
    return " ".join("".join(c["source"]) for c in nb["cells"])


def _task_ids(module_id: str) -> list[str]:
    """Task ids declared in labtasks.js for a module, in order."""
    js = LABTASKS.read_text(encoding="utf-8")
    return re.findall(r'id:\s*"(%s-\d+)"' % re.escape(module_id), js)


def verify() -> list[str]:
    """Return a list of human-readable problems. Empty list means healthy."""
    problems: list[str] = []

    if not LESSONS.exists():
        return ["lessons.json is missing — the browser track has no narrative."]

    lessons = json.loads(LESSONS.read_text(encoding="utf-8"))
    module_ids = {m["id"] for m in json.loads(MODULES.read_text(encoding="utf-8"))["modules"]}
    nb_cache: dict[str, str] = {}

    for mod_id, mod in sorted(lessons.items()):
        if mod_id.startswith("_"):
            continue  # commentary key
        if mod_id not in module_ids:
            problems.append(f"[{mod_id}] not a real basecamp (not in modules.json)")
            continue

        beats = mod.get("beats", [])
        task_ids = _task_ids(mod_id)
        if not task_ids:
            problems.append(f"[{mod_id}] no tasks found in labtasks.js")
            continue

        # --- 1. every beat is anchored somewhere real -----------------------
        for b in beats:
            where = b.get("before")
            if where != "end" and where not in task_ids:
                problems.append(
                    f"[{mod_id}/{b['id']}] before='{where}' is not a task id "
                    f"(have {task_ids} or 'end')"
                )
            if not b.get("html", "").strip():
                problems.append(f"[{mod_id}/{b['id']}] has no body text")

            src = b.get("source", "")
            rel = src.split(" ")[0] if src else ""
            if not rel or not (REPO / rel).exists():
                problems.append(f"[{mod_id}/{b['id']}] source notebook not found: {src!r}")
                continue

            if rel not in nb_cache:
                nb_cache[rel] = _notebook_text(rel)
            text = nb_cache[rel]
            for phrase in b.get("anchors", []):
                if phrase.lower() not in text.lower():
                    problems.append(
                        f"[{mod_id}/{b['id']}] anchor {phrase!r} no longer appears in "
                        f"{rel} — the beat and its source notebook have drifted"
                    )

        # --- 2. concept before task (style guide rule 10) -------------------
        taught_by_now: set[str] = set()
        beats_before = {t: [b for b in beats if b.get("before") == t] for t in task_ids}
        requires = mod.get("requires", {})

        for tid in task_ids:
            for b in beats_before[tid]:
                taught_by_now |= set(b.get("teaches", []))
            for concept in requires.get(tid, []):
                if concept not in taught_by_now:
                    problems.append(
                        f"[{mod_id}/{tid}] requires {concept!r} but no beat before it "
                        f"teaches it — a learner meets this task cold"
                    )

        # A task with no declared requirements is not proof of safety, it is an
        # unfilled contract. Say so, rather than passing silently.
        for tid in task_ids:
            if tid not in requires:
                problems.append(
                    f"[{mod_id}/{tid}] has no `requires` entry — declare what it "
                    f"assumes, or rule 10 is unenforced for this task"
                )

    return problems


def main() -> int:
    # Windows consoles default to cp1252, which cannot encode the ✓/✗ glyphs.
    # Without this the tool crashes on the report rather than on the content.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover — non-standard stdout
        pass

    quiet = "--quiet" in sys.argv
    problems = verify()

    if not quiet:
        lessons = json.loads(LESSONS.read_text(encoding="utf-8")) if LESSONS.exists() else {}
        narrated = [k for k in lessons if not k.startswith("_")]
        all_mods = [m["id"] for m in json.loads(MODULES.read_text(encoding="utf-8"))["modules"]]
        for mid in all_mods:
            if mid in narrated:
                beats = lessons[mid].get("beats", [])
                words = sum(len(re.sub(r"<[^>]+>", " ", b.get("html", "")).split()) for b in beats)
                print(f"  basecamp {mid}  {len(beats)} beats · ~{words} words")
            else:
                print(f"  basecamp {mid}  — no climb notes yet (renders as tasks only)")
        print()

    if problems:
        print(f"✗ {len(problems)} problem(s):")
        for p in problems:
            print("   -", p)
        return 1

    print("✓ climb notes verified: sources intact, no task met cold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
