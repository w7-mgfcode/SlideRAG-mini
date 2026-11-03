# /// script
# dependencies = []
# ///
"""Compare current analysis output vs previous (.prev/) for incremental mode.

Produces a structured diff showing added, removed, and changed sections.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def read_file_safe(path: Path) -> str:
    """Read a file, returning empty string on failure."""
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def extract_sections(content: str) -> dict[str, str]:
    """Extract markdown sections (## headings) from content."""
    sections = {}
    current_heading = "__preamble__"
    current_lines = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line.strip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections


def diff_file(current_path: Path, previous_path: Path) -> dict:
    """Diff a single file between current and previous versions."""
    current = read_file_safe(current_path)
    previous = read_file_safe(previous_path)

    if not previous:
        return {"status": "new", "sections_added": list(extract_sections(current).keys())}

    if not current:
        return {"status": "removed"}

    if current == previous:
        return {"status": "unchanged"}

    cur_sections = extract_sections(current)
    prev_sections = extract_sections(previous)

    added = [s for s in cur_sections if s not in prev_sections]
    removed = [s for s in prev_sections if s not in cur_sections]
    changed = [
        s for s in cur_sections
        if s in prev_sections and cur_sections[s] != prev_sections[s]
    ]

    return {
        "status": "modified",
        "sections_added": added,
        "sections_removed": removed,
        "sections_changed": changed,
        "sections_unchanged": [
            s for s in cur_sections
            if s in prev_sections and cur_sections[s] == prev_sections[s]
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compare current vs previous analysis output"
    )
    parser.add_argument("--current", required=True, help="Path to current analysis dir")
    parser.add_argument("--previous", required=True, help="Path to previous analysis dir")
    args = parser.parse_args()

    current_dir = Path(args.current).resolve()
    previous_dir = Path(args.previous).resolve()

    if not current_dir.is_dir():
        print(json.dumps({"error": f"Not a directory: {current_dir}"}), file=sys.stderr)
        sys.exit(2)

    if not previous_dir.is_dir():
        print(json.dumps({"error": f"Not a directory: {previous_dir}"}), file=sys.stderr)
        sys.exit(2)

    # Collect all markdown files from both directories
    current_files = {f.name for f in current_dir.glob("*.md")}
    previous_files = {f.name for f in previous_dir.glob("*.md")}
    all_files = current_files | previous_files

    results = {
        "added": [],
        "removed": [],
        "changed": [],
        "unchanged": [],
        "file_diffs": {},
        "summary": "",
    }

    for filename in sorted(all_files):
        cur_path = current_dir / filename
        prev_path = previous_dir / filename

        if filename in current_files and filename not in previous_files:
            results["added"].append(filename)
            results["file_diffs"][filename] = {"status": "new"}
        elif filename not in current_files and filename in previous_files:
            results["removed"].append(filename)
            results["file_diffs"][filename] = {"status": "removed"}
        else:
            diff = diff_file(cur_path, prev_path)
            results["file_diffs"][filename] = diff
            if diff["status"] == "modified":
                results["changed"].append(filename)
            elif diff["status"] == "unchanged":
                results["unchanged"].append(filename)

    total = len(all_files)
    results["summary"] = (
        f"{len(results['added'])} new, {len(results['removed'])} removed, "
        f"{len(results['changed'])} modified, {len(results['unchanged'])} unchanged "
        f"out of {total} files"
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
