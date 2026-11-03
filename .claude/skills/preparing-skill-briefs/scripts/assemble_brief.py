#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Assemble interview answers into a formatted skill brief with tier-appropriate defaults.

Usage:
    uv run scripts/assemble_brief.py --answers <path> --tier <simple|moderate|complex> --output <path>

Output (stdout): JSON with keys: output_path, fields_filled, fields_defaulted
Exit codes: 0 = success, 1 = assembly error, 2 = file/parse error
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# --- Default values by tier ---

TIER_DEFAULTS = {
    "simple": {
        "workflow_type": "linear",
        "phases": [
            {
                "name": "Execute",
                "description": "Run the core operation",
                "inputs": "User request",
                "outputs": "Operation result",
                "validation": "Output exists and is non-empty",
            },
            {
                "name": "Report",
                "description": "Summarize the outcome",
                "inputs": "Operation result",
                "outputs": "Summary message",
                "validation": "User informed of result",
            },
        ],
        "complexity_tier": "simple (2)",
        "has_conditional_routing": "no",
        "has_loop_back": "no",
        "has_state_management": "no",
        "has_external_dependencies": "no",
        "autonomous": "no",
        "tools_needed": ["Read", "Write", "Bash", "Glob", "Grep"],
        "runtime_dependencies": ["Python 3.8+"],
        "compatibility": "Any Claude Code environment",
        "safety_rules": [
            "Never fabricate data or output",
            "Never run destructive commands without confirmation",
        ],
        "restricted_paths": [".git/", ".env", "secrets/"],
        "data_sensitivity": "low",
    },
    "moderate": {
        "complexity_tier": "moderate (5)",
        "has_external_dependencies": "no",
        "tools_needed": ["Read", "Write", "Bash", "Glob", "Grep"],
        "runtime_dependencies": ["Python 3.10+", "uv"],
        "compatibility": "Any Claude Code environment",
        "safety_rules": [
            "Never fabricate data or output",
            "Never run destructive commands without confirmation",
        ],
        "restricted_paths": [".git/", ".env", "secrets/"],
        "data_sensitivity": "low",
    },
    "complex": {
        "has_external_dependencies": "no",
        "tools_needed": ["Read", "Write", "Bash", "Glob", "Grep"],
        "runtime_dependencies": ["Python 3.10+", "uv"],
        "compatibility": "Any Claude Code environment",
        "restricted_paths": [".git/", ".env", "secrets/"],
        "data_sensitivity": "low",
    },
}

BRIEF_SECTIONS = [
    ("Section 1: Identity (required)", ["name", "domain", "one_liner"]),
    ("Section 2: Trigger Boundary", ["triggers", "exclusions"]),
    (
        "Section 3: Workflow Shape",
        ["workflow_type", "phases"],
    ),
    (
        "Section 4: Complexity Signals",
        [
            "complexity_tier",
            "has_conditional_routing",
            "has_loop_back",
            "has_state_management",
            "has_external_dependencies",
            "autonomous",
        ],
    ),
    ("Section 5: Tools & Environment", ["tools_needed", "runtime_dependencies", "compatibility"]),
    (
        "Section 6: Output Expectations",
        ["output_files", "scripts_needed", "templates_needed", "references_needed"],
    ),
    ("Section 7: Safety & Constraints", ["safety_rules", "restricted_paths", "data_sensitivity"]),
    ("Section 8: Reference Material (optional)", ["urls", "existing_skills", "prior_art"]),
]


def load_answers(path: Path) -> dict:
    """Load answers from YAML or JSON file."""
    text = path.read_text(encoding="utf-8")

    if path.suffix in (".json",):
        return json.loads(text)

    if HAS_YAML:
        docs = list(yaml.safe_load_all(text))
        result = {}
        for doc in docs:
            if isinstance(doc, dict):
                result.update(doc)
        return result

    # Basic key-value fallback
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "---" or not stripped:
            continue
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            val = val.strip().strip('"').strip("'")
            if val and val != ">":
                result[key.strip()] = val
    return result


def flatten(data: dict) -> dict:
    """Flatten nested structure."""
    flat = {}
    for key, val in data.items():
        if isinstance(val, dict):
            flat.update(val)
        else:
            flat[key] = val
    return flat


def format_value(val, indent: int = 2) -> str:
    """Format a value for YAML output."""
    prefix = " " * indent
    if isinstance(val, list):
        if not val:
            return "[]"
        lines = []
        for item in val:
            if isinstance(item, dict):
                lines.append(f"{prefix}- name: {json.dumps(item.get('name', ''))}")
                for k, v in item.items():
                    if k != "name":
                        lines.append(f"{prefix}  {k}: {json.dumps(str(v))}")
            else:
                lines.append(f"{prefix}- {json.dumps(str(item))}")
        return "\n" + "\n".join(lines)
    if isinstance(val, str) and "\n" in val:
        return f">\n{prefix}" + f"\n{prefix}".join(val.splitlines())
    if isinstance(val, str):
        return json.dumps(val)
    return str(val)


def _render(flat: dict, fmt: str, fields_defaulted: list, fields_from_url: list) -> str:
    """Render the brief in the requested format."""
    if fmt == "markdown":
        return _render_markdown(flat, fields_defaulted, fields_from_url)
    return _render_yaml(flat, fields_defaulted, fields_from_url)


def _render_yaml(flat: dict, fields_defaulted: list, fields_from_url: list) -> str:
    """Render as YAML."""
    lines = ["---", "# Skill Generator Input Brief", ""]
    for section_name, fields in BRIEF_SECTIONS:
        lines.append(f"### {section_name}")
        lines.append("")
        for field in fields:
            val = flat.get(field)
            if val is not None:
                formatted = format_value(val)
                if field in fields_defaulted:
                    lines.append(f"{field}: {formatted}  # [inferred]")
                elif field in fields_from_url:
                    lines.append(f"{field}: {formatted}  # [from URL]")
                else:
                    lines.append(f"{field}: {formatted}")
            else:
                lines.append(f"{field}: TBD")
        lines.append("")
    return "\n".join(lines)


def _render_markdown(flat: dict, fields_defaulted: list, fields_from_url: list) -> str:
    """Render as copy-pasteable Markdown."""
    lines = ["# Skill Generator Input Brief", ""]
    for section_name, fields in BRIEF_SECTIONS:
        lines.append(f"## {section_name}")
        lines.append("")
        for field in fields:
            val = flat.get(field)
            provenance = ""
            if field in fields_defaulted:
                provenance = " *(inferred)*"
            elif field in fields_from_url:
                provenance = " *(from URL)*"

            if val is None:
                lines.append(f"- **{field}:** TBD")
            elif isinstance(val, list):
                lines.append(f"- **{field}:**{provenance}")
                for item in val:
                    if isinstance(item, dict):
                        parts = ", ".join(f"{k}: {v}" for k, v in item.items())
                        lines.append(f"  - {parts}")
                    else:
                        lines.append(f"  - {item}")
            else:
                lines.append(f"- **{field}:** {val}{provenance}")
        lines.append("")
    return "\n".join(lines)


def assemble(answers: dict, tier: str, output_path: Path, fmt: str = "yaml") -> dict:
    """Assemble answers + defaults into a formatted brief."""
    flat = flatten(answers)
    defaults = TIER_DEFAULTS.get(tier, TIER_DEFAULTS["moderate"])
    fields_filled = []
    fields_defaulted = []

    fields_from_url = []

    for section_name, fields in BRIEF_SECTIONS:
        for field in fields:
            val = flat.get(field)

            if val is None or val == "" or val == "TBD":
                val = defaults.get(field)
                if val is not None:
                    flat[field] = val
                    fields_defaulted.append(field)
            elif isinstance(val, str) and "[from URL]" in val:
                fields_from_url.append(field)
                fields_filled.append(field)
            else:
                fields_filled.append(field)

    content = _render(flat, fmt, fields_defaulted, fields_from_url)

    # Atomic write
    dir_path = output_path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(dir_path), suffix=".yaml")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        os.replace(tmp, str(output_path))
    except Exception:
        os.close(fd)
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

    return {
        "output_path": str(output_path),
        "format": fmt,
        "fields_filled": len(fields_filled),
        "fields_defaulted": len(fields_defaulted),
        "fields_from_url": len(fields_from_url),
        "filled": fields_filled,
        "defaulted": fields_defaulted,
        "from_url": fields_from_url,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Assemble interview answers into a formatted skill brief."
    )
    parser.add_argument("--answers", required=True, help="Path to answers file (YAML or JSON)")
    parser.add_argument(
        "--tier",
        required=True,
        choices=["simple", "moderate", "complex"],
        help="Target complexity tier",
    )
    parser.add_argument("--output", required=True, help="Output path for assembled brief")
    parser.add_argument(
        "--format",
        choices=["yaml", "markdown"],
        default="yaml",
        help="Output format: yaml (default) or markdown (copy-pasteable)",
    )
    args = parser.parse_args()

    answers_path = Path(args.answers)
    if not answers_path.exists():
        result = {
            "output_path": args.output,
            "fields_filled": 0,
            "fields_defaulted": 0,
            "error": f"File not found: {answers_path}",
        }
        json.dump(result, sys.stdout, indent=2)
        print()
        sys.exit(2)

    try:
        answers = load_answers(answers_path)
    except Exception as e:
        result = {
            "output_path": args.output,
            "fields_filled": 0,
            "fields_defaulted": 0,
            "error": f"Failed to parse {answers_path}: {e}",
        }
        json.dump(result, sys.stdout, indent=2)
        print()
        sys.exit(2)

    try:
        result = assemble(answers, args.tier, Path(args.output), fmt=args.format)
        json.dump(result, sys.stdout, indent=2)
        print()
        sys.exit(0)
    except Exception as e:
        json.dump({"error": str(e)}, sys.stdout, indent=2)
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
