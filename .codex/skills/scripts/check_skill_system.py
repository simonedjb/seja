#!/usr/bin/env python3
"""
check_skill_system.py — Validate .codex skill system integrity.

Exit codes: 0 = pass, 1 = failures found, 2 = script error.

Checks performed
================
  1. SKILL.md frontmatter: required fields (name, description), valid YAML
  2. metadata.references: all referenced files exist in .agent-resources/
  3. metadata.depends: all declared dependencies are valid skill names
  4. category field: present and matches allowed enum values
  5. Agent definitions: valid frontmatter with name, description, tools
  6. Dependency cycle detection: no circular depends chains
  7. Schema validation: context_budget enum validation

Usage
-----
    python .codex/skills/scripts/check_skill_system.py

Run from the repository root.
Optional flags:
    --verbose    Show details for passing checks too
    --self-test  Run built-in dependency cycle detection tests
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CLAUDE_DIR = REPO_ROOT / ".codex"
SKILLS_DIR = CLAUDE_DIR / "skills"
AGENT_RESOURCES_DIR = REPO_ROOT / ".agent-resources"
AGENTS_DIR = CLAUDE_DIR / "agents"

ALLOWED_CATEGORIES = {"planning", "analysis", "code", "utility", "internal"}
ALLOWED_BOOLEAN_FIELDS = {"disable-model-invocation"}
ALLOWED_CONTEXT_BUDGETS = {"light", "standard", "heavy"}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Simple YAML frontmatter parser (between --- delimiters)
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter from a markdown file.

    This is a lightweight parser that handles the subset of YAML
    used in SKILL.md and agent definition files: scalar key-value pairs,
    nested mappings (one level), and lists (with - prefix).
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}

    result = {}
    current_key = None
    current_list = None
    in_metadata = False
    metadata = {}

    for line in match.group(1).split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # Top-level key: value
        if not line.startswith(" ") and not line.startswith("\t"):
            if current_list is not None and current_key:
                if in_metadata:
                    metadata[current_key] = current_list
                else:
                    result[current_key] = current_list
                current_list = None
            in_metadata = False

            if ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip().strip("\"'")
                if key == "metadata":
                    in_metadata = True
                    current_key = None
                else:
                    result[key] = value if value else ""
                    current_key = key
            continue

        # Indented content (inside metadata or a list)
        if in_metadata:
            if stripped.startswith("- "):
                if current_list is None:
                    current_list = []
                current_list.append(stripped[2:].strip())
            elif ":" in stripped:
                if current_list is not None and current_key:
                    metadata[current_key] = current_list
                    current_list = None
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip().strip("\"'")
                current_key = key
                if value:
                    # Handle inline empty list notation: key: []
                    if value == "[]":
                        metadata[key] = []
                    else:
                        metadata[key] = value
        elif stripped.startswith("- "):
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip())

    # Flush remaining list
    if current_list is not None and current_key:
        if in_metadata:
            metadata[current_key] = current_list
        else:
            result[current_key] = current_list

    if metadata:
        result["metadata"] = metadata

    return result


def detect_cycles(dep_graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect cycles in a dependency graph using DFS. Returns list of cycles found."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in dep_graph}
    cycles = []
    path = []

    def dfs(node: str):
        color[node] = GRAY
        path.append(node)

        for neighbor in dep_graph.get(node, []):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                # Found a cycle — extract it from path
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor)

        path.pop()
        color[node] = BLACK

    for node in dep_graph:
        if color[node] == WHITE:
            dfs(node)

    return cycles


def check_skills(verbose: bool = False) -> tuple[list[str], list[str]]:
    """Check all SKILL.md files. Returns (errors, warnings)."""
    errors = []
    warnings = []
    skill_names = set()
    dep_graph: dict[str, list[str]] = {}

    skill_dirs = sorted(
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )

    print(f"## Skills ({len(skill_dirs)} found)\n")

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = skill_dir.name

        # Check required fields
        if not fm.get("name"):
            errors.append(f"  - {name}/SKILL.md: missing 'name' field in frontmatter")
        else:
            skill_names.add(fm["name"])

        if not fm.get("description"):
            errors.append(f"  - {name}/SKILL.md: missing 'description' field in frontmatter")

        # Check metadata
        metadata = fm.get("metadata", {})

        # Check metadata.references — empty list [] is valid
        # general-*, template-*, and project-* files live in .agent-resources/
        refs = metadata.get("references", [])
        if isinstance(refs, list):
            for ref in refs:
                ref_path = AGENT_RESOURCES_DIR / ref
                if not ref_path.exists():
                    message = f"  - {name}/SKILL.md: references non-existent file '{ref}'"
                    if ref.startswith("project-"):
                        warnings.append(message)
                    else:
                        errors.append(message)
        elif refs:
            warnings.append(
                f"  - {name}/SKILL.md: 'references' should be a list, got: {type(refs).__name__}"
            )

        # Check category field
        category = metadata.get("category")
        if not category:
            warnings.append(f"  - {name}/SKILL.md: missing 'category' field in metadata")
        elif category not in ALLOWED_CATEGORIES:
            errors.append(
                f"  - {name}/SKILL.md: invalid category '{category}' "
                f"(allowed: {', '.join(sorted(ALLOWED_CATEGORIES))})"
            )

        # Check context_budget field
        context_budget = metadata.get("context_budget")
        if context_budget is None:
            warnings.append(
                f"  - {name}/SKILL.md: missing 'context_budget' field "
                f"(expected one of: {', '.join(sorted(ALLOWED_CONTEXT_BUDGETS))}; defaulting to 'standard')"
            )
        elif context_budget not in ALLOWED_CONTEXT_BUDGETS:
            errors.append(
                f"  - {name}/SKILL.md: invalid context_budget '{context_budget}' "
                f"(allowed: {', '.join(sorted(ALLOWED_CONTEXT_BUDGETS))})"
            )

        # Version field validation
        version = metadata.get("version")
        if version is not None:
            if not VERSION_RE.match(str(version)):
                warnings.append(
                    f"  - {name}\\SKILL.md: invalid version format '{version}' "
                    f"(expected semver: X.Y.Z)"
                )
        else:
            warnings.append(
                f"  - {name}\\SKILL.md: missing metadata.version field"
            )

        # Build dependency graph
        depends = metadata.get("depends", [])
        if isinstance(depends, list):
            dep_graph[fm.get("name", name)] = depends

        if verbose and not any(name in e for e in errors + warnings):
            print(f"  OK: {name}")

    # Second pass: check depends references
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = skill_dir.name
        metadata = fm.get("metadata", {})
        depends = metadata.get("depends", [])
        if isinstance(depends, list):
            for dep in depends:
                if dep not in skill_names:
                    errors.append(
                        f"  - {name}/SKILL.md: depends on unknown skill '{dep}'"
                    )

    # Cycle detection
    cycles = detect_cycles(dep_graph)
    if cycles:
        for cycle in cycles:
            cycle_str = " -> ".join(cycle)
            errors.append(f"  - Dependency cycle detected: {cycle_str}")

    return errors, warnings


def check_openai_yaml(verbose: bool = False) -> tuple[list[str], list[str]]:
    """Check that each skill has agents/openai.yaml. Returns (errors, warnings)."""
    errors = []
    warnings = []

    skill_dirs = sorted(
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )

    print(f"## Skill UI Metadata ({len(skill_dirs)} skills)\n")

    for skill_dir in skill_dirs:
        metadata_file = skill_dir / "agents" / "openai.yaml"
        if not metadata_file.is_file():
            warnings.append(f"  - {skill_dir.name}: missing agents/openai.yaml")
        elif verbose:
            print(f"  OK: {skill_dir.name}")

    return errors, warnings


def check_agents(verbose: bool = False) -> tuple[list[str], list[str]]:
    """Check all agent definition files. Returns (errors, warnings)."""
    errors = []
    warnings = []

    if not AGENTS_DIR.is_dir():
        warnings.append("  - Agents directory not found")
        return errors, warnings

    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    print(f"## Agents ({len(agent_files)} found)\n")

    for agent_file in agent_files:
        text = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = agent_file.stem

        if not fm.get("name"):
            errors.append(f"  - {name}.md: missing 'name' field in frontmatter")

        if not fm.get("description"):
            errors.append(f"  - {name}.md: missing 'description' field in frontmatter")

        if not fm.get("tools"):
            warnings.append(f"  - {name}.md: missing 'tools' field in frontmatter")

        if verbose and not any(name in e for e in errors + warnings):
            print(f"  OK: {name}")

    return errors, warnings


def check_references(verbose: bool = False) -> tuple[list[str], list[str]]:
    """Check reference file naming conventions in .agent-resources/. Returns (errors, warnings)."""
    errors = []
    warnings = []

    if not AGENT_RESOURCES_DIR.is_dir():
        errors.append("  - .agent-resources/ directory not found")
        return errors, warnings

    ref_files = sorted(AGENT_RESOURCES_DIR.glob("*.md"))
    print(f"## References ({len(ref_files)} found in .agent-resources/)\n")

    for ref_file in ref_files:
        name = ref_file.name
        # Check naming convention: general-*, project-*, or template-*
        if not (name.startswith("general-") or name.startswith("project-") or name.startswith("template-")):
            warnings.append(
                f"  - {name}: does not follow naming convention "
                f"(expected general-*, project-*, or template-*)"
            )
        if verbose:
            print(f"  OK: {name}")

    return errors, warnings


def run_self_test() -> bool:
    """Run built-in tests for cycle detection. Returns True if all pass."""
    print("Running self-test...\n")
    passed = True

    # Test 1: Acyclic graph — should find no cycles
    acyclic = {"a": ["b", "c"], "b": ["c"], "c": [], "d": ["a"]}
    cycles = detect_cycles(acyclic)
    if not cycles:
        print("  PASS: Acyclic graph correctly detected as cycle-free")
    else:
        print(f"  FAIL: Acyclic graph reported cycles: {cycles}")
        passed = False

    # Test 2: Simple cycle — a -> b -> a
    cyclic_simple = {"a": ["b"], "b": ["a"]}
    cycles = detect_cycles(cyclic_simple)
    if cycles:
        print(f"  PASS: Simple cycle detected: {' -> '.join(cycles[0])}")
    else:
        print("  FAIL: Simple cycle (a -> b -> a) was not detected")
        passed = False

    # Test 3: Longer cycle — a -> b -> c -> a
    cyclic_long = {"a": ["b"], "b": ["c"], "c": ["a"]}
    cycles = detect_cycles(cyclic_long)
    if cycles:
        print(f"  PASS: Longer cycle detected: {' -> '.join(cycles[0])}")
    else:
        print("  FAIL: Longer cycle (a -> b -> c -> a) was not detected")
        passed = False

    # Test 4: Self-loop — a -> a
    self_loop = {"a": ["a"]}
    cycles = detect_cycles(self_loop)
    if cycles:
        print(f"  PASS: Self-loop detected: {' -> '.join(cycles[0])}")
    else:
        print("  FAIL: Self-loop (a -> a) was not detected")
        passed = False

    # Test 5: Disconnected graph with one cycle
    mixed = {"a": ["b"], "b": [], "c": ["d"], "d": ["c"]}
    cycles = detect_cycles(mixed)
    if cycles:
        print(f"  PASS: Cycle in disconnected component detected: {' -> '.join(cycles[0])}")
    else:
        print("  FAIL: Cycle in disconnected component was not detected")
        passed = False

    print()
    if passed:
        print("Self-test PASSED: all cycle detection fixtures validated correctly.")
    else:
        print("Self-test FAILED: see above for details.")

    return passed


def main():
    parser = argparse.ArgumentParser(
        description="Validate .codex skill system integrity"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show details for passing checks too"
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="Run built-in cycle detection tests"
    )
    args = parser.parse_args()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    print("# Skill System Integrity Check\n")

    if not CLAUDE_DIR.is_dir():
        print("ERROR: .codex directory not found")
        sys.exit(2)

    all_errors = []
    all_warnings = []

    # Check skills (includes cycle detection)
    errs, warns = check_skills(verbose=args.verbose)
    all_errors.extend(errs)
    all_warnings.extend(warns)

    # Check agents
    errs, warns = check_agents(verbose=args.verbose)
    all_errors.extend(errs)
    all_warnings.extend(warns)

    # Check skill UI metadata
    errs, warns = check_openai_yaml(verbose=args.verbose)
    all_errors.extend(errs)
    all_warnings.extend(warns)

    # Check references
    errs, warns = check_references(verbose=args.verbose)
    all_errors.extend(errs)
    all_warnings.extend(warns)

    # Report
    print()
    if all_errors:
        print(f"## Errors ({len(all_errors)})\n")
        for msg in all_errors:
            print(msg)
        print()

    if all_warnings:
        print(f"## Warnings ({len(all_warnings)})\n")
        for msg in all_warnings:
            print(msg)
        print()

    if not all_errors and not all_warnings:
        print("PASS: Skill system integrity check passed")
    elif all_errors:
        print(f"FAIL: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"WARN: {len(all_warnings)} warning(s), 0 errors")


if __name__ == "__main__":
    main()
