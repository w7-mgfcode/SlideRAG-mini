# /// script
# dependencies = []
# ///
"""Build a filtered, relevance-scored file tree for an AI/ML repository.

Produces a ranked list of key files for deep analysis, filtered by repo type.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Priority directories by repo type
PRIORITY_DIRS = {
    "agent-framework": [
        "src", "lib", "agents", "tools", "chains", "memory",
        "retrieval", "llm", "core", "api",
    ],
    "prompt-library": [
        "prompts", "templates", "examples", "instructions",
        "src", "lib", "core",
    ],
    "eval-harness": [
        "evals", "eval", "benchmarks", "tests", "scoring",
        "metrics", "judges", "src", "lib",
    ],
    "workflow-orchestrator": [
        "workflows", "pipelines", "dags", "flows", "steps",
        "orchestration", "src", "lib", "core",
    ],
    "hybrid": [
        "src", "lib", "core", "agents", "workflows", "prompts",
        "evals", "tools", "api",
    ],
}

# High-value file patterns (always relevant)
HIGH_VALUE_FILES = {
    "README.md", "README.rst",
    "pyproject.toml", "setup.py", "setup.cfg", "package.json",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "config.yaml", "config.json", "settings.py",
}

# Extensions to include
INCLUDE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
    ".yaml", ".yml", ".json", ".toml", ".md", ".txt",
    ".sh", ".bash", ".cfg", ".ini", ".env.example",
}

# Directories to always skip
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", ".cache", ".eggs", "*.egg-info",
    "vendor", "third_party", ".terraform",
}


def score_file(filepath: str, repo_type: str, file_size: int) -> float:
    """Score a file's relevance for analysis."""
    score = 0.0
    path = Path(filepath)
    name = path.name
    parts = set(path.parts)

    # High-value files get a boost
    if name in HIGH_VALUE_FILES:
        score += 5.0

    # Entry point patterns
    entry_patterns = ["main", "app", "index", "cli", "run", "__main__", "server"]
    stem = path.stem.lower()
    if stem in entry_patterns:
        score += 4.0

    # Priority directory match
    priority = PRIORITY_DIRS.get(repo_type, PRIORITY_DIRS["hybrid"])
    for i, pdir in enumerate(priority):
        if pdir in parts:
            score += 3.0 - (i * 0.2)
            break

    # Depth penalty (shallow files are more important)
    depth = len(path.parts)
    score -= depth * 0.3

    # Size bonus (moderate files are more useful than tiny or huge)
    if 100 < file_size < 50000:
        score += 1.0
    elif file_size > 100000:
        score -= 1.0

    # Config/schema files get a boost
    config_stems = {"config", "settings", "schema", "types", "constants", "env"}
    if stem in config_stems:
        score += 2.0

    # Test files get a mild boost (useful for understanding behavior)
    if "test" in stem or "spec" in stem:
        score += 0.5

    return round(score, 2)


def build_tree(repo_path: Path, repo_type: str, max_files: int = 500) -> dict:
    """Build filtered file tree with relevance scoring."""
    files = []
    skipped = 0
    total_scanned = 0

    for root, dirs, filenames in os.walk(repo_path):
        # Skip irrelevant directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in filenames:
            total_scanned += 1
            full_path = Path(root) / f
            rel_path = str(full_path.relative_to(repo_path))

            # Filter by extension
            ext = full_path.suffix.lower()
            if ext not in INCLUDE_EXTENSIONS and f not in HIGH_VALUE_FILES:
                skipped += 1
                continue

            # Get file size
            try:
                size = full_path.stat().st_size
            except OSError:
                skipped += 1
                continue

            # Skip empty files
            if size == 0:
                skipped += 1
                continue

            relevance = score_file(rel_path, repo_type, size)
            files.append({
                "path": rel_path,
                "size": size,
                "relevance": relevance,
            })

    # Sort by relevance descending
    files.sort(key=lambda x: x["relevance"], reverse=True)

    # Cap at max_files
    key_files = files[:max_files]

    return {
        "tree": [f["path"] for f in key_files],
        "key_files": [f["path"] for f in key_files[:50]],
        "stats": {
            "total_scanned": total_scanned,
            "included": len(key_files),
            "skipped": skipped,
            "capped": len(files) > max_files,
        },
        "scored_files": key_files[:50],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build filtered file tree with relevance scoring"
    )
    parser.add_argument("--path", required=True, help="Path to the repository")
    parser.add_argument("--type", required=True, help="Repo type from classify_repo.py")
    parser.add_argument("--max-files", type=int, default=500, help="Max files to include")
    args = parser.parse_args()

    repo_path = Path(args.path).resolve()
    if not repo_path.is_dir():
        print(json.dumps({"error": f"Not a directory: {repo_path}"}), file=sys.stderr)
        sys.exit(2)

    result = build_tree(repo_path, args.type, args.max_files)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
