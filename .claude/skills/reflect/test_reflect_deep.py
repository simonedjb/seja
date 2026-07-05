#!/usr/bin/env python3
"""Tests for /reflect --deep mode modules.

Invocation: test
Lifecycle: active

Covers reflect_colors, reflect_deep_scope, reflect_event_matrix, and
reflect_transition_graph with synthetic data.  Also enforces the
non-prescriptive rule across all .py source files in this directory.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup -- the modules under test use bare relative imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

import reflect_colors  # noqa: E402
import reflect_deep_scope  # noqa: E402
import reflect_event_matrix  # noqa: E402
import reflect_transition_graph  # noqa: E402


# ===================================================================
# 1. reflect_colors
# ===================================================================


class TestColors:
    """Tests for the shared color palette module."""

    def test_color_domain_length(self):
        assert len(reflect_colors.COLOR_DOMAIN) == len(reflect_colors.SKILL_ORDER) + len(reflect_colors.MODE_COLORS)

    def test_color_range_length(self):
        assert len(reflect_colors.COLOR_RANGE) == len(reflect_colors.COLOR_DOMAIN)

    def test_hex_format(self):
        hex_re = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for value in reflect_colors.COLOR_RANGE:
            assert hex_re.match(value), f"Bad hex value: {value}"

    def test_color_key_default_mode(self):
        assert reflect_colors.color_key("research", "default") == "research"

    def test_color_key_variant_mode(self):
        assert reflect_colors.color_key("research", "--deep") == "--deep"

    def test_color_key_empty_mode(self):
        assert reflect_colors.color_key("plan", "") == "plan"

    def test_color_key_unknown_mode(self):
        assert reflect_colors.color_key("check", "--unknown") == "check"

    def test_domain_range_alignment(self):
        """Each domain entry has a corresponding range entry."""
        assert len(reflect_colors.COLOR_DOMAIN) == len(reflect_colors.COLOR_RANGE)
        for key, color in zip(reflect_colors.COLOR_DOMAIN, reflect_colors.COLOR_RANGE):
            assert isinstance(key, str)
            assert isinstance(color, str)


# ===================================================================
# 2. reflect_deep_scope
# ===================================================================


def _make_briefs_md(entries: list[str]) -> str:
    """Build a minimal briefs.md from line entries."""
    return "# Briefs\n\n" + "\n".join(entries) + "\n"


def _make_telemetry_jsonl(records: list[dict]) -> str:
    """Build telemetry.jsonl content from a list of dicts."""
    return "\n".join(json.dumps(r) for r in records) + "\n"


class TestDeepScope:
    """Tests for scope resolution and filtering."""

    def test_scope_keyword_matches_skill_and_brief(self, tmp_path: Path):
        """Scope keyword 'publish' matches records with skill='publish'
        AND records with 'publish' in brief text."""
        briefs_path = tmp_path / "briefs.md"
        telemetry_path = tmp_path / "telemetry.jsonl"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        briefs_path.write_text(
            _make_briefs_md([
                "DONE | 2026-05-01 12:00 UTC | STARTED | 2026-05-01 11:00 UTC | publish | released v1.0",
                "DONE | 2026-05-01 14:00 UTC | STARTED | 2026-05-01 13:00 UTC | research | studied publish flow",
                "DONE | 2026-05-01 16:00 UTC | STARTED | 2026-05-01 15:00 UTC | implement | built feature X",
            ]),
            encoding="utf-8",
        )
        telemetry_path.write_text(
            _make_telemetry_jsonl([
                {"skill": "publish", "timestamp": "2026-05-01T11:00:00+00:00", "brief": "released v1.0", "id": "t1"},
                {"skill": "research", "timestamp": "2026-05-01T13:00:00+00:00", "brief": "studied publish flow", "id": "t2"},
                {"skill": "implement", "timestamp": "2026-05-01T15:00:00+00:00", "brief": "built feature X", "id": "t3"},
            ]),
            encoding="utf-8",
        )

        result = reflect_deep_scope.resolve_scope(
            scope="publish",
            since=None,
            until=None,
            briefs_path=briefs_path,
            telemetry_path=telemetry_path,
            output_dir=output_dir,
        )

        # Should match: t1 (skill=publish), t2 (brief contains "publish")
        assert len(result.telemetry_window) == 2
        matched_skills = {r["skill"] for r in result.telemetry_window}
        assert "publish" in matched_skills
        assert "research" in matched_skills
        # Should NOT match implement (no "publish" in skill or brief)
        assert "implement" not in matched_skills

        # Briefs should also match: publish skill line + research brief with "publish"
        assert len(result.briefs_window) == 2

        # Provenance counts should reflect both skill_name and brief_text matches
        assert result.match_counts["skill_name"] >= 1
        assert result.match_counts["brief_text"] >= 1

    def test_since_1d_filters_to_last_24h(self, tmp_path: Path):
        """--since 1d filters to approximately the last 24 hours."""
        briefs_path = tmp_path / "briefs.md"
        telemetry_path = tmp_path / "telemetry.jsonl"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        now = datetime.now(timezone.utc)
        recent = (now - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        old = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        recent_brief_ts = (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        old_brief_ts = (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M")

        briefs_path.write_text(
            _make_briefs_md([
                f"DONE | {recent_brief_ts} UTC | STARTED | {recent_brief_ts} UTC | research | recent work",
                f"DONE | {old_brief_ts} UTC | STARTED | {old_brief_ts} UTC | research | old work",
            ]),
            encoding="utf-8",
        )
        telemetry_path.write_text(
            _make_telemetry_jsonl([
                {"skill": "research", "timestamp": recent, "brief": "recent work", "id": "t1"},
                {"skill": "research", "timestamp": old, "brief": "old work", "id": "t2"},
            ]),
            encoding="utf-8",
        )

        result = reflect_deep_scope.resolve_scope(
            scope=None,
            since="1d",
            until=None,
            briefs_path=briefs_path,
            telemetry_path=telemetry_path,
            output_dir=output_dir,
        )

        # Only the recent record should survive
        assert len(result.telemetry_window) == 1
        assert result.telemetry_window[0]["id"] == "t1"
        assert len(result.briefs_window) == 1

    def test_no_keyword_date_only(self, tmp_path: Path):
        """No-keyword date-only returns the full window within the date range."""
        briefs_path = tmp_path / "briefs.md"
        telemetry_path = tmp_path / "telemetry.jsonl"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        briefs_path.write_text(
            _make_briefs_md([
                "DONE | 2026-05-01 12:00 UTC | STARTED | 2026-05-01 11:00 UTC | research | item A",
                "DONE | 2026-05-01 14:00 UTC | STARTED | 2026-05-01 13:00 UTC | plan | item B",
                "DONE | 2026-05-01 16:00 UTC | STARTED | 2026-05-01 15:00 UTC | implement | item C",
            ]),
            encoding="utf-8",
        )
        telemetry_path.write_text(
            _make_telemetry_jsonl([
                {"skill": "research", "timestamp": "2026-05-01T11:00:00+00:00", "brief": "item A", "id": "t1"},
                {"skill": "plan", "timestamp": "2026-05-01T13:00:00+00:00", "brief": "item B", "id": "t2"},
                {"skill": "implement", "timestamp": "2026-05-01T15:00:00+00:00", "brief": "item C", "id": "t3"},
            ]),
            encoding="utf-8",
        )

        result = reflect_deep_scope.resolve_scope(
            scope=None,
            since=None,
            until=None,
            briefs_path=briefs_path,
            telemetry_path=telemetry_path,
            output_dir=output_dir,
        )

        # All records returned
        assert len(result.telemetry_window) == 3
        assert len(result.briefs_window) == 3
        assert result.match_counts["total_telemetry"] == 3
        assert result.match_counts["total_briefs"] == 3

    def test_empty_result(self, tmp_path: Path):
        """Empty files produce zero match counts and empty windows."""
        briefs_path = tmp_path / "briefs.md"
        telemetry_path = tmp_path / "telemetry.jsonl"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        briefs_path.write_text("# Briefs\n", encoding="utf-8")
        telemetry_path.write_text("", encoding="utf-8")

        result = reflect_deep_scope.resolve_scope(
            scope="anything",
            since=None,
            until=None,
            briefs_path=briefs_path,
            telemetry_path=telemetry_path,
            output_dir=output_dir,
        )

        assert len(result.telemetry_window) == 0
        assert len(result.briefs_window) == 0
        assert len(result.matched_ids) == 0
        # With a scope keyword, provenance counts are all zero
        for count in result.match_counts.values():
            assert count == 0


# ===================================================================
# 3. reflect_event_matrix
# ===================================================================


def _ts(hour: int, minute: int = 0) -> str:
    """ISO timestamp helper for 2026-05-01 at the given hour:minute UTC."""
    return f"2026-05-01T{hour:02d}:{minute:02d}:00+00:00"


class TestEventMatrix:
    """Tests for the event matrix visualization module."""

    def test_overlapping_events_get_different_lanes(self):
        """Two overlapping events on 'implement' get lanes 0 and 1."""
        events = [
            {"skill": "implement", "start": _ts(10, 0), "end": _ts(10, 30)},
            {"skill": "implement", "start": _ts(10, 15), "end": _ts(10, 45)},
        ]
        result = reflect_event_matrix.assign_lanes(events)
        lanes = sorted(e["lane"] for e in result)
        assert lanes == [0, 1]

    def test_nonoverlapping_events_share_lane(self):
        """Three non-overlapping 'research' events all get lane 0."""
        events = [
            {"skill": "research", "start": _ts(9, 0), "end": _ts(9, 30)},
            {"skill": "research", "start": _ts(10, 0), "end": _ts(10, 30)},
            {"skill": "research", "start": _ts(11, 0), "end": _ts(11, 30)},
        ]
        result = reflect_event_matrix.assign_lanes(events)
        lanes = [e["lane"] for e in result]
        assert lanes == [0, 0, 0]

    def test_vegalite_spec_structure(self):
        """Vega-Lite output has $schema key and 11-entry color domain."""
        window = [
            {
                "skill": "research",
                "timestamp": _ts(10),
                "brief": "test brief",
                "duration_seconds": 300,
                "id": "t1",
            },
        ]
        events = reflect_event_matrix.build_events(window)
        events = reflect_event_matrix.assign_lanes(events)
        spec = reflect_event_matrix.build_vegalite_spec(
            events, "test-scope", ("2026-05-01", "2026-05-02"),
        )
        assert "$schema" in spec
        assert "vega-lite" in spec["$schema"]
        domain = spec["encoding"]["color"]["scale"]["domain"]
        assert len(domain) == len(reflect_colors.COLOR_DOMAIN)

    def test_generate_returns_paths(self, tmp_path: Path):
        """generate() returns paths dict with vl_json and html keys."""
        window = [
            {
                "skill": "research",
                "timestamp": _ts(10),
                "brief": "test",
                "duration_seconds": 600,
                "id": "t1",
            },
        ]
        prefix = tmp_path / "event-matrix"
        dr = (
            datetime(2026, 5, 1, tzinfo=timezone.utc),
            datetime(2026, 5, 2, tzinfo=timezone.utc),
        )
        result = reflect_event_matrix.generate(
            window=window,
            output_prefix=prefix,
            title_scope="test-scope",
            date_range=dr,
        )
        assert "vl_json" in result
        assert "html" in result
        assert result["vl_json"].exists()
        assert result["html"].exists()

        # Validate the written JSON
        spec = json.loads(result["vl_json"].read_text(encoding="utf-8"))
        assert "$schema" in spec

    def test_three_way_overlap_uses_three_lanes(self):
        """Three fully overlapping events use lanes 0, 1, 2."""
        events = [
            {"skill": "implement", "start": _ts(10, 0), "end": _ts(10, 30)},
            {"skill": "implement", "start": _ts(10, 5), "end": _ts(10, 35)},
            {"skill": "implement", "start": _ts(10, 10), "end": _ts(10, 40)},
        ]
        result = reflect_event_matrix.assign_lanes(events)
        lanes = sorted(e["lane"] for e in result)
        assert lanes == [0, 1, 2]

    def test_mode_extraction(self):
        """Mode flag substring detection works correctly."""
        assert reflect_event_matrix.extract_mode("deep dive --deep mode") == "--deep"
        assert reflect_event_matrix.extract_mode("plain brief") == "default"
        assert reflect_event_matrix.extract_mode("") == "default"
        assert reflect_event_matrix.extract_mode("--inventory scan") == "--inventory"

    def test_duration_minutes_fallback(self):
        """Missing or zero duration_seconds falls back to 5 minutes."""
        assert reflect_event_matrix.duration_minutes({}) == 5.0
        assert reflect_event_matrix.duration_minutes({"duration_seconds": 0}) == 5.0
        assert reflect_event_matrix.duration_minutes({"duration_seconds": 120}) == 2.0


# ===================================================================
# 4. reflect_transition_graph
# ===================================================================


class TestTransitionGraph:
    """Tests for the transition graph visualization module."""

    def test_edge_label_count(self):
        """3 transitions A->B produce edge label '3'."""
        skills = ["research", "plan", "research", "plan", "research", "plan"]
        # Consecutive pairs: (research,plan), (plan,research), (research,plan), (plan,research), (research,plan)
        pairs = [(skills[i], skills[i + 1]) for i in range(len(skills) - 1)]
        pair_counts = Counter(pairs)
        assert pair_counts[("research", "plan")] == 3

        skill_counts = Counter(skills)
        dot = reflect_transition_graph._build_dot(skill_counts, pair_counts, "test")
        # The edge label for research->plan should be "3"
        assert 'label="3"' in dot

    def test_edge_color_matches_target(self):
        """Edge A->B color equals SKILL_COLORS['B'] (target-colored)."""
        skills = ["research", "plan"]
        pairs = [(skills[i], skills[i + 1]) for i in range(len(skills) - 1)]
        pair_counts = Counter(pairs)
        skill_counts = Counter(skills)
        dot = reflect_transition_graph._build_dot(skill_counts, pair_counts, "test")
        # The edge research->plan should be colored with plan's color
        plan_color = reflect_colors.SKILL_COLORS["plan"]
        # Find the edge line
        for line in dot.split("\n"):
            if '"research" -> "plan"' in line:
                assert plan_color in line
                break
        else:
            pytest.fail("Edge research->plan not found in DOT output")

    def test_node_max_count_width(self):
        """Node with max count gets width 1.60."""
        skill_counts = Counter({"research": 10, "plan": 5, "implement": 1})
        pair_counts = Counter({("research", "plan"): 1})
        dot = reflect_transition_graph._build_dot(skill_counts, pair_counts, "test")
        # research has max count (10), so width = max(0.3, 10/10 * 1.6) = 1.60
        assert "width=1.60" in dot

    def test_self_loop_present(self):
        """Self-loop present for consecutive same-skill invocations."""
        window = [
            {"skill": "research", "timestamp": _ts(10)},
            {"skill": "research", "timestamp": _ts(11)},
            {"skill": "research", "timestamp": _ts(12)},
        ]
        sorted_window = reflect_transition_graph._sort_window(window)
        skills = reflect_transition_graph._extract_skills(sorted_window)
        pairs = [(skills[i], skills[i + 1]) for i in range(len(skills) - 1)]
        pair_counts = Counter(pairs)
        assert ("research", "research") in pair_counts
        assert pair_counts[("research", "research")] == 2

        skill_counts = Counter(skills)
        dot = reflect_transition_graph._build_dot(skill_counts, pair_counts, "test")
        assert '"research" -> "research"' in dot

    def test_dot_output_starts_with_digraph(self):
        """DOT output starts with 'digraph'."""
        skill_counts = Counter({"research": 1})
        pair_counts = Counter()
        dot = reflect_transition_graph._build_dot(skill_counts, pair_counts, "test")
        assert dot.startswith("digraph")

    def test_generate_returns_paths(self, tmp_path: Path):
        """generate() returns paths dict with dot and html keys."""
        window = [
            {"skill": "research", "timestamp": _ts(10), "brief": "a"},
            {"skill": "plan", "timestamp": _ts(11), "brief": "b"},
        ]
        prefix = tmp_path / "transition-graph"
        dr = (
            datetime(2026, 5, 1, tzinfo=timezone.utc),
            datetime(2026, 5, 2, tzinfo=timezone.utc),
        )
        result = reflect_transition_graph.generate(
            window=window,
            output_prefix=prefix,
            title_scope="test-scope",
            date_range=dr,
        )
        assert "dot" in result
        assert "html" in result
        assert result["dot"].exists()
        assert result["html"].exists()

        dot_content = result["dot"].read_text(encoding="utf-8")
        assert dot_content.startswith("digraph")


# ===================================================================
# 5. Non-prescriptive enforcement
# ===================================================================


_FORBIDDEN = [
    "you should",
    "consider changing",
    "we recommend",
    "you might want",
]


class TestNonPrescriptive:
    """Scan all .py source files in the reflect directory for forbidden
    prescriptive substrings in string literals and comments."""

    @pytest.fixture(scope="class")
    def reflect_py_files(self) -> list[Path]:
        reflect_dir = Path(__file__).parent
        return [
            p
            for p in sorted(reflect_dir.glob("*.py"))
            if p.name != Path(__file__).name  # exclude this test file
        ]

    def test_no_prescriptive_language(self, reflect_py_files: list[Path]):
        violations: list[str] = []
        for py_file in reflect_py_files:
            content = py_file.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                # Only check comments and string literals
                is_comment = stripped.startswith("#")
                has_string = '"' in line or "'" in line
                if not is_comment and not has_string:
                    continue
                lower = line.lower()
                for phrase in _FORBIDDEN:
                    if phrase in lower:
                        # Skip meta-references: the phrase appears inside
                        # quotes as an example of what to avoid (e.g.
                        # 'never emits its own "you should"').
                        quoted = f'"{phrase}"'
                        if quoted in lower:
                            continue
                        violations.append(
                            f"{py_file.name}:{lineno}: found '{phrase}' in: {stripped[:80]}"
                        )
        assert not violations, "Prescriptive language found:\n" + "\n".join(violations)
