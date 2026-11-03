# /// script
# dependencies = []
# ///
"""Classify an AI/ML repository by type based on file tree patterns.

Detects: agent-framework, prompt-library, eval-harness, workflow-orchestrator, hybrid.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Repo type detection signals
SIGNALS = {
    "agent-framework": {
        "file_patterns": [
            "agent", "agents", "tools", "tool_use", "react", "chain",
            "llm", "chat", "completion", "memory", "retrieval",
        ],
        "import_patterns": [
            "langchain", "langgraph", "autogen", "crewai", "openai",
            "anthropic", "llamaindex", "haystack", "semantic_kernel",
            "claude_agent_sdk", "smolagents", "pydantic_ai", "instructor",
            "marvin", "mirascope", "agno",
        ],
        "config_files": ["agent.yaml", "agent.json", "agents.yaml", "tools.yaml"],
    },
    "prompt-library": {
        "file_patterns": [
            "prompt", "prompts", "template", "templates", "system_prompt",
            "few_shot", "examples", "instructions",
        ],
        "import_patterns": ["jinja2", "promptflow", "guidance", "dspy", "outlines", "lmql"],
        "config_files": ["prompts.yaml", "prompts.json", "templates.yaml"],
    },
    "eval-harness": {
        "file_patterns": [
            "eval", "evals", "benchmark", "benchmarks", "score", "scoring",
            "metric", "metrics", "test_suite", "harness", "judge",
        ],
        "import_patterns": [
            "pytest", "evaluate", "ragas", "deepeval", "promptfoo",
            "inspect_ai", "braintrust", "phoenix", "arize",
        ],
        "config_files": ["eval.yaml", "evals.yaml", "benchmark.yaml", "promptfooconfig.yaml"],
    },
    "workflow-orchestrator": {
        "file_patterns": [
            "workflow", "workflows", "pipeline", "pipelines", "dag",
            "orchestrat", "step", "steps", "phase", "stages", "flow",
        ],
        "import_patterns": [
            "prefect", "airflow", "dagster", "luigi", "celery",
            "temporal", "argo", "kubeflow", "hatchet", "inngest",
        ],
        "config_files": ["workflow.yaml", "pipeline.yaml", "dag.yaml", "flow.yaml"],
    },
}

# Minimum confidence threshold for a single-type classification
CONFIDENCE_THRESHOLD = 0.4
# If top two types are within this margin, classify as hybrid
HYBRID_MARGIN = 0.15


def scan_directory(repo_path: Path, max_depth: int = 4) -> dict:
    """Scan directory for classification signals."""
    results = {
        "files": [],
        "dirs": [],
        "readme_content": "",
        "package_files": [],
    }

    readme_names = {"README.md", "README.rst", "README.txt", "README"}
    package_names = {
        "package.json", "setup.py", "setup.cfg", "pyproject.toml",
        "Cargo.toml", "go.mod", "requirements.txt",
    }

    for root, dirs, files in os.walk(repo_path):
        depth = len(Path(root).relative_to(repo_path).parts)
        if depth > max_depth:
            dirs.clear()
            continue

        # Skip irrelevant directories
        dirs[:] = [
            d for d in dirs
            if d not in {
                ".git", "node_modules", "__pycache__", ".venv", "venv",
                ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
                ".next", ".nuxt",
            }
        ]

        rel_root = Path(root).relative_to(repo_path)
        for d in dirs:
            results["dirs"].append(str(rel_root / d))

        for f in files:
            rel_path = str(rel_root / f)
            results["files"].append(rel_path)

            if f in readme_names and depth <= 1:
                try:
                    content = (Path(root) / f).read_text(errors="ignore")[:5000]
                    results["readme_content"] = content
                except OSError:
                    pass

            if f in package_names:
                results["package_files"].append(rel_path)

    return results


def classify(scan: dict) -> dict:
    """Classify repo type based on scan results."""
    scores: dict[str, float] = {}
    matched_signals: dict[str, list[str]] = {}

    all_paths = " ".join(scan["files"] + scan["dirs"]).lower()
    readme = scan["readme_content"].lower()

    for repo_type, signals in SIGNALS.items():
        score = 0.0
        matches = []

        # Check file/dir name patterns
        for pattern in signals["file_patterns"]:
            if pattern in all_paths:
                score += 1.0
                matches.append(f"path:{pattern}")

        # Check import patterns (in README or package files)
        combined_text = readme
        for pf in scan["package_files"]:
            matches.append(f"pkg:{pf}")

        for pattern in signals["import_patterns"]:
            if pattern in combined_text or pattern in all_paths:
                score += 1.5
                matches.append(f"import:{pattern}")

        # Check config files
        file_basenames = {Path(f).name.lower() for f in scan["files"]}
        for config in signals["config_files"]:
            if config.lower() in file_basenames:
                score += 2.0
                matches.append(f"config:{config}")

        # Check README mentions
        for pattern in signals["file_patterns"][:3]:
            if pattern in readme:
                score += 0.5
                matches.append(f"readme:{pattern}")

        scores[repo_type] = score
        matched_signals[repo_type] = matches

    # Normalize scores
    total = sum(scores.values()) or 1.0
    normalized = {k: v / total for k, v in scores.items()}

    # Sort by score descending
    ranked = sorted(normalized.items(), key=lambda x: x[1], reverse=True)

    top_type, top_score = ranked[0]
    second_type, second_score = ranked[1] if len(ranked) > 1 else ("", 0.0)

    # Determine classification
    if top_score < CONFIDENCE_THRESHOLD and (top_score - second_score) < HYBRID_MARGIN:
        repo_type = "hybrid"
        confidence = top_score
        signals_used = matched_signals[top_type] + matched_signals[second_type]
    else:
        repo_type = top_type
        confidence = top_score
        signals_used = matched_signals[top_type]

    return {
        "repo_type": repo_type,
        "confidence": round(confidence, 3),
        "signals": signals_used[:20],
        "scores": {k: round(v, 3) for k, v in ranked},
        "file_count": len(scan["files"]),
        "dir_count": len(scan["dirs"]),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Classify an AI/ML repository by type"
    )
    parser.add_argument("--path", required=True, help="Path to the repository")
    args = parser.parse_args()

    repo_path = Path(args.path).resolve()
    if not repo_path.is_dir():
        print(json.dumps({"error": f"Not a directory: {repo_path}"}), file=sys.stderr)
        sys.exit(2)

    scan = scan_directory(repo_path)
    result = classify(scan)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
