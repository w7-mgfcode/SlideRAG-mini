#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Validate a draft skill brief for completeness against complexity tier rules.

Usage:
    uv run scripts/validate_brief.py --brief <path> --tier <simple|moderate|complex>

Output (stdout): JSON with keys: complete (bool), missing_fields (list), warnings (list)
Exit codes: 0 = complete, 1 = incomplete, 2 = file/parse error
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # Fall back to basic parsing


# --- Tier requirements ---

REQUIRED_FIELDS = {
    "simple": {
        "section_1": ["name", "domain", "one_liner"],
        "section_2": ["triggers", "exclusions"],
        "section_4": ["complexity_tier"],
    },
    "moderate": {
        "section_1": ["name", "domain", "one_liner"],
        "section_2": ["triggers", "exclusions"],
        "section_3": ["workflow_type", "phases"],
        "section_4": [
            "complexity_tier",
            "has_conditional_routing",
            "has_loop_back",
            "has_state_management",
            "autonomous",
        ],
    },
    "complex": {
        "section_1": ["name", "domain", "one_liner"],
        "section_2": ["triggers", "exclusions"],
        "section_3": ["workflow_type", "phases"],
        "section_4": [
            "complexity_tier",
            "has_conditional_routing",
            "has_loop_back",
            "has_state_management",
            "autonomous",
        ],
        "section_5": ["tools_needed", "runtime_dependencies"],
        "section_6": ["output_files"],
    },
}

RECOMMENDED_FIELDS = {
    "simple": {},
    "moderate": {
        "section_5": ["tools_needed"],
        "section_6": ["scripts_needed"],
    },
    "complex": {
        "section_6": ["scripts_needed", "references_needed"],
        "section_7": ["safety_rules"],
    },
}

FIELD_VALIDATORS = {
    "name": lambda v: isinstance(v, str) and len(v) <= 64 and v == v.lower() and " " not in v,
    "domain": lambda v: isinstance(v, str) and len(v.strip()) > 0,
    "one_liner": lambda v: isinstance(v, str) and len(v.strip()) > 10,
    "triggers": lambda v: isinstance(v, list) and len(v) >= 3,
    "exclusions": lambda v: isinstance(v, list) and len(v) >= 2,
    "workflow_type": lambda v: isinstance(v, str) and v in ("linear", "multi-phase", "iterative-loop", "event-driven", "orchestrator"),
    "phases": lambda v: isinstance(v, list) and len(v) >= 2,
    "complexity_tier": lambda v: isinstance(v, str) and len(v.strip()) > 0,
}


def parse_yaml_file(path: Path) -> dict:
    """Parse a YAML file into a dict. Uses PyYAML if available, else basic parsing."""
    text = path.read_text(encoding="utf-8")

    if yaml is not None:
        # Handle multi-document YAML (--- separators)
        docs = list(yaml.safe_load_all(text))
        result = {}
        for doc in docs:
            if isinstance(doc, dict):
                result.update(doc)
        return result

    # Basic fallback: find key-value pairs at top level
    result = {}
    current_key = None
    current_list = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "---" or not stripped:
            continue
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            result[current_key] = current_list
        elif ":" in stripped:
            if current_list is not None:
                current_list = None
            key, _, val = stripped.partition(":")
            current_key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val and val != ">":
                result[current_key] = val
    return result


def flatten_brief(data: dict) -> dict:
    """Flatten nested brief structure into a flat field map."""
    flat = {}
    for key, val in data.items():
        if isinstance(val, dict):
            flat.update(val)
        else:
            flat[key] = val
    return flat


def validate(brief_path: Path, tier: str) -> dict:
    """Validate brief and return result dict."""
    if tier not in REQUIRED_FIELDS:
        return {
            "complete": False,
            "missing_fields": [],
            "warnings": [f"Unknown tier '{tier}'. Use: simple, moderate, complex"],
        }

    try:
        data = parse_yaml_file(brief_path)
    except Exception as e:
        return {
            "complete": False,
            "missing_fields": [],
            "warnings": [f"Failed to parse {brief_path}: {e}"],
        }

    flat = flatten_brief(data)
    missing = []
    warnings = []

    # Check required fields
    for section, fields in REQUIRED_FIELDS[tier].items():
        for field in fields:
            val = flat.get(field)
            if val is None or val == "" or val == "TBD":
                missing.append(f"{section}.{field}")
            elif field in FIELD_VALIDATORS and not FIELD_VALIDATORS[field](val):
                warnings.append(f"{section}.{field}: value fails validation (got: {repr(val)[:60]})")

    # Check recommended fields
    for section, fields in RECOMMENDED_FIELDS.get(tier, {}).items():
        for field in fields:
            val = flat.get(field)
            if val is None or val == "" or val == "TBD":
                warnings.append(f"{section}.{field}: recommended but missing")

    # Phase-specific validation for moderate+
    if tier in ("moderate", "complex"):
        phases = flat.get("phases", [])
        if isinstance(phases, list):
            for i, phase in enumerate(phases):
                if isinstance(phase, dict):
                    for req in ("name", "description", "inputs", "outputs", "validation"):
                        if req not in phase or not phase[req]:
                            warnings.append(f"phase[{i}].{req}: missing in phase definition")

    # Inferred field detection
    for key, val in flat.items():
        if isinstance(val, str) and "[inferred]" in val:
            warnings.append(f"{key}: contains [inferred] marker — user should review")

    return {
        "complete": len(missing) == 0,
        "missing_fields": missing,
        "warnings": warnings,
    }


def score_brief(brief_path: Path, tier: str) -> dict:
    """Score a brief on five quality dimensions (each 0-10). Returns per-dimension
    scores, weights, and a weighted total."""

    try:
        data = parse_yaml_file(brief_path)
    except Exception as e:
        return {"error": f"Failed to parse {brief_path}: {e}", "total": 0}

    flat = flatten_brief(data)
    required = REQUIRED_FIELDS.get(tier, REQUIRED_FIELDS["moderate"])
    dimensions = {}

    # --- 1. Field specificity (25%) ---
    specificity_scores = []
    for field_list in required.values():
        for field in field_list:
            val = flat.get(field)
            if val is None or val == "" or val == "TBD":
                specificity_scores.append(0)
            elif isinstance(val, str) and len(val.strip()) <= 5:
                specificity_scores.append(3)  # too short / vague
            elif isinstance(val, str) and "[from URL]" in val:
                specificity_scores.append(7)  # sourced from URL — concrete but not user-stated
            elif isinstance(val, str) and "[inferred]" in val:
                specificity_scores.append(5)  # present but inferred
            elif isinstance(val, list) and len(val) <= 1:
                specificity_scores.append(4)
            else:
                specificity_scores.append(10)
    dimensions["field_specificity"] = {
        "score": round(sum(specificity_scores) / max(len(specificity_scores), 1), 1),
        "weight": 0.25,
    }

    # --- 2. Trigger realism (20%) ---
    triggers = flat.get("triggers", [])
    exclusions = flat.get("exclusions", [])
    trigger_score = 10
    if not isinstance(triggers, list) or len(triggers) < 3:
        trigger_score -= 4
    elif len(triggers) < 5:
        trigger_score -= 1
    # Penalize very short triggers (likely too generic)
    if isinstance(triggers, list):
        short = sum(1 for t in triggers if isinstance(t, str) and len(t.split()) <= 2)
        if short > len(triggers) / 2:
            trigger_score -= 3
    if not isinstance(exclusions, list) or len(exclusions) < 2:
        trigger_score -= 3
    dimensions["trigger_realism"] = {
        "score": max(0, min(10, trigger_score)),
        "weight": 0.20,
    }

    # --- 3. Phase boundary clarity (20%) ---
    phases = flat.get("phases", [])
    phase_score = 10
    if not isinstance(phases, list) or len(phases) < 2:
        phase_score = 2
    elif isinstance(phases, list):
        for phase in phases:
            if isinstance(phase, dict):
                if not phase.get("validation"):
                    phase_score -= 2
                if not phase.get("inputs") or not phase.get("outputs"):
                    phase_score -= 1
    dimensions["phase_boundary_clarity"] = {
        "score": max(0, min(10, phase_score)),
        "weight": 0.20,
    }

    # --- 4. Completeness (20%) ---
    total_required = sum(len(fields) for fields in required.values())
    filled = 0
    inferred = 0
    from_url = 0
    for field_list in required.values():
        for field in field_list:
            val = flat.get(field)
            if val is None or val == "" or val == "TBD":
                continue
            elif isinstance(val, str) and "[from URL]" in val:
                from_url += 1
            elif isinstance(val, str) and "[inferred]" in val:
                inferred += 1
            else:
                filled += 1
    # URL-derived counts at 0.7 weight (concrete source), inferred at 0.5
    completeness_raw = (filled + from_url * 0.7 + inferred * 0.5) / max(total_required, 1) * 10
    dimensions["completeness"] = {
        "score": round(min(10, completeness_raw), 1),
        "weight": 0.20,
    }

    # --- 5. Safety coverage (15%) ---
    safety_rules = flat.get("safety_rules", [])
    restricted = flat.get("restricted_paths", [])
    sensitivity = flat.get("data_sensitivity")
    safety_score = 5  # baseline
    if isinstance(safety_rules, list) and len(safety_rules) >= 2:
        safety_score += 2
    if isinstance(safety_rules, list) and len(safety_rules) >= 4:
        safety_score += 1
    if isinstance(restricted, list) and len(restricted) >= 2:
        safety_score += 1
    if sensitivity and sensitivity != "TBD":
        safety_score += 1
    # For complex tier, demand more
    if tier == "complex" and (not isinstance(safety_rules, list) or len(safety_rules) < 3):
        safety_score -= 3
    dimensions["safety_coverage"] = {
        "score": max(0, min(10, safety_score)),
        "weight": 0.15,
    }

    # --- Weighted total ---
    total = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {
        "total": round(total, 1),
        "dimensions": {k: {"score": v["score"], "weight": v["weight"]} for k, v in dimensions.items()},
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate a draft skill brief for completeness against tier rules."
    )
    parser.add_argument("--brief", required=True, help="Path to the draft brief YAML file")
    parser.add_argument(
        "--tier",
        required=True,
        choices=["simple", "moderate", "complex"],
        help="Target complexity tier",
    )
    parser.add_argument(
        "--score",
        action="store_true",
        help="Include a quality score (1-10) with per-dimension breakdown",
    )
    args = parser.parse_args()

    brief_path = Path(args.brief)
    if not brief_path.exists():
        result = {
            "complete": False,
            "missing_fields": [],
            "warnings": [f"File not found: {brief_path}"],
        }
        json.dump(result, sys.stdout, indent=2)
        print()
        sys.exit(2)

    result = validate(brief_path, args.tier)

    if args.score:
        result["quality_score"] = score_brief(brief_path, args.tier)

    json.dump(result, sys.stdout, indent=2)
    print()
    sys.exit(0 if result["complete"] else 1)


if __name__ == "__main__":
    main()
