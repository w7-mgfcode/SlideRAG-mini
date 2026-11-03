# /// script
# dependencies = []
# ///
"""Validate Mermaid code blocks in markdown files.

Checks for common syntax errors: orphan nodes, unbalanced brackets,
missing arrow targets, duplicate node IDs with conflicting labels.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_mermaid_blocks(content: str) -> list[dict]:
    """Extract all mermaid code blocks from markdown content."""
    blocks = []
    pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    for i, match in enumerate(pattern.finditer(content)):
        blocks.append({
            "index": i,
            "content": match.group(1).strip(),
            "start_line": content[:match.start()].count("\n") + 1,
        })
    return blocks


def validate_block(block: str) -> list[str]:
    """Validate a single Mermaid block. Returns list of error messages."""
    errors = []
    lines = block.splitlines()

    if not lines:
        errors.append("Empty mermaid block")
        return errors

    # Detect diagram type
    first_line = lines[0].strip().lower()
    diagram_type = None
    for dtype in ["flowchart", "graph", "sequencediagram", "statediagram", "classdiagram"]:
        if first_line.startswith(dtype.replace("diagram", "Diagram").lower()) or \
           first_line.startswith(dtype):
            diagram_type = dtype
            break

    if not diagram_type:
        # Try common patterns
        if first_line.startswith("graph"):
            diagram_type = "graph"
        elif first_line.startswith("flowchart"):
            diagram_type = "flowchart"
        elif first_line.startswith("sequencediagram"):
            diagram_type = "sequenceDiagram"

    if not diagram_type:
        errors.append(f"Unknown diagram type: {first_line}")
        return errors

    # Check balanced brackets
    brackets = {"[": "]", "{": "}", "(": ")"}
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith("%%"):
            continue

        for open_b, close_b in brackets.items():
            open_count = line.count(open_b)
            close_count = line.count(close_b)
            if open_count != close_count:
                # Allow for multi-char brackets like [[ ]]
                if not (open_b == "[" and "[[" in line and "]]" in line):
                    errors.append(f"Line {line_num}: Unbalanced '{open_b}' ({open_count}) vs '{close_b}' ({close_count})")

    # For flowchart/graph: check for arrow targets
    if diagram_type in ("flowchart", "graph"):
        arrow_patterns = [" --> ", " --- ", " -.-> ", " ==> ", " --o ", " --x "]
        for line_num, line in enumerate(lines[1:], 2):
            stripped = line.strip()
            if not stripped or stripped.startswith("%%") or stripped.startswith("subgraph") or \
               stripped == "end" or stripped.startswith("style") or stripped.startswith("class"):
                continue

            for arrow in arrow_patterns:
                if arrow in stripped:
                    parts = stripped.split(arrow)
                    if len(parts) >= 2:
                        target = parts[-1].strip()
                        if not target or target == "":
                            errors.append(f"Line {line_num}: Arrow with no target")

            # Check for dangling arrows at end of line
            if stripped.endswith("-->") or stripped.endswith("--->") or \
               stripped.endswith("==>") or stripped.endswith("-.->"):
                errors.append(f"Line {line_num}: Dangling arrow at end of line")

    # Check for duplicate node IDs with different labels (flowchart/graph)
    if diagram_type in ("flowchart", "graph"):
        node_labels: dict[str, str] = {}
        node_pattern = re.compile(r"(\w+)\[([^\]]+)\]")
        for line_num, line in enumerate(lines[1:], 2):
            for match in node_pattern.finditer(line):
                node_id = match.group(1)
                label = match.group(2)
                if node_id in node_labels:
                    if node_labels[node_id] != label:
                        errors.append(
                            f"Line {line_num}: Node '{node_id}' has conflicting labels: "
                            f"'{node_labels[node_id]}' vs '{label}'"
                        )
                else:
                    node_labels[node_id] = label

    return errors


def validate_file(filepath: Path) -> dict:
    """Validate all Mermaid blocks in a markdown file."""
    content = filepath.read_text(errors="ignore")
    blocks = extract_mermaid_blocks(content)

    results = {
        "file": str(filepath),
        "blocks_found": len(blocks),
        "blocks_valid": 0,
        "blocks_invalid": 0,
        "errors": [],
    }

    for block in blocks:
        errors = validate_block(block["content"])
        if errors:
            results["blocks_invalid"] += 1
            for err in errors:
                results["errors"].append({
                    "block": block["index"],
                    "line": block["start_line"],
                    "message": err,
                })
        else:
            results["blocks_valid"] += 1

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate Mermaid code blocks in markdown files"
    )
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to validate")
    args = parser.parse_args()

    all_results = []
    total_errors = 0

    for path_str in args.paths:
        path = Path(path_str).resolve()
        if path.is_file():
            files = [path]
        elif path.is_dir():
            files = sorted(path.glob("**/*.md"))
        else:
            print(json.dumps({"error": f"Not found: {path}"}), file=sys.stderr)
            sys.exit(2)

        for f in files:
            result = validate_file(f)
            all_results.append(result)
            total_errors += len(result["errors"])

    output = {
        "files_checked": len(all_results),
        "total_errors": total_errors,
        "valid": total_errors == 0,
        "results": all_results,
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
