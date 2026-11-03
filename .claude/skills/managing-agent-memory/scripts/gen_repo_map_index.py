#!/usr/bin/env python3
"""
gen_repo_map_index.py — Auto-generate docs/_base/REPO_MAP_INDEX.md

Scans docs/_kB/repo-map/ and builds an index table with "what it answers"
and "load when" entries for each doc. Reads first 10 lines of unknown files
to generate summaries. Preserves manually-edited summaries on re-runs.

Usage:
    python3 gen_repo_map_index.py --kb-dir docs/_kB/repo-map --output docs/_base/REPO_MAP_INDEX.md

    # Dry run (print to stdout):
    python3 gen_repo_map_index.py --kb-dir docs/_kB/repo-map --dry-run
"""

import argparse
import os
import re
from datetime import date
from pathlib import Path

# Known docs from mapping-repo-context — deterministic descriptions
KNOWN_DOCS = {
    "00_README.md": (
        "KB overview and completeness/quality gate status",
        "Checking KB quality, confirming mapping-repo-context ran successfully",
    ),
    "01_WORKSPACE_MAP.md": (
        "Repo boundaries, monorepo topology, workspace relationships",
        "Understanding overall repo or monorepo structure",
    ),
    "02_REPO_TREE.md": (
        "Top-level directory layout annotated with purpose",
        "Navigating the codebase, onboarding a new engineer",
    ),
    "03_COMPONENT_INVENTORY.md": (
        "Master component table: language, type, CI status, K8s flag",
        "Tech stack questions, new component decisions, K8s detection",
    ),
    "04_BUILD_AND_CICD.md": (
        "Pipeline stages, gates, build tooling, CI entrypoints",
        "CI/CD changes, build system questions, pipeline contract generation",
    ),
    "05_DEPLOYMENT_AND_ENVIRONMENTS.md": (
        "Environment layout, Helm/Kustomize config, ArgoCD app structure",
        "Deployment questions, environment-specific configuration",
    ),
    "06_RUNTIME_ARCHITECTURE.md": (
        "Communication patterns, auth model, data storage, observability setup",
        "Architecture changes, service boundary decisions",
    ),
    "07_OBSERVABILITY.md": (
        "Metrics, traces, logs, dashboards, alerting configuration",
        "Alerting thresholds, monitoring setup, debugging queries",
    ),
    "08_DEPENDENCIES_AND_BLAST_RADIUS.md": (
        "Dependency graph with Mermaid diagrams, shared library inventory",
        "Impact analysis, blast radius assessment, refactoring planning",
    ),
    "09_END_TO_END_FLOWS.md": (
        "≥5 end-to-end flows with sequence diagrams",
        "Understanding request lifecycle, debugging complex flows",
    ),
    "10_RISKS_GAPS_RECOMMENDATIONS.md": (
        "Discovered risks, gaps, and architectural recommendations",
        "Risk assessment, RULES.md seeding, prioritization decisions",
    ),
    "11_GLOSSARY_OPEN_QUESTIONS.md": (
        "Domain terms glossary and list of UNKNOWNs from discovery",
        "Naming decisions, domain model questions, open question resolution",
    ),
    "knowledge-graph.yaml": (
        "Entity nodes, aggregate boundaries, edge types in YAML",
        "Domain model reasoning, entity relationship questions",
    ),
    "kb_chunks.yaml": (
        "Chunking manifest for RAG ingestion of this KB",
        "Vector DB ingestion, RAG pipeline setup",
    ),
}

KNOWN_INTERFACE_DOCS = {
    "00_INTERFACES_OVERVIEW.md": (
        "All interface types summarized: HTTP, gRPC, events, queues, external",
        "High-level interface inventory",
    ),
    "01_API_ROUTES_CATALOG.md": (
        "HTTP and gRPC endpoint catalog with methods, paths, auth, schemas",
        "API changes, contract review, new service integration",
    ),
    "02_EVENTS_JOBS_QUEUES_CATALOG.md": (
        "Async events, batch jobs, queues: producers, consumers, schemas",
        "Async architecture changes, event-driven design questions",
    ),
    "03_EXTERNAL_INTEGRATIONS_CATALOG.md": (
        "Third-party integrations: direction, auth, rate limits, fallbacks",
        "External dependency review, security assessment",
    ),
}


def read_first_lines(filepath: Path, n: int = 10) -> str:
    """Read first N lines of a file, stripping markdown headers."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= n:
                    break
                lines.append(line.rstrip())
        return "\n".join(lines)
    except OSError:
        return ""


def derive_summary(filepath: Path, content: str) -> tuple[str, str]:
    """Derive 'what it answers' and 'load when' from first 10 lines."""
    # Extract title from first heading
    title_match = re.search(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem.replace("_", " ").title()

    # Heuristic: use title as "what it answers"
    what = f"Content about: {title}"
    when = f"Working on {filepath.stem.replace('_', ' ').lower()}"
    return what, when


def load_existing_index(output_path: Path) -> dict[str, tuple[str, str]]:
    """Load manually-edited summaries from existing index to preserve them."""
    preserved = {}
    if not output_path.exists():
        return preserved

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse table rows: | [filename](link) | what | when |
    pattern = re.compile(
        r"\|\s*\[([^\]]+)\]\([^)]+\)\s*\|\s*([^|]+)\|\s*([^|]+)\|"
    )
    for match in pattern.finditer(content):
        filename = match.group(1).strip()
        what = match.group(2).strip()
        when = match.group(3).strip()
        preserved[filename] = (what, when)

    return preserved


def scan_kb_dir(kb_dir: Path) -> list[dict]:
    """Scan KB dir and return list of doc entries."""
    entries = []

    # Root-level numbered docs
    for filename, (what, when) in KNOWN_DOCS.items():
        filepath = kb_dir / filename
        rel_path = f"../_kB/repo-map/{filename}"
        entries.append({
            "filename": filename,
            "rel_path": rel_path,
            "what": what,
            "when": when,
            "exists": filepath.exists(),
            "is_known": True,
        })

    # Unknown root-level docs (not in KNOWN_DOCS)
    if kb_dir.exists():
        for fpath in sorted(kb_dir.iterdir()):
            if fpath.is_file() and fpath.suffix == ".md" and fpath.name not in KNOWN_DOCS:
                content = read_first_lines(fpath)
                what, when = derive_summary(fpath, content)
                entries.append({
                    "filename": fpath.name,
                    "rel_path": f"../_kB/repo-map/{fpath.name}",
                    "what": what,
                    "when": when,
                    "exists": True,
                    "is_known": False,
                })

    # interfaces/ subdirectory
    interfaces_dir = kb_dir / "interfaces"
    if interfaces_dir.exists():
        for filename, (what, when) in KNOWN_INTERFACE_DOCS.items():
            filepath = interfaces_dir / filename
            rel_path = f"../_kB/repo-map/interfaces/{filename}"
            entries.append({
                "filename": filename,
                "rel_path": rel_path,
                "what": what,
                "when": when,
                "exists": filepath.exists(),
                "is_known": True,
            })

    # services/ subdirectory (summarize as group)
    services_dir = kb_dir / "services"
    if services_dir.exists():
        service_count = len(list(services_dir.glob("*/SERVICE_CONTEXT.md")))
        if service_count > 0:
            entries.append({
                "filename": "services/ (directory)",
                "rel_path": f"../_kB/repo-map/services/",
                "what": f"{service_count} per-service SERVICE_CONTEXT.md stubs with ownership, endpoints, DB, async",
                "when": "Per-service architecture questions, service-specific runbooks",
                "exists": True,
                "is_known": True,
            })

    return entries


def build_table(entries: list[dict], preserved: dict) -> str:
    lines = ["| File | What it answers | Load when... |"]
    lines.append("|------|-----------------|-------------|")

    for entry in entries:
        if not entry["exists"]:
            continue  # Skip docs that don't exist yet

        filename = entry["filename"]
        rel_path = entry["rel_path"]
        what, when = entry["what"], entry["when"]

        # Use preserved manual edits if available
        if filename in preserved and not entry.get("is_known"):
            what, when = preserved[filename]

        lines.append(f"| [{filename}]({rel_path}) | {what} | {when} |")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate REPO_MAP_INDEX.md")
    parser.add_argument("--kb-dir", default="docs/_kB/repo-map", help="Path to repo-map KB dir")
    parser.add_argument("--output", default="docs/_base/REPO_MAP_INDEX.md", help="Output path")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout only")
    args = parser.parse_args()

    kb_dir = Path(args.kb_dir)
    output_path = Path(args.output)
    today = date.today().isoformat()

    # Load existing index to preserve manual edits
    preserved = load_existing_index(output_path)

    # Scan KB directory
    entries = scan_kb_dir(kb_dir)
    doc_count = sum(1 for e in entries if e["exists"])

    # Build table
    table = build_table(entries, preserved)

    # Build output document
    output = f"""# Repo Map Index
> LLM: Read this index first. Load individual docs ONLY when the current task touches
> that domain. Do NOT pre-load all docs. This index is auto-generated — do not edit
> manually; re-run the generating-claudemd skill to update it.
>
> Last updated: {today} | Generator: generating-claudemd skill | Docs: {doc_count}

## System at a Glance

{{FILL IN: 2-4 sentence plain-language summary of what this system does.}}

## Document Index

<!-- AUTO-GENERATED — do not edit manually -->
{table}
<!-- /AUTO-GENERATED -->

## Dependency Hotspots (LLM: high blast-radius targets — extra caution required)

See [08_DEPENDENCIES_AND_BLAST_RADIUS.md](../_kB/repo-map/08_DEPENDENCIES_AND_BLAST_RADIUS.md)
for the full dependency graph and Mermaid diagrams.

{{FILL IN: top 3-5 services by incoming dependency count, with risk level.}}

## Tech Stack Snapshot

See [03_COMPONENT_INVENTORY.md](../_kB/repo-map/03_COMPONENT_INVENTORY.md) for full inventory.

{{FILL IN: 5-7 row summary table of key technology choices.}}

## Index Update History

| Date | Change | Who |
|------|--------|-----|
| {today} | Generated/updated by generating-claudemd skill | automation |
"""

    if args.dry_run:
        print(output)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✓ Written: {output_path} ({doc_count} docs indexed)")


if __name__ == "__main__":
    main()
