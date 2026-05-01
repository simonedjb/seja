"""Tests for generate_call_graph.py -- call-graph generator.

Covers Step 8 of plan-000411:

- Node discovery across the 7 typed classes (skill, agent, script, rule,
  ref-general, ref-template, ref-project) with priv/tests exclusions and
  empty ref-project tolerance.
- Edge extraction for all four skill-edge shapes (invokes, delegates,
  orchestrates, eager-load + lazy-load).
- Script->script imports and subprocess-invokes edges via AST.
- `description_source` sourcing across quick-guide / designer-description /
  developer-fallback / none.
- `--check` mode drift detection and unresolved-reference detection.
- Idempotency across runs with `--fixed-date`.
- HTML / CSS / JS shape contracts: CDN pins, palette, layout + panel functions.

Tests patch the module-level path constants to point at a synthetic tree
under ``tmp_path`` rather than refactoring the generator's public API.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import generate_call_graph as gen


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "generate_call_graph.py"
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _patch_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    """Redirect the generator's module-level path constants at ``root``.

    This is the surgical alternative to refactoring ``compute_outputs`` to
    accept a ``root`` argument. The generator's top-level constants are
    resolved against this root so every discovery / extraction pass walks
    the synthetic tree.
    """
    monkeypatch.setattr(gen, "REPO_ROOT", root)
    monkeypatch.setattr(gen, "SKILLS_DIR", root / ".claude" / "skills")
    monkeypatch.setattr(gen, "AGENTS_DIR", root / ".claude" / "agents")
    monkeypatch.setattr(
        gen, "SCRIPTS_SUBDIR", root / ".claude" / "skills" / "scripts"
    )
    monkeypatch.setattr(gen, "RULES_DIR", root / ".claude" / "rules")
    monkeypatch.setattr(
        gen, "REFS_GENERAL_DIR", root / "_references" / "general"
    )
    monkeypatch.setattr(
        gen, "REFS_TEMPLATE_DIR", root / "_references" / "template"
    )
    monkeypatch.setattr(
        gen, "REFS_PROJECT_DIR", root / "_references" / "project"
    )
    monkeypatch.setattr(
        gen,
        "OUTPUT_JSON",
        root / "_references" / "general" / "call-graph.json",
    )
    monkeypatch.setattr(
        gen,
        "OUTPUT_MD",
        root / "seja-public" / "docs" / "concepts" / "call-graph.md",
    )
    monkeypatch.setattr(
        gen,
        "OUTPUT_HTML",
        root / "seja-public" / "docs" / "concepts" / "call-graph.html",
    )
    monkeypatch.setattr(
        gen,
        "OUTPUT_CSS",
        root / "seja-public" / "docs" / "concepts" / "call-graph.css",
    )
    monkeypatch.setattr(
        gen,
        "OUTPUT_JS",
        root / "seja-public" / "docs" / "concepts" / "call-graph.js",
    )
    monkeypatch.setattr(
        gen,
        "OUTPUT_JSON_PUBLIC",
        root / "seja-public" / "docs" / "concepts" / "call-graph.json",
    )
    monkeypatch.setattr(
        gen,
        "SKILL_GRAPH_JSON",
        root / "_references" / "general" / "skill-graph.json",
    )


def _minimal_tree(root: Path) -> None:
    """Write a minimal synthetic tree with one example of each node type.

    Intentionally excludes ref-project to exercise the empty-directory
    tolerance path.
    """
    # SKILL.md
    _write(
        root / ".claude" / "skills" / "demo" / "SKILL.md",
        (
            "---\n"
            "name: /demo\n"
            "description: demo skill\n"
            "metadata:\n"
            "  context_budget: low\n"
            "---\n"
            "\n"
            "# Demo\n"
            "\n"
            "A demo skill.\n"
            "\n"
            "## Quick Guide\n"
            "\n"
            "**What this skill does for you**: demo stuff.\n"
        ),
    )
    # Also a pre-skill and post-skill (required by step spec -- both must be
    # included as skill nodes).
    _write(
        root / ".claude" / "skills" / "pre-skill" / "SKILL.md",
        "---\nname: /pre-skill\n---\n\n# Pre-skill\n\nLifecycle hook.\n",
    )
    _write(
        root / ".claude" / "skills" / "post-skill" / "SKILL.md",
        "---\nname: /post-skill\n---\n\n# Post-skill\n\nLifecycle hook.\n",
    )

    # Agent
    _write(
        root / ".claude" / "agents" / "demo-agent.md",
        "---\nname: demo-agent\ndescription: demo agent for tests\n---\n"
        "\n# Demo Agent\n\nDoes demo things.\n",
    )

    # Script
    _write(
        root / ".claude" / "skills" / "scripts" / "demo_script.py",
        '"""demo_script.py -- demo script docstring lead."""\n'
        "\nimport os\n",
    )

    # Rule
    _write(
        root / ".claude" / "rules" / "demo-rule.md",
        "# Demo Rule\n\nA demo rule.\n",
    )

    # ref-general
    _write(
        root / "_references" / "general" / "coding-standards.md",
        "# Coding Standards\n\nSmall functions.\n",
    )

    # ref-template
    _write(
        root / "_references" / "template" / "conventions.md",
        "# Conventions\n\nTemplate.\n",
    )

    # _references/project/ intentionally missing -- tolerated.


# ---------------------------------------------------------------------------
# 1) Node discovery across the 7 types
# ---------------------------------------------------------------------------


def test_node_discovery_across_7_types(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    _patch_root(monkeypatch, tmp_path)

    nodes = gen.discover_all_nodes()
    types_seen = {n["type"] for n in nodes}

    # 6 of 7 types are present; ref-project is (correctly) absent.
    assert "skill" in types_seen
    assert "agent" in types_seen
    assert "script" in types_seen
    assert "rule" in types_seen
    assert "ref-general" in types_seen
    assert "ref-template" in types_seen
    assert "ref-project" not in types_seen

    # Exactly one node per present type (except skill -- 3 because of
    # pre-skill + post-skill + demo).
    counts: dict[str, int] = {}
    for node in nodes:
        counts[node["type"]] = counts.get(node["type"], 0) + 1
    assert counts["skill"] == 3
    assert counts["agent"] == 1
    assert counts["script"] == 1
    assert counts["rule"] == 1
    assert counts["ref-general"] == 1
    assert counts["ref-template"] == 1

    # pre-skill and post-skill are first-class skill nodes.
    ids = {n["id"] for n in nodes}
    assert "skill:pre-skill" in ids
    assert "skill:post-skill" in ids
    assert "skill:demo" in ids


def test_node_discovery_excludes_priv_and_tests_scripts(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    # Scripts under priv/ and tests/ must be excluded.
    _write(
        tmp_path / ".claude" / "skills" / "scripts" / "priv" / "secret.py",
        '"""secret.py -- private."""\n',
    )
    _write(
        tmp_path / ".claude" / "skills" / "scripts" / "tests" / "test_x.py",
        '"""test_x.py -- test helper."""\n',
    )
    _write(
        tmp_path / ".claude" / "skills" / "scripts" / "__init__.py",
        "",
    )
    _patch_root(monkeypatch, tmp_path)

    scripts = gen.discover_scripts()
    names = [s["label"] for s in scripts]
    assert "demo_script.py" in names
    assert "secret.py" not in names
    assert "test_x.py" not in names
    assert "__init__.py" not in names
    # Only the one legitimate top-level non-test, non-priv script.
    assert len(scripts) == 1


def test_node_discovery_tolerates_empty_ref_project(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    # Create the project dir but leave it empty.
    (tmp_path / "_references" / "project").mkdir(parents=True)
    _patch_root(monkeypatch, tmp_path)

    refs = gen.discover_refs(
        tmp_path / "_references" / "project", "ref-project", "ref-project"
    )
    assert refs == []


def test_skill_user_invocable_manifest_field(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    # Override the fixture lifecycle hooks with the explicit current shape.
    _write(
        tmp_path / ".claude" / "skills" / "pre-skill" / "SKILL.md",
        "---\nname: /pre-skill\nuser-invocable: false\n---\n\n# Pre-skill\n",
    )
    _write(
        tmp_path / ".claude" / "skills" / "post-skill" / "SKILL.md",
        "---\nname: /post-skill\nuser-invocable: false\n---\n\n# Post-skill\n",
    )
    _write(
        tmp_path / ".claude" / "skills" / "explicit" / "SKILL.md",
        "---\nname: /explicit\nuser-invocable: true\n---\n\n# Explicit\n",
    )
    _patch_root(monkeypatch, tmp_path)

    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-21T00:00:00Z"
    )
    nodes = {node["id"]: node for node in manifest["nodes"]}

    assert nodes["skill:pre-skill"]["user_invocable"] is False
    assert nodes["skill:post-skill"]["user_invocable"] is False
    assert nodes["skill:explicit"]["user_invocable"] is True
    assert nodes["skill:demo"]["user_invocable"] is True
    assert "user_invocable" not in nodes["agent:demo-agent"]
    assert "user_invocable" not in nodes["script:demo_script.py"]
    assert "user_invocable" not in nodes["rule:demo-rule"]
    assert "user_invocable" not in nodes["ref-general:coding-standards.md"]


def test_parse_skill_user_invocable_defaults_true_on_absent_or_malformed():
    assert gen._parse_skill_user_invocable("name: /demo\n") is True
    assert (
        gen._parse_skill_user_invocable(
            "name: /demo\nuser-invocable: true\n"
        )
        is True
    )
    assert (
        gen._parse_skill_user_invocable(
            "name: /demo\nuser-invocable: false\n"
        )
        is False
    )
    assert (
        gen._parse_skill_user_invocable(
            "name: /demo\nuser-invocable: yes\n"
        )
        is True
    )


# ---------------------------------------------------------------------------
# 2) Edge extraction -- all four skill edge shapes
# ---------------------------------------------------------------------------


def _edges_tree(root: Path) -> None:
    """Build a fixture with all four edge shapes in one SKILL.md."""
    # Target skill (orchestrates target).
    _write(
        root / ".claude" / "skills" / "plan" / "SKILL.md",
        "---\nname: /plan\n---\n\n# Plan\n\nTarget skill.\n",
    )
    # Target agent (delegates target).
    _write(
        root / ".claude" / "agents" / "bar.md",
        "---\nname: bar\ndescription: bar agent\n---\n\n# Bar\n\nAgent.\n",
    )
    # Target script (invokes target).
    _write(
        root / ".claude" / "skills" / "scripts" / "foo.py",
        '"""foo.py -- foo script."""\n',
    )
    # Target rule (lazy-load ref).
    _write(
        root / ".claude" / "rules" / "coding-standards.md",
        "# Coding standards\n\nRule body.\n",
    )
    # Target general ref (eager-load).
    _write(
        root / "_references" / "general" / "coding-standards.md",
        "# Coding Standards\n\nSmall functions.\n",
    )
    # Target general ref (lazy-load).
    _write(
        root / "_references" / "general" / "shared-definitions.md",
        "# Shared\n\nDefinitions.\n",
    )

    # The source SKILL.md with all four edge shapes.
    _write(
        root / ".claude" / "skills" / "source" / "SKILL.md",
        "---\n"
        "name: /source\n"
        "description: edge-extraction fixture\n"
        "metadata:\n"
        "  eager_references:\n"
        "    - general/coding-standards.md\n"
        "  references:\n"
        "    - general/coding-standards.md\n"
        "    - general/shared-definitions.md\n"
        "---\n"
        "\n"
        "# Source\n"
        "\n"
        "## Steps\n"
        "\n"
        "1. Run `python .claude/skills/scripts/foo.py` to do a thing.\n"
        "2. Delegate to the reviewer (Agent tool, subagent_type='bar').\n"
        "3. Run /plan to plan next steps.\n"
    )


def test_edge_extraction_all_four_shapes(monkeypatch, tmp_path):
    _edges_tree(tmp_path)
    _patch_root(monkeypatch, tmp_path)

    outputs, manifest, warnings = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )
    edges_by_type: dict[str, list[dict]] = {}
    for edge in manifest["edges"]:
        edges_by_type.setdefault(edge["type"], []).append(edge)

    # invokes: /source -> foo.py
    invokes = [e for e in edges_by_type.get("invokes", [])
               if e["source"] == "skill:source"]
    assert any(e["target"] == "script:foo.py" for e in invokes), (
        f"expected invokes edge skill:source -> script:foo.py; "
        f"got {invokes}"
    )

    # delegates: /source -> bar
    delegates = edges_by_type.get("delegates", [])
    assert any(
        e["source"] == "skill:source" and e["target"] == "agent:bar"
        for e in delegates
    ), f"expected delegates edge skill:source -> agent:bar; got {delegates}"

    # orchestrates: /source -> /plan
    orchestrates = edges_by_type.get("orchestrates", [])
    assert any(
        e["source"] == "skill:source" and e["target"] == "skill:plan"
        for e in orchestrates
    ), f"expected orchestrates edge; got {orchestrates}"

    # eager-load: /source -> ref-general:coding-standards.md
    eager = edges_by_type.get("eager-load", [])
    assert any(
        e["source"] == "skill:source"
        and e["target"] == "ref-general:coding-standards.md"
        for e in eager
    ), f"expected eager-load edge; got {eager}"

    # lazy-load: /source -> ref-general:shared-definitions.md
    # (general/coding-standards.md appears in both eager and references,
    # but lazy-load edges are restricted to the set minus eager entries.)
    lazy = edges_by_type.get("lazy-load", [])
    assert any(
        e["source"] == "skill:source"
        and e["target"] == "ref-general:shared-definitions.md"
        for e in lazy
    ), f"expected lazy-load edge; got {lazy}"


# ---------------------------------------------------------------------------
# 3) Script->script edges (imports + subprocess invokes)
# ---------------------------------------------------------------------------


def test_script_to_script_imports_and_invokes(monkeypatch, tmp_path):
    # Create a minimal skill so the graph has at least one discovered skill
    # (not strictly required for script->script edges but keeps invariants).
    _write(
        tmp_path / ".claude" / "skills" / "demo" / "SKILL.md",
        "---\nname: /demo\n---\n\n# Demo\n\n## Quick Guide\n\nHi.\n",
    )

    # The script we are testing edges from.
    _write(
        tmp_path / ".claude" / "skills" / "scripts" / "generate_foo.py",
        (
            '"""generate_foo.py -- foo generator."""\n'
            "import sys\n"
            "import subprocess\n"
            "import project_config\n"
            "\n"
            "subprocess.run([sys.executable, "
            '".claude/skills/scripts/generate_bar.py"])\n'
        ),
    )
    # Import target.
    _write(
        tmp_path / ".claude" / "skills" / "scripts" / "project_config.py",
        '"""project_config.py -- config module."""\n',
    )
    # Subprocess-invoke target.
    _write(
        tmp_path / ".claude" / "skills" / "scripts" / "generate_bar.py",
        '"""generate_bar.py -- bar generator."""\n',
    )

    _patch_root(monkeypatch, tmp_path)

    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )

    edges = manifest["edges"]

    imports_edge = next(
        (
            e for e in edges
            if e["source"] == "script:generate_foo.py"
            and e["target"] == "script:project_config.py"
            and e["type"] == "imports"
        ),
        None,
    )
    assert imports_edge is not None, (
        f"expected imports edge generate_foo.py -> project_config.py; "
        f"got edges={edges}"
    )

    invokes_edge = next(
        (
            e for e in edges
            if e["source"] == "script:generate_foo.py"
            and e["target"] == "script:generate_bar.py"
            and e["type"] == "invokes"
        ),
        None,
    )
    assert invokes_edge is not None, (
        f"expected invokes edge generate_foo.py -> generate_bar.py; "
        f"got edges={edges}"
    )


# ---------------------------------------------------------------------------
# 4) Description sourcing
# ---------------------------------------------------------------------------


def test_description_source_quick_guide(monkeypatch, tmp_path):
    # Post-plan-000466: Quick Guide narrative lives in a sibling
    # SKILL-quickguide.md file. SKILL.md body carries the pointer plus
    # agent-executional content.
    skill_dir = tmp_path / ".claude" / "skills" / "demo"
    _write(
        skill_dir / "SKILL.md",
        "---\nname: /demo\n---\n\n"
        "> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)\n\n"
        "# Demo\n\nAn H1 lead sentence.\n",
    )
    _write(
        skill_dir / "SKILL-quickguide.md",
        "**What this skill does for you**: canonical Quick Guide body.\n",
    )
    _patch_root(monkeypatch, tmp_path)
    node = {
        "id": "skill:demo",
        "type": "skill",
        "label": "/demo",
        "path": ".claude/skills/demo/SKILL.md",
    }
    desc, source = gen.compute_node_description(node)
    assert source == "quick-guide", (
        f"expected quick-guide; got {source} desc={desc!r}"
    )
    assert "Quick Guide body" in desc


def test_description_source_developer_fallback_when_sibling_missing(
    monkeypatch, tmp_path
):
    # Sibling missing -> fall through to developer-fallback (H1 + lead).
    skill_path = tmp_path / ".claude" / "skills" / "nosib" / "SKILL.md"
    _write(
        skill_path,
        "---\nname: /nosib\n---\n\n"
        "# Nosib\n\nFallback lead sentence.\n",
    )
    _patch_root(monkeypatch, tmp_path)
    node = {
        "id": "skill:nosib",
        "type": "skill",
        "label": "/nosib",
        "path": ".claude/skills/nosib/SKILL.md",
    }
    desc, source = gen.compute_node_description(node)
    assert source == "developer-fallback", (
        f"expected developer-fallback when sibling absent; got {source}"
    )
    assert "Nosib" in desc or "Fallback lead" in desc


def test_description_source_designer_description_markdown(
    monkeypatch, tmp_path
):
    agent_path = tmp_path / ".claude" / "agents" / "demo-agent.md"
    _write(
        agent_path,
        "---\n"
        "name: demo-agent\n"
        "designer_description: Hand-crafted designer copy for the agent.\n"
        "---\n"
        "\n"
        "# Agent\n\nDeveloper lead sentence.\n",
    )
    _patch_root(monkeypatch, tmp_path)
    node = {
        "id": "agent:demo-agent",
        "type": "agent",
        "label": "demo-agent",
        "path": ".claude/agents/demo-agent.md",
    }
    desc, source = gen.compute_node_description(node)
    assert source == "designer-description"
    assert "Hand-crafted designer copy" in desc


def test_description_source_developer_fallback_script(monkeypatch, tmp_path):
    script_path = (
        tmp_path / ".claude" / "skills" / "scripts" / "helper.py"
    )
    _write(
        script_path,
        '"""helper.py -- developer-oriented docstring lead."""\n',
    )
    _patch_root(monkeypatch, tmp_path)
    node = {
        "id": "script:helper.py",
        "type": "script",
        "label": "helper.py",
        "path": ".claude/skills/scripts/helper.py",
    }
    desc, source = gen.compute_node_description(node)
    assert source == "developer-fallback"
    assert "developer-oriented docstring lead" in desc


def test_description_source_none_for_empty_markdown(monkeypatch, tmp_path):
    empty_path = tmp_path / ".claude" / "rules" / "empty-rule.md"
    _write(empty_path, "")
    _patch_root(monkeypatch, tmp_path)
    node = {
        "id": "rule:empty-rule",
        "type": "rule",
        "label": "empty-rule",
        "path": ".claude/rules/empty-rule.md",
    }
    desc, source = gen.compute_node_description(node)
    assert source == "none"
    assert desc == ""


# ---------------------------------------------------------------------------
# 5) --check drift detection
# ---------------------------------------------------------------------------


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def _write_all_outputs(root: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    """Generate fresh outputs to disk for the fixture tree, return manifest."""
    _patch_root(monkeypatch, root)
    outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return manifest


def test_check_detects_json_drift(monkeypatch, tmp_path, capsys):
    _minimal_tree(tmp_path)
    _write_all_outputs(tmp_path, monkeypatch)

    # Mutate a structurally meaningful field in the JSON on disk.
    json_path = tmp_path / "_references" / "general" / "call-graph.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["nodes"][0]["label"] = "MUTATED"
    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    # run_check prints to stderr via sys.stderr.
    exit_code = gen.run_check(strict=False, verbose=False)
    captured = capsys.readouterr()
    assert exit_code == 1, (
        f"expected exit 1 on drift; got {exit_code}. "
        f"stdout={captured.out!r} stderr={captured.err!r}"
    )
    assert "DRIFT:" in captured.err, (
        f"expected DRIFT: in stderr; got {captured.err!r}"
    )


def test_check_passes_on_fresh_outputs(monkeypatch, tmp_path, capsys):
    _minimal_tree(tmp_path)
    _write_all_outputs(tmp_path, monkeypatch)

    exit_code = gen.run_check(strict=False, verbose=False)
    captured = capsys.readouterr()
    assert exit_code == 0, (
        f"expected exit 0 on fresh outputs; got {exit_code}. "
        f"stderr={captured.err!r}"
    )
    assert "CHECK PASS" in captured.out


# ---------------------------------------------------------------------------
# 6) --check unresolved reference detection
# ---------------------------------------------------------------------------


def test_check_detects_unresolved_script_reference(
    monkeypatch, tmp_path, capsys
):
    # Minimal tree with a SKILL.md referencing a nonexistent script.
    _minimal_tree(tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "brokenref" / "SKILL.md",
        "---\n"
        "name: /brokenref\n"
        "---\n"
        "\n"
        "# Brokenref\n"
        "\n"
        "## Quick Guide\n\nDescribes the broken ref.\n"
        "\n"
        "## Steps\n\n"
        "Run `python .claude/skills/scripts/nonexistent.py` to do a thing.\n",
    )
    _patch_root(monkeypatch, tmp_path)

    # The skill->script regex validates targets against the discovered node
    # set, so a nonexistent target is dropped silently from the edges list
    # and therefore will not trigger the UNRESOLVED code path -- which is
    # by design. To exercise the UNRESOLVED path we inject a synthetic edge
    # pointing at a non-discovered node via a frontmatter ref that resolves
    # at parse time but the target is later deleted. We use the cheaper
    # approach: generate outputs, then delete a referenced node file, then
    # run --check. The stale on-disk JSON still carries the edge.

    # Simpler: produce outputs normally, then manually inject an unresolved
    # edge into the on-disk JSON. Drift detection ALSO triggers; to isolate
    # UNRESOLVED we use a fixture where a DESIGNER-resolved reference in
    # the frontmatter points at a target we remove between passes. But the
    # most direct route: call run_check with a manifest that already has a
    # bogus edge. We add a reference entry pointing at `general/ghost.md`
    # and then regenerate; eager-load resolution will emit a warning (not
    # an edge). The canonical UNRESOLVED path requires an edge whose target
    # is absent from the node set.
    # Construct such a condition by patching extract_skill_edges: seed an
    # edge to a nonexistent target via a direct monkeypatch.

    original_extract = gen.extract_skill_edges

    def patched_extract(skill_path: Path, nodes: list[dict],
                        warnings: list[str]) -> list[dict]:
        edges = original_extract(skill_path, nodes, warnings)
        if skill_path.parent.name == "brokenref":
            edges.append({
                "source": "skill:brokenref",
                "target": "script:ghost.py",
                "type": "invokes",
                "label": "",
            })
        return edges

    monkeypatch.setattr(gen, "extract_skill_edges", patched_extract)

    # First: regenerate outputs (captures the bogus edge in JSON on disk).
    outputs, _manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    # Now --check: output matches (no DRIFT) but the ghost edge is UNRESOLVED.
    exit_code = gen.run_check(strict=False, verbose=False)
    captured = capsys.readouterr()
    assert exit_code == 1, (
        f"expected exit 1 on unresolved ref; got {exit_code}. "
        f"stderr={captured.err!r}"
    )
    assert "UNRESOLVED:" in captured.err, (
        f"expected UNRESOLVED: in stderr; got {captured.err!r}"
    )
    # The message should cite the source path (not just the node id).
    assert "brokenref" in captured.err


# ---------------------------------------------------------------------------
# 7) Idempotency across runs with --fixed-date
# ---------------------------------------------------------------------------


def test_idempotent_outputs_with_fixed_date(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    _patch_root(monkeypatch, tmp_path)

    outputs1, _m1, _w1 = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )
    outputs2, _m2, _w2 = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )

    # All 5 artifacts byte-identical across two runs.
    assert set(outputs1.keys()) == set(outputs2.keys())
    for path in outputs1:
        assert outputs1[path] == outputs2[path], (
            f"idempotency violated for {path}"
        )


# ---------------------------------------------------------------------------
# 8) HTML / CSS / JS shape contracts
# ---------------------------------------------------------------------------


def test_html_contains_pinned_cytoscape_script_tag():
    html = gen.render_html("2026-04-18T00:00:00Z")
    # CDN pin is part of the contract.
    assert (
        'src="https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js"'
        in html
    ), "expected pinned cytoscape@3.30.4 script tag in HTML"
    # Pinned fcose + cola + svg extensions (dagre and cose-bilkent were
    # replaced by better alternatives for dense hub-and-spoke graphs).
    assert "cytoscape-fcose@2.2.0" in html
    assert "cytoscape-cola@2.5.1" in html
    assert "webcola@3.4.0" in html
    assert "cytoscape-svg@0.4.0" in html
    # Canonical structural elements from the page.
    assert '<div id="cy"' in html
    assert '<aside id="side-panel"' in html


def test_html_contains_user_facing_filter_controls():
    html = gen.render_html("2026-04-18T00:00:00Z")
    assert 'id="filter-hide-internal-skills"' in html
    assert 'id="filter-preset-user-facing"' in html
    assert 'id="filter-preset-full"' in html
    assert "Hide internal skills (pre-skill, post-skill)" in html


def test_css_contains_palette_hex_for_all_7_node_types():
    css = gen.render_css("2026-04-18T00:00:00Z")
    # All 7 pastel palette hex values from the plan.
    palette_hexes = [
        "#b8d5f2",  # skill (darkened from #cfe4fb in plan-000452)
        "#e6d5ed",  # agent (darkened from #f2e8f7 in plan-000452)
        "#d5e3ef",  # script (darkened from #e8f0f7 in plan-000452)
        "#f8e6a8",  # rule (darkened from #fdf2d2 in plan-000452)
        "#cfe3cf",  # ref-general (darkened from #e3f0e3 in plan-000452)
        "#d7cce8",  # ref-template (darkened from #eae3f5 in plan-000452)
        "#efcccc",  # ref-project (darkened from #f7e3e3 in plan-000452)
    ]
    for hex_val in palette_hexes:
        assert hex_val in css, (
            f"expected palette hex {hex_val} in CSS; not found"
        )
    # Matching borders for each swatch (smoke-test one per type).
    assert "#6da3d4" in css  # skill border
    assert "#b58282" in css  # ref-project border


def test_js_contains_three_layouts_and_panel_functions():
    js = gen.render_js("2026-04-18T00:00:00Z")
    # Three layout keys: fcose (force), cola (constraint-force with
    # downward flow), concentric (radial by type).
    assert "'fcose'" in js
    assert "'cola'" in js
    assert "'concentric'" in js
    # Panel open/close behaviour.
    assert "function openPanel" in js
    assert "function closePanel" in js
    # Layout runner used by the radio switcher.
    assert "function runLayout" in js
    # Focus-mode faded-opacity values (plan-000452). Non-neighbor nodes stay
    # readable at 0.40 / 0.55 instead of the prior 0.15 / 0.2.
    assert "'opacity': 0.40" in js
    assert "'text-opacity': 0.55" in js


def test_js_contains_user_facing_filter_logic():
    js = gen.render_js("2026-04-18T00:00:00Z")
    assert "callGraph:filter-hide-internal-skills" in js
    assert "filter-preset-user-facing" in js
    assert "filter-preset-full" in js
    assert "user_invocable" in js


# ---------------------------------------------------------------------------
# 9) Parse-helper microtests (round out coverage of leaf helpers)
# ---------------------------------------------------------------------------


def test_strip_frontmatter_returns_body():
    fm, body = gen._strip_frontmatter(
        "---\nname: foo\n---\n\n# H1\n\nBody.\n"
    )
    assert "name: foo" in fm
    assert body.startswith("# H1")


def test_strip_frontmatter_handles_no_frontmatter():
    fm, body = gen._strip_frontmatter("# H1\n\nBody.\n")
    assert fm == ""
    assert body.startswith("# H1")


def test_parse_ref_lists_extracts_eager_and_lazy():
    fm = (
        "name: /demo\n"
        "metadata:\n"
        "  eager_references:\n"
        "    - general/foo.md\n"
        "  references:\n"
        "    - general/foo.md\n"
        "    - general/bar.md\n"
    )
    eager, refs = gen._parse_ref_lists(fm)
    assert eager == ["general/foo.md"]
    assert refs == ["general/foo.md", "general/bar.md"]


def test_sanitize_mermaid_id_replaces_non_alnum():
    assert gen._sanitize_mermaid_id("skill:foo-bar") == "skill_foo_bar"
    assert (
        gen._sanitize_mermaid_id("ref-general:general/foo.md")
        == "ref_general_general_foo_md"
    )


def test_sanitize_edge_label_truncates_long_text():
    label = "x" * 80
    sanitized = gen._sanitize_edge_label(label)
    assert len(sanitized) == 50
    assert sanitized.endswith("...")


def test_build_manifest_deduplicates_edges():
    nodes = [
        {
            "id": "skill:a",
            "type": "skill",
            "label": "/a",
            "path": ".claude/skills/a/SKILL.md",
        },
        {
            "id": "skill:b",
            "type": "skill",
            "label": "/b",
            "path": ".claude/skills/b/SKILL.md",
        },
    ]
    edges = [
        {"source": "skill:a", "target": "skill:b",
         "type": "orchestrates", "label": ""},
        # Duplicate -- should be collapsed.
        {"source": "skill:a", "target": "skill:b",
         "type": "orchestrates", "label": ""},
    ]
    # Stub description extraction to avoid real filesystem reads.
    from unittest.mock import patch
    with patch.object(gen, "compute_node_description",
                      return_value=("", "none")):
        manifest = gen.build_manifest(
            nodes, edges, [], "2026-04-18T00:00:00Z"
        )
    assert manifest["edge_count"] == 1
    assert manifest["node_count"] == 2


# ---------------------------------------------------------------------------
# 10) Python designer_description shapes
# ---------------------------------------------------------------------------


def test_python_designer_description_comment_block():
    src = (
        "#!/usr/bin/env python3\n"
        "# designer: Designer-voiced line one.\n"
        "#     continuation line two.\n"
        "\n"
        "import os\n"
    )
    result = gen._extract_python_designer_description(src)
    assert "Designer-voiced line one." in result
    assert "continuation line two." in result


def test_python_designer_description_module_assignment():
    src = (
        '"""docstring."""\n'
        '__designer_description__ = "Module-level designer copy."\n'
    )
    result = gen._extract_python_designer_description(src)
    assert result == "Module-level designer copy."


def test_python_designer_description_absent_returns_empty():
    src = '"""just a docstring."""\nimport os\n'
    assert gen._extract_python_designer_description(src) == ""


def test_python_designer_description_syntax_error_returns_empty():
    # Broken syntax should short-circuit to empty rather than crash.
    src = "def ("
    assert gen._extract_python_designer_description(src) == ""


def test_python_docstring_lead_strips_script_prefix():
    src = '"""generate_x.py -- real description here."""\n'
    assert gen._extract_python_docstring_lead(src) == (
        "real description here."
    )


def test_python_docstring_lead_returns_empty_when_missing():
    src = "import os\n"
    assert gen._extract_python_docstring_lead(src) == ""


def test_python_docstring_lead_syntax_error_returns_empty():
    assert gen._extract_python_docstring_lead("def (") == ""


# ---------------------------------------------------------------------------
# 11) Frontmatter designer_description shapes
# ---------------------------------------------------------------------------


def test_parse_frontmatter_designer_description_inline_quoted():
    fm = 'designer_description: "Quoted inline value."\n'
    assert gen._parse_frontmatter_designer_description(fm) == (
        "Quoted inline value."
    )


def test_parse_frontmatter_designer_description_inline_single_quoted():
    fm = "designer_description: 'Single quoted.'\n"
    assert gen._parse_frontmatter_designer_description(fm) == "Single quoted."


def test_parse_frontmatter_designer_description_block_pipe():
    fm = (
        "designer_description: |\n"
        "  Line one.\n"
        "  Line two.\n"
        "other_key: v\n"
    )
    result = gen._parse_frontmatter_designer_description(fm)
    assert "Line one." in result
    assert "Line two." in result


def test_parse_frontmatter_designer_description_absent_returns_empty():
    fm = "name: foo\n"
    assert gen._parse_frontmatter_designer_description(fm) == ""


def test_parse_frontmatter_designer_description_empty_input():
    assert gen._parse_frontmatter_designer_description("") == ""


def test_parse_frontmatter_designer_description_block_with_empty_body():
    # Block scalar opened with `|` but no indented content. The extractor
    # must not crash; it should return an empty string. Regression guard
    # for the silent-empty-extraction failure mode called out in
    # plan-000427 Phase 2 TEST deep-dive.
    fm = (
        "designer_description: |\n"
        "other_key: v\n"
    )
    assert gen._parse_frontmatter_designer_description(fm) == ""


def test_parse_frontmatter_designer_description_inline_with_trailing_hash():
    # Inline value that contains a trailing `#` which YAML would fold
    # into a comment. The current regex extractor is not YAML-aware and
    # captures the entire line after the key. Pin that behaviour so a
    # future refactor to a real YAML parser cannot silently change the
    # contract without updating the authoring rubric (plan-000427).
    fm = "designer_description: value with trailing # not-a-comment\n"
    result = gen._parse_frontmatter_designer_description(fm)
    assert result == "value with trailing # not-a-comment"


# ---------------------------------------------------------------------------
# 12) CLI end-to-end: main() writes all 5 artifacts
# ---------------------------------------------------------------------------


def test_cli_main_writes_all_five_artifacts(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    _patch_root(monkeypatch, tmp_path)

    exit_code = gen.main(["--fixed-date", "2026-04-18T00:00:00Z"])
    assert exit_code == 0

    # All 5 artifacts should exist on disk.
    assert (tmp_path / "_references" / "general" / "call-graph.json").exists()
    md = tmp_path / "seja-public" / "docs" / "concepts" / "call-graph.md"
    html = tmp_path / "seja-public" / "docs" / "concepts" / "call-graph.html"
    css = tmp_path / "seja-public" / "docs" / "concepts" / "call-graph.css"
    js = tmp_path / "seja-public" / "docs" / "concepts" / "call-graph.js"
    assert md.exists()
    assert html.exists()
    assert css.exists()
    assert js.exists()


def test_cli_main_verbose_prints_summary(monkeypatch, tmp_path, capsys):
    _minimal_tree(tmp_path)
    _patch_root(monkeypatch, tmp_path)

    exit_code = gen.main(
        ["--fixed-date", "2026-04-18T00:00:00Z", "--verbose"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "wrote:" in captured.err
    assert "node types:" in captured.err
    assert "edge types:" in captured.err


def test_cli_main_errors_on_empty_tree(monkeypatch, tmp_path, capsys):
    # No skills anywhere -- main() should error out with exit 1.
    # Create a root that has NOTHING -- no skills, no agents, no scripts.
    _patch_root(monkeypatch, tmp_path)

    exit_code = gen.main(["--fixed-date", "2026-04-18T00:00:00Z"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "no nodes discovered" in captured.err


def test_cli_main_check_mode_dispatches_to_run_check(
    monkeypatch, tmp_path, capsys
):
    _minimal_tree(tmp_path)
    _write_all_outputs(tmp_path, monkeypatch)

    exit_code = gen.main(["--check"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "CHECK PASS" in captured.out


# ---------------------------------------------------------------------------
# 13) --check --strict upgrades warnings
# ---------------------------------------------------------------------------


def test_check_strict_promotes_warnings_to_errors(
    monkeypatch, tmp_path, capsys
):
    # Build a fixture where a SKILL.md frontmatter references a ref that
    # does not resolve -- generates a warning.
    _write(
        tmp_path / ".claude" / "skills" / "demo" / "SKILL.md",
        "---\n"
        "name: /demo\n"
        "metadata:\n"
        "  eager_references:\n"
        "    - general/does-not-exist.md\n"
        "---\n"
        "\n"
        "# Demo\n\n## Quick Guide\n\nHi.\n",
    )
    # A real ref so discover_refs returns something non-empty.
    _write(
        tmp_path / "_references" / "general" / "real.md",
        "# Real\n\nReal ref.\n",
    )

    _write_all_outputs(tmp_path, monkeypatch)

    # Non-strict: warning does not fail.
    exit_code = gen.run_check(strict=False, verbose=False)
    capsys.readouterr()  # clear
    assert exit_code == 0

    # Strict: warning becomes error.
    exit_code = gen.run_check(strict=True, verbose=False)
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "SUSPICIOUS:" in captured.err


# ---------------------------------------------------------------------------
# 14) Markdown rendering emits expected sections
# ---------------------------------------------------------------------------


def test_markdown_render_contains_required_sections(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    # Add a second skill so the orchestration section has content to consider.
    _write(
        tmp_path / ".claude" / "skills" / "caller" / "SKILL.md",
        "---\n"
        "name: /caller\n"
        "metadata:\n"
        "  eager_references:\n"
        "    - general/coding-standards.md\n"
        "---\n"
        "\n"
        "# Caller\n\n## Quick Guide\n\nHi.\n\n"
        "## Steps\n\n"
        "Run `python .claude/skills/scripts/demo_script.py` to execute.\n",
    )
    _patch_root(monkeypatch, tmp_path)

    outputs, _manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )
    md = outputs[gen.OUTPUT_MD]

    # Required section headers.
    assert "# SEJA harness call graph" in md
    assert "## Skill orchestration" in md
    assert "## Skill invocations" in md
    assert "## Skill reference loads" in md
    assert "## Per-skill call trees" in md
    assert "## Reverse indices" in md
    # Frontmatter with freshness + diataxis.
    assert "diataxis: reference" in md
    assert "freshness: release-bound" in md
    assert "last-reviewed: 2026-04-18" in md
    # Accessibility text fallback block.
    assert (
        "<summary>Text-only relationship list "
        "(accessibility fallback)</summary>"
    ) in md


def test_markdown_render_mentions_skills_by_label(monkeypatch, tmp_path):
    _minimal_tree(tmp_path)
    _patch_root(monkeypatch, tmp_path)

    outputs, _manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-18T00:00:00Z"
    )
    md = outputs[gen.OUTPUT_MD]
    # Every discovered skill should have a per-skill H3 drill-down.
    for label in ("/demo", "/pre-skill", "/post-skill"):
        assert f"### {label}" in md, (
            f"missing per-skill H3 for {label} in call-graph.md"
        )


# ---------------------------------------------------------------------------
# 15) Resolve reference entry helper
# ---------------------------------------------------------------------------


def test_resolve_ref_entry_matches_general():
    nodes = [
        {
            "id": "ref-general:coding-standards.md",
            "type": "ref-general",
            "label": "coding-standards",
            "path": "_references/general/coding-standards.md",
        },
    ]
    assert (
        gen._resolve_ref_entry("general/coding-standards.md", nodes)
        == "ref-general:coding-standards.md"
    )


def test_resolve_ref_entry_returns_none_on_miss():
    nodes = [
        {
            "id": "ref-general:a.md",
            "type": "ref-general",
            "label": "a",
            "path": "_references/general/a.md",
        },
    ]
    assert gen._resolve_ref_entry("general/does-not-exist.md", nodes) is None


def test_resolve_ref_entry_empty_input_returns_none():
    assert gen._resolve_ref_entry("", []) is None


# ---------------------------------------------------------------------------
# Suggests edges from skill-graph.json (plan-000414)
# ---------------------------------------------------------------------------


def _two_skill_tree(root: Path) -> None:
    """Tree with just two skill nodes: /foo and /bar, no other node types."""
    _write(
        root / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\ndescription: foo skill\n---\n\n# Foo\n\nFoo.\n",
    )
    _write(
        root / ".claude" / "skills" / "bar" / "SKILL.md",
        "---\nname: /bar\ndescription: bar skill\n---\n\n# Bar\n\nBar.\n",
    )


def _write_skill_graph_json(root: Path, edges: list[dict]) -> None:
    _write(
        root / "_references" / "general" / "skill-graph.json",
        json.dumps(
            {"version": "1.0", "generated": "2026-04-19T00:00:00Z",
             "categories": [], "edges": edges},
            indent=2,
        ) + "\n",
    )


def test_suggests_edge_extracted_from_skill_graph_json(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    _two_skill_tree(tmp_path)
    _write_skill_graph_json(
        tmp_path,
        [{"after": "/foo", "suggest": "/bar", "reason": "try it",
          "category": "utilities"}],
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    suggests = [e for e in manifest["edges"] if e["type"] == "suggests"]
    assert len(suggests) == 1
    assert suggests[0]["source"] == "skill:foo"
    assert suggests[0]["target"] == "skill:bar"
    assert suggests[0]["label"] == "try it"


def test_suggests_edge_normalizes_flag_variants(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "plan" / "SKILL.md",
        "---\nname: /plan\n---\n\n# Plan\n\nPlan.\n",
    )
    _write(
        tmp_path / ".claude" / "skills" / "implement" / "SKILL.md",
        "---\nname: /implement\n---\n\n# Implement\n\nImpl.\n",
    )
    _write_skill_graph_json(
        tmp_path,
        [{"after": "/plan --light", "suggest": "/implement",
          "reason": "Ready to implement this proposal?", "category": "x"}],
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    suggests = [e for e in manifest["edges"] if e["type"] == "suggests"]
    assert len(suggests) == 1
    assert suggests[0]["source"] == "skill:plan"
    assert suggests[0]["target"] == "skill:implement"


def test_suggests_edge_dedupes_on_source_target(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    _two_skill_tree(tmp_path)
    _write_skill_graph_json(
        tmp_path,
        [
            {"after": "/foo", "suggest": "/bar", "reason": "first reason",
             "category": "a"},
            {"after": "/foo", "suggest": "/bar", "reason": "second reason",
             "category": "b"},
        ],
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    suggests = [e for e in manifest["edges"] if e["type"] == "suggests"]
    assert len(suggests) == 1
    assert suggests[0]["label"] == "first reason"


def test_suggests_non_skill_target_dropped_silently(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    _two_skill_tree(tmp_path)
    _write_skill_graph_json(
        tmp_path,
        [
            {"after": "/foo", "suggest": "docs/how-to/recipes.md",
             "reason": "see recipes", "category": "a"},
            {"after": "/foo", "suggest": "general/getting-started.md",
             "reason": "get started", "category": "b"},
        ],
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    suggests = [e for e in manifest["edges"] if e["type"] == "suggests"]
    assert suggests == []
    assert not any("docs/how-to" in w for w in manifest["warnings"])


def test_suggests_edge_style_present_in_js(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    _two_skill_tree(tmp_path)
    _write_skill_graph_json(
        tmp_path,
        [{"after": "/foo", "suggest": "/bar", "reason": "r", "category": "a"}],
    )
    outputs, _manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    js = outputs[gen.OUTPUT_JS]
    assert 'edge[type = "suggests"]' in js
    assert "'dashed'" in js


def test_suggests_edge_missing_skill_graph_json_is_noop(monkeypatch, tmp_path):
    """When skill-graph.json is absent, the generator emits zero suggests edges."""
    _patch_root(monkeypatch, tmp_path)
    _two_skill_tree(tmp_path)
    # Intentionally do NOT write skill-graph.json.
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    suggests = [e for e in manifest["edges"] if e["type"] == "suggests"]
    assert suggests == []


# ---------------------------------------------------------------------------
# Broadened delegate patterns (orphan-fix A)
# ---------------------------------------------------------------------------


def test_delegate_detected_via_launch_backtick_pattern(monkeypatch, tmp_path):
    r"""`Launch the \`code-reviewer\` agent` should produce a delegates edge
    even without a literal subagent_type= assignment."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "check" / "SKILL.md",
        "---\nname: /check\n---\n\n# Check\n\n"
        "Launch the `code-reviewer` agent with the scope.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "code-reviewer.md",
        "---\nname: code-reviewer\n---\n\n# Code reviewer\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [e for e in manifest["edges"] if e["type"] == "delegates"]
    assert any(
        e["source"] == "skill:check" and e["target"] == "agent:code-reviewer"
        for e in delegates
    )


def test_delegate_detected_via_agent_md_path(monkeypatch, tmp_path):
    """`.claude/agents/onboarding-generator.md` reference produces a
    delegates edge even when subagent_type= names general-purpose."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "onboard" / "SKILL.md",
        "---\nname: /onboard\n---\n\n# Onboard\n\n"
        "Launch the `onboarding-generator` agent "
        "(subagent_type=`general-purpose`, "
        "using the prompt from `.claude/agents/onboarding-generator.md`).\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "onboarding-generator.md",
        "---\nname: onboarding-generator\n---\n\n# Onboarding generator\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [e for e in manifest["edges"] if e["type"] == "delegates"]
    assert any(
        e["source"] == "skill:onboard"
        and e["target"] == "agent:onboarding-generator"
        for e in delegates
    )


def test_delegate_dedupes_when_multiple_patterns_match(monkeypatch, tmp_path):
    """If all three patterns name the same agent, emit exactly one edge."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "check" / "SKILL.md",
        "---\nname: /check\n---\n\n# Check\n\n"
        "Launch the `code-reviewer` agent "
        "(subagent_type=`code-reviewer`, "
        "using the prompt from `.claude/agents/code-reviewer.md`).\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "code-reviewer.md",
        "---\nname: code-reviewer\n---\n\n# Code reviewer\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:check"
        and e["target"] == "agent:code-reviewer"
    ]
    assert len(delegates) == 1


# ---------------------------------------------------------------------------
# Rule auto-loads edges (orphan-fix C)
# ---------------------------------------------------------------------------


def test_rule_autoload_edge_matches_claude_star_star_glob(monkeypatch, tmp_path):
    """A rule with `paths: [\".claude/**\"]` emits an auto-loads edge from
    every discovered SKILL.md."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n",
    )
    _write(
        tmp_path / ".claude" / "skills" / "bar" / "SKILL.md",
        "---\nname: /bar\n---\n\n# Bar\n",
    )
    _write(
        tmp_path / ".claude" / "rules" / "harness-structure.md",
        "---\npaths:\n  - \".claude/**\"\n---\n# Harness Structure\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    autoloads = [e for e in manifest["edges"] if e["type"] == "auto-loads"]
    assert len(autoloads) == 2
    sources = {e["source"] for e in autoloads}
    assert sources == {"skill:foo", "skill:bar"}
    assert all(e["target"] == "rule:harness-structure" for e in autoloads)


def test_rule_autoload_edge_absent_when_no_paths_match(monkeypatch, tmp_path):
    """A rule whose `paths:` glob matches no SKILL.md emits no edges
    (ground truth for consumer-project-scoped rules in the harness-dev
    repo)."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n",
    )
    _write(
        tmp_path / ".claude" / "rules" / "backend.md",
        "---\npaths:\n  - \"backend/app/**\"\n---\n# Backend\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    autoloads = [e for e in manifest["edges"] if e["type"] == "auto-loads"]
    assert autoloads == []


# ---------------------------------------------------------------------------
# Dynamic ref-load edges (orphan-fix D)
# ---------------------------------------------------------------------------


def test_dynamic_load_edge_from_skill_mentioning_review_perspectives(
    monkeypatch, tmp_path
):
    """A skill body that mentions `review-perspectives/` should emit
    dynamic-load edges to every ref-general file under that subdirectory."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "check" / "SKILL.md",
        "---\nname: /check\n---\n\n# Check\n\n"
        "Load only the selected `review-perspectives/<tag>.md` files.\n",
    )
    _write(
        tmp_path / "_references" / "general" / "review-perspectives" / "sec.md",
        "---\nname: SEC\n---\n# Security\n",
    )
    _write(
        tmp_path / "_references" / "general" / "review-perspectives" / "arch.md",
        "---\nname: ARCH\n---\n# Architecture\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    dyn = [e for e in manifest["edges"] if e["type"] == "dynamic-load"]
    assert len(dyn) == 2
    assert all(e["source"] == "skill:check" for e in dyn)
    assert {e["target"] for e in dyn} == {
        "ref-general:review-perspectives/sec.md",
        "ref-general:review-perspectives/arch.md",
    }
    assert all(e["label"] == "review-perspectives" for e in dyn)


def test_dynamic_load_edge_from_agent_onboarding_subdir(monkeypatch, tmp_path):
    """An agent body that references `onboarding/` emits dynamic-load
    edges to every file under _references/general/onboarding/."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "agents" / "onboarding-generator.md",
        "---\nname: onboarding-generator\n---\n"
        "Select from onboarding/bld-l1.md based on role.\n",
    )
    _write(
        tmp_path / "_references" / "general" / "onboarding" / "bld-l1.md",
        "# BLD L1\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    dyn = [e for e in manifest["edges"] if e["type"] == "dynamic-load"]
    assert len(dyn) == 1
    assert dyn[0]["source"] == "agent:onboarding-generator"
    assert dyn[0]["target"] == "ref-general:onboarding/bld-l1.md"
    assert dyn[0]["label"] == "onboarding"


def test_dynamic_load_dedupes_same_source_target(monkeypatch, tmp_path):
    """Multiple mentions of the same subdir in one body emit one edge per
    target, not one per mention."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "check" / "SKILL.md",
        "---\nname: /check\n---\n\n# Check\n\n"
        "Load review-perspectives/sec.md and review-perspectives/arch.md "
        "and also review-perspectives/general.md.\n",
    )
    _write(
        tmp_path / "_references" / "general" / "review-perspectives" / "sec.md",
        "# Sec\n",
    )
    outputs, manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    dyn = [e for e in manifest["edges"] if e["type"] == "dynamic-load"]
    # Only one ref-general file exists under that subdir.
    assert len(dyn) == 1


def test_dynamic_load_dotted_style_present_in_js(monkeypatch, tmp_path):
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n",
    )
    outputs, _manifest, _ = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    js = outputs[gen.OUTPUT_JS]
    assert 'edge[type = "dynamic-load"]' in js
    assert "'dotted'" in js


# ---------------------------------------------------------------------------
# Conditional-edge annotation (plan-000438 Step 5)
# ---------------------------------------------------------------------------


def test_conditional_edge_mode_flag_prose_pattern(monkeypatch, tmp_path):
    """Pattern 1: `**Deep-dive mode** (`--deep` flag): Launch the `bar` agent.`

    The mode-flag parenthesis shape with a backtick-quoted flag should
    annotate the resulting delegates edge with `when: "--deep"`.
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n"
        "**Deep-dive mode** (`--deep` flag): Launch the `bar` agent "
        "to do deep analysis.\n",
    )
    _write(
        tmp_path / ".claude" / "skills" / "bar" / "SKILL.md",
        "---\nname: /bar\n---\n\n# Bar\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "bar.md",
        "---\nname: bar\n---\n\n# Bar agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:bar"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge skill:foo -> agent:bar; got {delegates}"
    )
    assert delegates[0].get("when") == "--deep", (
        f"expected when='--deep'; got {delegates[0]}"
    )


def test_conditional_edge_if_flag_passed_pattern(monkeypatch, tmp_path):
    """Pattern 2: ``If `--inventory` is passed, Launch the `inventory-agent` agent``.

    The ``If `--X` is passed`` phrasing should attach `when: "--inventory"`
    to the delegation. Prose includes the trailing word ``agent`` so the
    baseline extractor emits the `delegates` edge; the conditional
    annotator then attaches `when` to that pre-existing edge
    (scope-restrict contract, plan-000443).
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "research" / "SKILL.md",
        "---\nname: /research\n---\n\n# Research\n\n"
        "If `--inventory` is passed, Launch the `inventory-agent` agent "
        "to catalog elements.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "inventory-agent.md",
        "---\nname: inventory-agent\n---\n\n# Inventory agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:research"
        and e["target"] == "agent:inventory-agent"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge; got {delegates}"
    )
    assert delegates[0].get("when") == "--inventory", (
        f"expected when='--inventory'; got {delegates[0]}"
    )


def test_conditional_edge_when_invoked_with_flag_pattern(monkeypatch, tmp_path):
    """Pattern 4: ``When invoked with `--framing metacomm`, Launch ...``

    Multi-word flag captured via the ``--X Y`` token shape should attach
    `when: "--framing metacomm"` to the resolved target. Prose includes
    the trailing word ``agent`` so the baseline extractor emits the
    `delegates` edge first; the conditional annotator then attaches
    `when` to that pre-existing edge (scope-restrict contract,
    plan-000443).

    Also asserts the negative case: when no backtick-quoted agent name
    resolves inside the paragraph, no edge is emitted (prefer false
    negatives).
    """
    _patch_root(monkeypatch, tmp_path)
    # Positive case: backtick-quoted target name inside the paragraph.
    _write(
        tmp_path / ".claude" / "skills" / "plan" / "SKILL.md",
        "---\nname: /plan\n---\n\n# Plan\n\n"
        "When invoked with `--framing metacomm`, Launch the "
        "`metacomm-agent` agent to frame the brief.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "metacomm-agent.md",
        "---\nname: metacomm-agent\n---\n\n# Metacomm agent\n",
    )
    # Negative case: condition prose without any resolvable target name.
    _write(
        tmp_path / ".claude" / "skills" / "help" / "SKILL.md",
        "---\nname: /help\n---\n\n# Help\n\n"
        "When invoked with `--browse`, render an interactive browser "
        "with no specific delegation target named here.\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:plan"
        and e["target"] == "agent:metacomm-agent"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge skill:plan -> agent:metacomm-agent; "
        f"got {delegates}"
    )
    assert delegates[0].get("when") == "--framing metacomm", (
        f"expected when='--framing metacomm'; got {delegates[0]}"
    )
    # Negative: /help should not gain a conditional edge because no
    # backtick-quoted agent / script / skill name appears in the paragraph
    # following the `--browse` mention.
    help_conditional = [
        e for e in manifest["edges"]
        if e["source"] == "skill:help" and "when" in e
    ]
    assert help_conditional == [], (
        f"expected no conditional edges from skill:help; got "
        f"{help_conditional}"
    )


def test_conditional_edge_negative_unmatched_prose_stays_unconditional(
    monkeypatch, tmp_path
):
    """A plain delegation without a conditional pattern must not gain
    `when` or `conditional` fields."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "runner" / "SKILL.md",
        "---\nname: /runner\n---\n\n# Runner\n\n"
        "Launch the `foo-agent` agent to process the job.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "foo-agent.md",
        "---\nname: foo-agent\n---\n\n# Foo agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:runner"
        and e["target"] == "agent:foo-agent"
    ]
    assert len(delegates) == 1
    edge = delegates[0]
    assert "when" not in edge, (
        f"expected no `when` field on unconditional edge; got {edge}"
    )
    assert "conditional" not in edge, (
        f"expected no `conditional` field on unconditional edge; got {edge}"
    )


def test_conditional_edge_scope_restrict_no_baseline_no_fabrication(
    monkeypatch, tmp_path
):
    """Scope-restrict contract (plan-000443, check-000440 Finding 2).

    If conditional-prose resolves to a target name that the baseline
    extractor did NOT emit an edge for (e.g. prose that mentions a skill
    by backticked name without the invocation-context verb the baseline
    requires), the annotator must NOT fabricate a new edge. Conditional
    annotation is additive metadata on existing edges only.
    """
    _patch_root(monkeypatch, tmp_path)
    # Conditional prose names `help` (a known skill) but without the
    # `/help` forward-slash anchor + invocation-context verb the baseline
    # `extract_skill_edges` requires for an `orchestrates` edge. Before
    # the scope-restrict this would have fabricated a skill->skill edge.
    _write(
        tmp_path / ".claude" / "skills" / "source-skill" / "SKILL.md",
        "---\nname: /source-skill\n---\n\n# Source\n\n"
        "When invoked with `--browse`, consult the `help` skill for "
        "navigation.\n",
    )
    _write(
        tmp_path / ".claude" / "skills" / "help" / "SKILL.md",
        "---\nname: /help\n---\n\n# Help\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    fabricated = [
        e for e in manifest["edges"]
        if e["source"] == "skill:source-skill"
        and e["target"] == "skill:help"
    ]
    assert fabricated == [], (
        f"conditional-prose annotator must not fabricate edges outside "
        f"the baseline extractor's scope; got {fabricated}"
    )


def test_conditional_edge_dedup_conditional_and_unconditional_mentions(
    monkeypatch, tmp_path
):
    """When the same delegation is mentioned twice (once conditional,
    once unconditional), build_manifest should collapse to a single edge
    that preserves the `when` annotation from the conditional mention."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "dual" / "SKILL.md",
        "---\nname: /dual\n---\n\n# Dual\n\n"
        "Launch the `worker-agent` agent for the default flow.\n\n"
        "**Deep mode** (`--deep` flag): Launch the `worker-agent` "
        "agent with deep settings.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "worker-agent.md",
        "---\nname: worker-agent\n---\n\n# Worker agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:dual"
        and e["target"] == "agent:worker-agent"
    ]
    # Dedup: exactly one edge.
    assert len(delegates) == 1, (
        f"expected a single deduped edge; got {delegates}"
    )
    # The surviving edge carries the conditional annotation (merge
    # semantics in build_manifest promote `when` from either occurrence
    # into the kept edge).
    assert delegates[0].get("when") == "--deep", (
        f"expected when='--deep' survived dedup; got {delegates[0]}"
    )


def test_conditional_edge_dedup_reverse_order_conditional_first(
    monkeypatch, tmp_path
):
    """Reverse of the dedup_conditional_and_unconditional_mentions test:
    conditional mention comes FIRST in document order, unconditional
    mention comes SECOND. `when` must still survive the merge regardless
    of discovery order (dedup symmetry in build_manifest)."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "dual-rev" / "SKILL.md",
        "---\nname: /dual-rev\n---\n\n# Dual-rev\n\n"
        "**Deep mode** (`--deep` flag): Launch the `worker-agent` "
        "agent with deep settings.\n\n"
        "Launch the `worker-agent` agent for the default flow.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "worker-agent.md",
        "---\nname: worker-agent\n---\n\n# Worker agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:dual-rev"
        and e["target"] == "agent:worker-agent"
    ]
    assert len(delegates) == 1, (
        f"expected a single deduped edge; got {delegates}"
    )
    assert delegates[0].get("when") == "--deep", (
        f"expected when='--deep' survived dedup (reverse order); "
        f"got {delegates[0]}"
    )


def test_conditional_edge_json_schema_omits_absent_fields(
    monkeypatch, tmp_path
):
    """Edges without `when` / `conditional` must not carry those keys with
    a null value -- they must be omitted entirely so existing consumers
    see the pre-plan-000438 JSON shape."""
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "plain" / "SKILL.md",
        "---\nname: /plain\n---\n\n# Plain\n\n"
        "Launch the `plain-agent` agent.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "plain-agent.md",
        "---\nname: plain-agent\n---\n\n# Plain agent\n",
    )
    outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    # Assert on the manifest dict directly.
    for edge in manifest["edges"]:
        if "when" in edge:
            assert edge["when"], (
                f"`when` present but empty on edge {edge}"
            )
        if "conditional" in edge:
            assert edge["conditional"] is True, (
                f"`conditional` present but not True on edge {edge}"
            )
    # Also assert the serialized JSON omits the keys rather than emitting
    # `"when": null` / `"conditional": null`.
    json_text = outputs[gen.OUTPUT_JSON]
    data = json.loads(json_text)
    for edge in data["edges"]:
        # No null-valued when/conditional keys should appear on the wire.
        assert edge.get("when") != None or "when" not in edge  # noqa: E711
        assert (
            edge.get("conditional") != None  # noqa: E711
            or "conditional" not in edge
        )
        # The plain-agent edge must carry neither field.
        if (
            edge["source"] == "skill:plain"
            and edge["target"] == "agent:plain-agent"
        ):
            assert "when" not in edge, f"unexpected `when` on {edge}"
            assert "conditional" not in edge, (
                f"unexpected `conditional` on {edge}"
            )
    # Double-check literally: no `"when": null` substring in the JSON.
    assert '"when": null' not in json_text
    assert '"conditional": null' not in json_text


def test_conditional_edge_html_css_js_shape(monkeypatch, tmp_path):
    """Regenerated HTML/CSS/JS artifacts must expose the conditional-edge
    legend row, filter checkbox, CSS swatch class, Cytoscape selector,
    and dash-pattern style (plan-000438 Steps 3-4)."""
    _patch_root(monkeypatch, tmp_path)
    # Minimal skill tree so compute_outputs succeeds.
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n## Quick Guide\n\nHi.\n",
    )
    outputs, _manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19"
    )
    html = outputs[gen.OUTPUT_HTML]
    css = outputs[gen.OUTPUT_CSS]
    js = outputs[gen.OUTPUT_JS]

    # HTML: legend swatch class + filter checkbox id.
    assert 'id="filter-conditional-show"' in html, (
        "expected filter-conditional-show checkbox in HTML "
        "(positive-semantics replacement for the legacy filter-conditional-only)"
    )
    assert "swatch-edge-conditional" in html, (
        "expected swatch-edge-conditional legend row in HTML"
    )

    # CSS: swatch class selector.
    assert ".swatch-edge-conditional" in css, (
        "expected .swatch-edge-conditional rule in CSS"
    )

    # JS: Cytoscape selector + dash-pattern style property.
    # Attribute-defined selector `[conditional]` (not the earlier `[?conditional]`
    # truthy form) -- the data mapping only sets the attribute on actually-
    # conditional edges, so attribute-presence is a stronger contract.
    assert "'edge[conditional]'" in js, (
        "expected Cytoscape selector 'edge[conditional]' in JS"
    )
    assert "'line-dash-pattern'" in js, (
        "expected 'line-dash-pattern' style property in JS"
    )


# ---------------------------------------------------------------------------
# plan-000443 Step 4: direct coverage for Patterns 3 & 5, broader
# negative-phrasing, and CRLF normalization.
# ---------------------------------------------------------------------------


def test_conditional_edge_pattern3_plural_arguments_includes(
    monkeypatch, tmp_path
):
    r"""Pattern 3 (plural): ``If the arguments includes `--inventory`, Launch
    the `inventory-agent` agent.``

    Baseline extractor emits a `delegates` edge from the ``\`X\` agent``
    phrasing; the conditional annotator attaches ``when: "--inventory"``.
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n"
        "If the arguments includes `--inventory`, Launch the "
        "`inventory-agent` agent to catalog elements.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "inventory-agent.md",
        "---\nname: inventory-agent\n---\n\n# Inventory agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:inventory-agent"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge skill:foo -> agent:inventory-agent; "
        f"got {delegates}"
    )
    assert delegates[0].get("when") == "--inventory", (
        f"expected when='--inventory'; got {delegates[0]}"
    )


def test_conditional_edge_pattern3_singular_argument_includes(
    monkeypatch, tmp_path
):
    """Pattern 3 (singular): ``If the argument includes `--depth`, Launch
    the `depth-agent` agent.``

    The singular ``argument includes`` form is covered by the same regex
    (``arguments?`` / ``includes?``).
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n"
        "If the argument includes `--depth`, Launch the `depth-agent` "
        "agent to dive deeper.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "depth-agent.md",
        "---\nname: depth-agent\n---\n\n# Depth agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:depth-agent"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge skill:foo -> agent:depth-agent; "
        f"got {delegates}"
    )
    assert delegates[0].get("when") == "--depth", (
        f"expected when='--depth'; got {delegates[0]}"
    )


def test_conditional_edge_pattern5_was_provided(monkeypatch, tmp_path):
    """Pattern 5: ``If `--deep` was provided, Launch the `council-debate`
    agent.``

    The ``was provided`` phrasing attaches ``when: "--deep"`` to the
    baseline-emitted delegates edge.
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n"
        "If `--deep` was provided, Launch the `council-debate` agent to "
        "run a structured debate.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "council-debate.md",
        "---\nname: council-debate\n---\n\n# Council debate\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:council-debate"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge skill:foo -> agent:council-debate; "
        f"got {delegates}"
    )
    assert delegates[0].get("when") == "--deep", (
        f"expected when='--deep'; got {delegates[0]}"
    )


def test_conditional_edge_pattern1_negative_without(monkeypatch, tmp_path):
    r"""Pattern 1 negative look-ahead (plan-000443 Step 3): ``without`` must
    reject the match.

    Fixture: ``**Default mode** (without `--deep` flag): Launch the
    `default-agent` agent.`` The baseline extractor still emits the
    `delegates` edge from the ``\`X\` agent`` prose, but the conditional
    annotator must NOT attach a ``when`` field because Pattern 1's
    negative look-ahead rejects ``without`` flag-absence phrasings.
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n"
        "**Default mode** (without `--deep` flag): Launch the "
        "`default-agent` agent for the standard path.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "default-agent.md",
        "---\nname: default-agent\n---\n\n# Default agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:default-agent"
    ]
    assert len(delegates) == 1, (
        f"expected baseline delegates edge to persist; got {delegates}"
    )
    assert "when" not in delegates[0], (
        f"`without` flag-absence phrasing must be rejected by Pattern 1's "
        f"negative look-ahead; got edge {delegates[0]}"
    )


def test_conditional_edge_pattern1_negative_absent(monkeypatch, tmp_path):
    """Pattern 1 negative look-ahead (plan-000443 Step 3): ``absent`` must
    reject the match.

    Mirror of the ``without`` case for the ``absent`` alternation branch.
    """
    _patch_root(monkeypatch, tmp_path)
    _write(
        tmp_path / ".claude" / "skills" / "foo" / "SKILL.md",
        "---\nname: /foo\n---\n\n# Foo\n\n"
        "**Fallback mode** (absent `--strict` flag): Launch the "
        "`fallback-agent` agent for the permissive path.\n",
    )
    _write(
        tmp_path / ".claude" / "agents" / "fallback-agent.md",
        "---\nname: fallback-agent\n---\n\n# Fallback agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:fallback-agent"
    ]
    assert len(delegates) == 1, (
        f"expected baseline delegates edge to persist; got {delegates}"
    )
    assert "when" not in delegates[0], (
        f"`absent` flag-absence phrasing must be rejected by Pattern 1's "
        f"negative look-ahead; got edge {delegates[0]}"
    )


def test_conditional_edge_crlf_normalization(monkeypatch, tmp_path):
    """Plan-000443 Step 1: `_read_text` normalizes CRLF -> LF so paragraph
    boundary detection (``\\n\\n``) works uniformly on Windows-authored
    SKILL.md files.

    Write the fixture with raw ``\\r\\n`` line endings via `write_bytes`
    (bypassing `_write`'s LF normalization) so we actually exercise the
    generator's normalization pass. Assert the conditional annotator
    attaches ``when`` on the baseline delegates edge -- proof that the
    paragraph-bounded window resolver found the target name despite the
    CRLF source.
    """
    _patch_root(monkeypatch, tmp_path)
    skill_path = tmp_path / ".claude" / "skills" / "foo" / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    crlf_body = (
        "---\r\nname: /foo\r\n---\r\n\r\n# Foo\r\n\r\n"
        "If `--crlf-test` is passed, Launch the `crlf-agent` agent to "
        "handle the CRLF path.\r\n"
    )
    skill_path.write_bytes(crlf_body.encode("utf-8"))
    # Sanity: confirm the fixture actually carries CRLF bytes on disk --
    # otherwise this test would validate nothing.
    assert b"\r\n" in skill_path.read_bytes(), (
        "fixture must preserve CRLF bytes for the normalization test to be "
        "meaningful"
    )
    _write(
        tmp_path / ".claude" / "agents" / "crlf-agent.md",
        "---\nname: crlf-agent\n---\n\n# CRLF agent\n",
    )
    _outputs, manifest, _warnings = gen.compute_outputs(
        fixed_date="2026-04-19T00:00:00Z", verbose=False
    )
    delegates = [
        e for e in manifest["edges"]
        if e["type"] == "delegates"
        and e["source"] == "skill:foo"
        and e["target"] == "agent:crlf-agent"
    ]
    assert len(delegates) == 1, (
        f"expected one delegates edge skill:foo -> agent:crlf-agent; "
        f"got {delegates}"
    )
    assert delegates[0].get("when") == "--crlf-test", (
        f"expected when='--crlf-test' after CRLF normalization; got "
        f"{delegates[0]}"
    )
