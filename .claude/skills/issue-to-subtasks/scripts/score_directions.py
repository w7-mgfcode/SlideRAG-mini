#!/usr/bin/env python3
"""
score_directions.py

Deterministically rerank candidate directions or subtask orderings against the
7-dimension rubric defined in references/scoring-rubric.md.

Input (stdin, JSON):
  {
    "candidates": [
      {
        "id": "direction-A",
        "name": "Refactor X first, then add Y",
        "scores": {
          "value": 4,
          "risk": 3,            # higher input means MORE risk; we invert
          "readiness": 5,
          "dependency_load": 2, # higher input means MORE deps; we invert
          "validation_ease": 4,
          "rollback_safety": 5,
          "evidence_strength": 4
        }
      }
    ],
    "weights": {                 # optional; defaults all to 1.0
      "value": 1.5,
      "risk": 1.0,
      "readiness": 1.0,
      "dependency_load": 1.0,
      "validation_ease": 1.0,
      "rollback_safety": 1.0,
      "evidence_strength": 1.5
    }
  }

Output (stdout, JSON):
  {
    "ranked": [
      {
        "id": "direction-A",
        "name": "...",
        "weighted_score": 4.21,
        "raw_scores": {...},
        "rank": 1
      },
      ...
    ],
    "table_markdown": "| Rank | ... |\n..."
  }

All scores must be 1-5 integers. Risk and dependency_load are INVERTED before
weighting (so the user provides "amount of risk" and the system rewards lower).
"""

from __future__ import annotations

import json
import sys
from typing import Any

DIMENSIONS = [
    "value",
    "risk",
    "readiness",
    "dependency_load",
    "validation_ease",
    "rollback_safety",
    "evidence_strength",
]
INVERTED = {"risk", "dependency_load"}
DEFAULT_WEIGHTS = {dim: 1.0 for dim in DIMENSIONS}


def validate_candidate(cand: dict[str, Any]) -> None:
    if "id" not in cand or "scores" not in cand:
        raise ValueError(f"candidate missing 'id' or 'scores': {cand}")
    for dim in DIMENSIONS:
        if dim not in cand["scores"]:
            raise ValueError(f"candidate {cand['id']} missing dimension '{dim}'")
        v = cand["scores"][dim]
        if not isinstance(v, int) or not (1 <= v <= 5):
            raise ValueError(
                f"candidate {cand['id']} dimension '{dim}' must be int in [1,5], got {v!r}"
            )


def weighted_score(scores: dict[str, int], weights: dict[str, float]) -> float:
    total = 0.0
    weight_sum = 0.0
    for dim in DIMENSIONS:
        raw = scores[dim]
        # Invert risk and dependency_load so high "amount" → low contribution
        effective = (6 - raw) if dim in INVERTED else raw
        w = weights.get(dim, 1.0)
        total += effective * w
        weight_sum += w
    return round(total / weight_sum, 3) if weight_sum > 0 else 0.0


def render_table(ranked: list[dict[str, Any]]) -> str:
    lines = [
        "| Rank | ID | Name | Score | Value | Risk | Ready | DepLoad | Validate | Rollback | Evidence |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in ranked:
        s = r["raw_scores"]
        name = r.get("name", "").replace("|", "\\|")
        lines.append(
            f"| {r['rank']} | {r['id']} | {name} | {r['weighted_score']:.2f} | "
            f"{s['value']} | {s['risk']} | {s['readiness']} | "
            f"{s['dependency_load']} | {s['validation_ease']} | "
            f"{s['rollback_safety']} | {s['evidence_strength']} |"
        )
    return "\n".join(lines)


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        sys.stderr.write(
            "ERROR: no input on stdin. Pipe a JSON object with 'candidates'.\n"
        )
        return 2

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"ERROR: invalid JSON: {e}\n")
        return 2

    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        sys.stderr.write("ERROR: input must contain a non-empty 'candidates' list.\n")
        return 2

    weights = {**DEFAULT_WEIGHTS, **data.get("weights", {})}

    for cand in candidates:
        validate_candidate(cand)

    scored = [
        {
            "id": c["id"],
            "name": c.get("name", c["id"]),
            "weighted_score": weighted_score(c["scores"], weights),
            "raw_scores": c["scores"],
        }
        for c in candidates
    ]
    scored.sort(key=lambda x: x["weighted_score"], reverse=True)
    for i, item in enumerate(scored, start=1):
        item["rank"] = i

    output = {
        "ranked": scored,
        "table_markdown": render_table(scored),
        "weights_used": weights,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
