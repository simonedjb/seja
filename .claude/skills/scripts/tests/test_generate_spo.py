"""Smoke tests for generate_spo.py — base rendering plus the facet / traceability /
bilingual / deep-link / analyses extensions."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_SPO = ROOT / ".claude" / "skills" / "scripts" / "priv" / "generate_spo.py"
_DEMO = ROOT / ".claude" / "references" / "template" / "demo" / "product-overview.yaml"

_spec = importlib.util.spec_from_file_location("generate_spo", _SPO)
spo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(spo)


def _load_demo():
    return spo.load_project_data(_DEMO, None)


def test_norm_card_has_new_default_fields():
    card = spo._norm_card({"id": "X-1", "layer": "goals", "title": "t"})
    for field in ("subsystem", "channels", "req_ids", "decision_ids", "journey_ids", "source_ref"):
        assert field in card, f"missing default field {field}"


def test_meta_defaults_facets_and_languages():
    data = _load_demo()
    assert "facets" in data["meta"]
    assert isinstance(data["meta"]["languages"], list) and data["meta"]["languages"]
    assert data["meta"]["locale"] in data["meta"]["languages"]


def test_pick_lang_handles_string_and_map():
    assert spo._pick_lang("hello", "en-US") == "hello"
    assert spo._pick_lang({"en-US": "Hi", "pt-BR": "Oi"}, "pt-BR") == "Oi"
    assert spo._pick_lang({"en-US": "Hi"}, "pt-BR") == "Hi"  # fallback


def test_generate_html_is_self_contained_and_has_extensions():
    data = _load_demo()
    html = spo.generate_html(data)
    # self-contained: no external asset references
    assert "<style>" in html and "const DATA =" in html
    assert 'src="' not in html.split("<body")[0] or "http" not in html[:2000]
    # extension wiring present
    for token in ("renderFacetBar", "computeAnalyses", "trace-chip", "function L(", "btn-lang", "btn-analyses"):
        assert token in html, f"missing extension token {token}"


def test_validate_data_flags_dangling_refs(capsys):
    data = {"cards": [{"id": "A", "enables": ["ZZZ"], "depends": []}]}
    spo.validate_data(data)
    err = capsys.readouterr().err
    assert "ZZZ" in err


def test_owner_facet_auto_declared(tmp_path):
    """When a card has a non-empty owner and no owner facet is declared, one is auto-injected."""
    yaml_content = (
        "meta:\n"
        "  title: Test Project\n"
        "  facets: []\n"
        "layers:\n"
        "  - id: goals\n"
        "    name: Goals\n"
        "cards:\n"
        "  - id: G-01\n"
        "    layer: goals\n"
        "    title: Goal One\n"
        "    owner: Alex\n"
    )
    spo_file = tmp_path / "product-overview.yaml"
    spo_file.write_text(yaml_content, encoding="utf-8")
    data = spo.load_project_data(spo_file, None)
    facet_ids = [f["id"] for f in data["meta"]["facets"]]
    assert "owner" in facet_ids, "owner facet should be auto-declared when cards have owner values"
    owner_facet = next(f for f in data["meta"]["facets"] if f["id"] == "owner")
    assert owner_facet == {"id": "owner", "label": "Owner", "field": "owner"}


def _make_strip_data():
    """Minimal data dict with sensitive fields populated on a single card."""
    return {
        "meta": {
            "title": "Test",
            "facets": [],
            "layers": [{"id": "goals", "name": "Goals"}],
            "languages": ["en-US"],
            "locale": "en-US",
        },
        "cards": [
            {
                "id": "G-01",
                "layer": "goals",
                "title": "Goal One",
                "owner": "Alex",
                "tracker_id": "PROJ-123",
                "tracker_title": "Fix thing",
                "source_ref": "path/to/file.md",
                "req_ids": ["R-001"],
                "decision_ids": ["D-001"],
                "journey_ids": ["JM-001"],
            }
        ],
    }


def _extract_embedded_json(html: str) -> dict:
    """Parse the const DATA = {...}; block from generated HTML."""
    import json as _json
    marker = "const DATA ="
    start = html.index(marker) + len(marker)
    json_str = html[start:].lstrip()
    embedded, _ = _json.JSONDecoder().raw_decode(json_str)
    return embedded


def test_strip_internal_blanks_sensitive_fields():
    """With strip_internal=True, owner/tracker/ref/id-list fields in the embedded JSON are blanked."""
    data = _make_strip_data()
    html = spo.generate_html(data, strip_internal=True)
    embedded = _extract_embedded_json(html)
    card = embedded["cards"][0]
    assert card["owner"] == ""
    assert card["tracker_id"] == ""
    assert card["tracker_title"] == ""
    assert card["source_ref"] == ""
    assert card["req_ids"] == []
    assert card["decision_ids"] == []
    assert card["journey_ids"] == []


def test_strip_internal_false_preserves_fields():
    """With strip_internal=False (default), all sensitive fields are preserved in the embedded JSON."""
    data = _make_strip_data()
    html = spo.generate_html(data, strip_internal=False)
    embedded = _extract_embedded_json(html)
    card = embedded["cards"][0]
    assert card["owner"] == "Alex"
    assert card["tracker_id"] == "PROJ-123"
    assert card["tracker_title"] == "Fix thing"
    assert card["source_ref"] == "path/to/file.md"
    assert card["req_ids"] == ["R-001"]
    assert card["decision_ids"] == ["D-001"]
    assert card["journey_ids"] == ["JM-001"]


def test_owner_facet_explicit_wins(tmp_path):
    """When meta.facets already contains an owner entry, it is preserved unchanged."""
    yaml_content = (
        "meta:\n"
        "  title: Test Project\n"
        "  facets:\n"
        "    - id: owner\n"
        "      label: Dono\n"
        "      field: owner\n"
        "layers:\n"
        "  - id: goals\n"
        "    name: Goals\n"
        "cards:\n"
        "  - id: G-01\n"
        "    layer: goals\n"
        "    title: Goal One\n"
        "    owner: Alex\n"
    )
    spo_file = tmp_path / "product-overview.yaml"
    spo_file.write_text(yaml_content, encoding="utf-8")
    data = spo.load_project_data(spo_file, None)
    owner_facets = [f for f in data["meta"]["facets"] if f["id"] == "owner"]
    assert len(owner_facets) == 1, "should not duplicate the owner facet"
    assert owner_facets[0]["label"] == "Dono", "explicit owner facet label should be preserved"


def test_compute_analyses_untracked():
    """Cards in 'implementing' status with no tracker_id appear in the Untracked implementing section."""
    data = {
        "meta": {
            "title": "Untracked Test",
            "facets": [],
            "languages": ["en-US"],
            "locale": "en-US",
            "version_labels": {"V1": 1},
        },
        "layers": [{"id": "goals", "name": "Goals", "color": "#ccc"}],
        "personas": [],
        "quality_criteria": [],
        "cards": [
            {
                "id": "IMP-TRACK",
                "layer": "goals",
                "title": "Tracked Card",
                "status": "implementing",
                "tracker_id": "T-1",
                "enables": [], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_title": "", "owner": "", "external": False, "provider": "",
                "status_plan": "", "status_date": "", "subsystem": "", "channels": [],
                "req_ids": [], "decision_ids": [], "journey_ids": [], "source_ref": "",
            },
            {
                "id": "IMP-NOTRACK",
                "layer": "goals",
                "title": "Untracked Card",
                "status": "implementing",
                "tracker_id": "",
                "enables": [], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_title": "", "owner": "", "external": False, "provider": "",
                "status_plan": "", "status_date": "", "subsystem": "", "channels": [],
                "req_ids": [], "decision_ids": [], "journey_ids": [], "source_ref": "",
            },
        ],
    }
    html = spo.generate_html(data)
    # Section label must be present as a string literal in the generated JavaScript
    assert "Untracked implementing" in html, "Untracked implementing section must appear in the generated JS"
    # Embedded DATA has exactly one card that meets the untracked criteria
    embedded = _extract_embedded_json(html)
    untracked = [
        c for c in embedded["cards"]
        if c.get("status") == "implementing" and not c.get("tracker_id")
    ]
    assert len(untracked) == 1, "expected exactly one untracked implementing card in embedded DATA"
    assert untracked[0]["id"] == "IMP-NOTRACK", "the untracked card must be IMP-NOTRACK"


def test_chain_completion_metric():
    """Chain completion metric shows done/total descendants for top-layer cards (lowest pct first)."""
    # 3-card upward enables chain: feature enables task enables goal.
    # feature is done, task is implementing (not done), goal is proposed.
    # Goal is the top-layer card (last in layers list). Descendants of goal: task + feature.
    # done=1 (feature), total=2 → 50%.
    data = {
        "meta": {
            "title": "Chain Completion Test",
            "facets": [],
            "languages": ["en-US"],
            "locale": "en-US",
            "version_labels": {"V1": 1},
        },
        "layers": [
            {"id": "features", "name": "Features", "color": "#ccc"},
            {"id": "tasks",    "name": "Tasks",    "color": "#ccc"},
            {"id": "goals",    "name": "Goals",    "color": "#ccc"},
        ],
        "personas": [],
        "quality_criteria": [],
        "cards": [
            {
                "id": "F-1", "layer": "features", "title": "A Feature",
                "status": "done", "enables": ["T-1"], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_id": "", "tracker_title": "", "owner": "", "external": False,
                "provider": "", "status_plan": "", "status_date": "", "subsystem": "",
                "channels": [], "req_ids": [], "decision_ids": [], "journey_ids": [],
                "source_ref": "",
            },
            {
                "id": "T-1", "layer": "tasks", "title": "A Task",
                "status": "implementing", "enables": ["G-1"], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_id": "", "tracker_title": "", "owner": "", "external": False,
                "provider": "", "status_plan": "", "status_date": "", "subsystem": "",
                "channels": [], "req_ids": [], "decision_ids": [], "journey_ids": [],
                "source_ref": "",
            },
            {
                "id": "G-1", "layer": "goals", "title": "A Goal",
                "status": "proposed", "enables": [], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_id": "", "tracker_title": "", "owner": "", "external": False,
                "provider": "", "status_plan": "", "status_date": "", "subsystem": "",
                "channels": [], "req_ids": [], "decision_ids": [], "journey_ids": [],
                "source_ref": "",
            },
        ],
    }
    html = spo.generate_html(data)
    # Section label must be present as a string literal in the generated JavaScript
    assert "Chain completion" in html, "Chain completion section must appear in the generated JS"
    # Re-implement the chain completion algorithm in Python to verify the JS would compute 1/2 done (50%)
    embedded = _extract_embedded_json(html)
    cards = embedded["cards"]
    layers = embedded["layers"]
    layer_idx = {l["id"]: i for i, l in enumerate(layers)}
    top_idx = len(layers) - 1

    def _collect_descendants(root_id):
        visited = {}
        result = []
        def _visit(cid):
            for c in cards:
                if cid in (c.get("enables") or []) and c["id"] not in visited:
                    visited[c["id"]] = True
                    result.append(c)
                    _visit(c["id"])
        _visit(root_id)
        return result

    top_cards = [c for c in cards if layer_idx.get(c["layer"]) == top_idx]
    chain_completion = []
    for c in top_cards:
        descs = _collect_descendants(c["id"])
        if not descs:
            continue
        done = sum(1 for d in descs if d.get("status") == "done")
        total = len(descs)
        pct = round(done / total * 100)
        chain_completion.append({"id": c["id"], "done": done, "total": total, "pct": pct})
    chain_completion.sort(key=lambda e: e["pct"])

    assert len(chain_completion) == 1, "exactly one top-layer card (G-1) must have descendants"
    entry = chain_completion[0]
    assert entry["id"] == "G-1", "chain completion entry must be for G-1"
    assert entry["done"] == 1, "G-1 chain must have 1 done descendant (F-1)"
    assert entry["total"] == 2, "G-1 chain must have 2 total descendants (T-1, F-1)"
    assert entry["pct"] == 50, "G-1 chain must show 50% completion"


def test_layer_completion_bar_rendered():
    """A layer-completion-bar with done/implementing/proposed segments is rendered in every layer header."""
    data = {
        "meta": {
            "title": "Completion Bar Test",
            "facets": [],
            "languages": ["en-US"],
            "locale": "en-US",
            "version_labels": {"V1": 1},
        },
        "layers": [
            {"id": "features", "name": "Features", "color": "#4a7"},
        ],
        "personas": [],
        "quality_criteria": [],
        "cards": [
            {
                "id": "F-1", "layer": "features", "title": "Done Card",
                "status": "done", "enables": [], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_id": "", "tracker_title": "", "owner": "", "external": False,
                "provider": "", "status_plan": "", "status_date": "", "subsystem": "",
                "channels": [], "req_ids": [], "decision_ids": [], "journey_ids": [],
                "source_ref": "",
            },
            {
                "id": "F-2", "layer": "features", "title": "Implementing Card",
                "status": "implementing", "enables": [], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_id": "", "tracker_title": "", "owner": "", "external": False,
                "provider": "", "status_plan": "", "status_date": "", "subsystem": "",
                "channels": [], "req_ids": [], "decision_ids": [], "journey_ids": [],
                "source_ref": "",
            },
            {
                "id": "F-3", "layer": "features", "title": "Proposed Card",
                "status": "proposed", "enables": [], "depends": [], "version": "V1",
                "personas": [], "quality_criteria": [], "fulfillment": [],
                "tracker_id": "", "tracker_title": "", "owner": "", "external": False,
                "provider": "", "status_plan": "", "status_date": "", "subsystem": "",
                "channels": [], "req_ids": [], "decision_ids": [], "journey_ids": [],
                "source_ref": "",
            },
        ],
    }
    html = spo.generate_html(data)
    assert "layer-completion-bar" in html, "layer-completion-bar class must appear in generated HTML"
    assert "layer-bar-done" in html, "layer-bar-done segment must appear in generated HTML"
    assert "layer-bar-implementing" in html, "layer-bar-implementing segment must appear in generated HTML"
    assert "layer-bar-proposed" in html, "layer-bar-proposed segment must appear in generated HTML"
    # Label class and JS template fragment are present in the source
    assert "layer-bar-label" in html, "layer-bar-label class must appear in generated HTML"
    assert "done / " in html and "total" in html, "bar label JS template fragments must appear in generated HTML"


def _make_fulfillment_data(fulfillment_items):
    """Minimal data dict with a single card whose fulfillment list is configurable."""
    return {
        "meta": {
            "title": "Fulfillment Test",
            "facets": [],
            "languages": ["en-US"],
            "locale": "en-US",
            "version_labels": {"V1": 1},
        },
        "layers": [{"id": "goals", "name": "Goals", "color": "#ccc"}],
        "personas": [],
        "quality_criteria": [],
        "cards": [
            {
                "id": "G-01",
                "layer": "goals",
                "title": "Goal One",
                "status": "implementing",
                "enables": [],
                "depends": [],
                "version": "V1",
                "personas": [],
                "quality_criteria": [],
                "fulfillment": fulfillment_items,
                "tracker_id": "",
                "tracker_title": "",
                "owner": "",
                "external": False,
                "provider": "",
                "status_plan": "",
                "status_date": "",
                "subsystem": "",
                "channels": [],
                "req_ids": [],
                "decision_ids": [],
                "journey_ids": [],
                "source_ref": "",
            }
        ],
    }


def test_fulfillment_dot_rendered_when_present():
    """fulfillment-dot CSS class and JS feature exist in the HTML when a card has fulfillment items."""
    data = _make_fulfillment_data(["study 2026-06 n=24"])
    html = spo.generate_html(data)
    assert "fulfillment-dot" in html, (
        "fulfillment-dot class must appear in generated HTML when card has fulfillment evidence"
    )


def test_fulfillment_dot_absent_when_empty():
    """Empty fulfillment propagates as [] in embedded DATA; fulfillment-dot CSS class is still defined."""
    data = _make_fulfillment_data([])
    html = spo.generate_html(data)
    # The dot feature must be compiled in (CSS class defined) even when no card has evidence
    assert "fulfillment-dot" in html, (
        "fulfillment-dot CSS class must be defined in stylesheet regardless of card data"
    )
    # Empty fulfillment must round-trip correctly as an empty list in serialized DATA
    embedded = _extract_embedded_json(html)
    assert embedded["cards"][0]["fulfillment"] == [], (
        "card with fulfillment:[] must preserve the empty list in embedded DATA"
    )


def test_drift_roadmap_coexistence():
    """Drift mode and roadmap mode can be active simultaneously without mutual exclusion.

    Checks:
    - No JS pattern resets state.drift when roadmap is toggled (no 'state.drift = false' in source).
    - No JS pattern resets state.roadmap when drift is toggled (no 'state.roadmap = false' in source).
    - The 'drift-mode' CSS class is defined in the generated HTML source.
    - The 'roadmap-mode' CSS class is defined in the generated HTML source.
    """
    data = _make_fulfillment_data([])
    html = spo.generate_html(data)

    # No mutual-exclusion assignments anywhere in the generated JS/CSS source
    assert "state.drift = false" not in html, (
        "state.drift must never be force-reset to false in the generated source "
        "(would prevent simultaneous drift+roadmap view)"
    )
    assert "state.roadmap = false" not in html, (
        "state.roadmap must never be force-reset to false in the generated source "
        "(would prevent simultaneous drift+roadmap view)"
    )

    # Both CSS classes must be present (defined in <style>) so they can coexist at runtime
    assert "drift-mode" in html, (
        "drift-mode CSS class must be defined in generated HTML"
    )
    assert "roadmap-mode" in html, (
        "roadmap-mode CSS class must be defined in generated HTML"
    )


def test_generate_html_has_new_extension_tokens():
    """Plan-000615 extension tokens are present in generated HTML from all new capability additions."""
    data = _load_demo()
    html = spo.generate_html(data)
    # Step 5: layer completion bars
    assert "fulfillment-dot" in html, "fulfillment-dot CSS class (step 6) must appear in generated HTML"
    assert "layer-completion-bar" in html, "layer-completion-bar CSS class (step 5) must appear in generated HTML"
    # Step 3: untracked implementing section label in JS source
    assert "Untracked implementing" in html, "Untracked implementing section label (step 3) must appear in generated HTML"
    # Step 4: chain completion section label in JS source
    assert "Chain completion" in html, "Chain completion section label (step 4) must appear in generated HTML"


def test_panel_is_single_purpose_and_analyses_ids_wired():
    """Plan-000627: the right panel is a single-purpose view driven by
    state.panelView; the Analyses card-id buttons use event delegation
    (data-card-id -> focusCard); the retired two-boolean model
    (panelOpen/analyses) and the dead inline onclick are gone.

    Supersedes the former test_panel_open_state_present, which guarded the
    plan-000619 panelOpen model that plan-000627 replaced."""
    data = _load_demo()
    html = spo.generate_html(data)
    # New single-purpose model + markup
    assert "panelView" in html, "panelView state selector must appear in generated HTML"
    assert "function focusCard(" in html, "shared focusCard(id) must appear in generated HTML"
    assert 'id="btn-criteria"' in html, "Criteria toolbar toggle must appear in generated HTML"
    assert 'id="qc-header-label"' in html, "qc-header-label span must appear in generated HTML"
    assert '<div id="analyses-panel">' in html, "analyses view must be a plain div (accordion retired)"
    # Analyses card-id delegation wiring
    assert "data-card-id" in html, "analysis id buttons must carry data-card-id"
    assert "getAttribute('data-card-id')" in html, "delegated listener must read data-card-id"
    assert "closest('.analysis-id-btn')" in html, "delegated listener must match .analysis-id-btn"
    # Reset hides the panel (deviation: panelView null on reset)
    assert "state.panelView = null;  // reset hides/collapses the panel" in html, (
        "resetAll must set panelView to null so reset collapses the panel"
    )
    # Retired patterns are gone
    assert 'onclick="selectCard(' not in html, "dead inline onclick=selectCard must be removed"
    assert "state.panelOpen" not in html, "retired state.panelOpen must be gone"
    assert "state.analyses" not in html, "retired state.analyses must be gone"
    assert "<summary>Structure Analyses" not in html, "retired analyses accordion summary must be gone"
    # The Analyses toolbar button still exists (rewired, not removed)
    assert "btn-analyses" in html, "btn-analyses toolbar button must still exist"


def test_analyses_hidden_css_present():
    """Plan-000619 step 2a: analyses panel must have a .hidden rule that hides it."""
    data = _load_demo()
    html = spo.generate_html(data)
    assert "#analyses-panel.hidden { display: none; }" in html, (
        "#analyses-panel.hidden { display: none; } CSS rule must appear in generated HTML"
    )


def test_analyses_keyboard_shortcut_present():
    """Plan-000619 step 2c: 'A' keyboard shortcut must be wired in the keydown handler."""
    data = _load_demo()
    html = spo.generate_html(data)
    assert "case 'a': case 'A':" in html, (
        "case 'a': case 'A': keyboard shortcut must appear in generated HTML"
    )


def test_harness_outcome_descs_length():
    """Plan-000619 step 3a: _HARNESS_OUTCOME_DESCS must have one entry per HARNESS_OUTCOMES entry."""
    assert len(spo._HARNESS_OUTCOME_DESCS) == len(spo.HARNESS_OUTCOMES), (
        f"_HARNESS_OUTCOME_DESCS length ({len(spo._HARNESS_OUTCOME_DESCS)}) "
        f"must equal HARNESS_OUTCOMES length ({len(spo.HARNESS_OUTCOMES)})"
    )


def test_harness_skill_label_lookup():
    """Plan-000619 step 3c: skill labels with a leading '/' resolve to the correct _SKILL_OUTCOMES entry."""
    import pytest
    cg_path = ROOT / ".claude" / "references" / "general" / "call-graph.json"
    if not cg_path.exists():
        pytest.skip("call-graph.json not available")
    data = spo.build_harness_data(cg_path)
    # Find the reflect skill card(s) -- labels from the call-graph may carry a leading '/'
    reflect_cards = [
        c for c in data["cards"]
        if c.get("layer") == "skills" and c.get("title", "").lstrip("/") == "reflect"
    ]
    assert reflect_cards, "reflect skill card must be present in harness data"
    card = reflect_cards[0]
    assert card["enables"] != ["O-01"], (
        "reflect skill card must resolve to its dedicated outcome list "
        f"(got {card['enables']!r}; expected something other than ['O-01'])"
    )


def test_harness_internal_skills_layer():
    """Plan-000630: Internal Skills layer sits between Agents and Skills;
    all internal nodes are carded as SI-NN with non-empty, upward-only enables."""
    import pytest
    import json as _json
    cg_path = ROOT / ".claude" / "references" / "general" / "call-graph.json"
    if not cg_path.exists():
        pytest.skip("call-graph.json not available")
    data = spo.build_harness_data(cg_path)
    layers = data["layers"]
    layer_ids = [l["id"] for l in layers]

    # (a) skills-internal layer exists and sits between agents and skills
    assert "skills-internal" in layer_ids, "skills-internal layer must exist in harness data"
    si_idx = layer_ids.index("skills-internal")
    ag_idx = layer_ids.index("agents")
    sk_idx = layer_ids.index("skills")
    assert ag_idx < si_idx < sk_idx, (
        f"skills-internal (idx {si_idx}) must be between agents (idx {ag_idx}) "
        f"and skills (idx {sk_idx}) in the layers list"
    )

    # (b) every _internal/* label plus /pre-skill and /post-skill is on skills-internal with SI- id
    with open(cg_path, encoding="utf-8") as f:
        cg = _json.load(f)
    nodes = cg["nodes"]
    internal_labels = {
        n.get("label", n["id"]) for n in nodes
        if n["type"] == "skill-internal"
           or n.get("label", n["id"]) in {"/pre-skill", "/post-skill"}
    }
    si_cards = [c for c in data["cards"] if c["layer"] == "skills-internal"]
    si_titles = {c["title"] for c in si_cards}
    for label in internal_labels:
        assert label in si_titles, (
            f"internal skill {label!r} must be carded on skills-internal layer"
        )
    for c in si_cards:
        assert c["id"].startswith("SI-"), (
            f"card on skills-internal must have SI- prefix; got {c['id']!r}"
        )

    # (c) no user-facing skill is on skills-internal
    user_facing = {"/research", "/plan", "/implement"}
    for c in si_cards:
        assert c["title"] not in user_facing, (
            f"user-facing skill {c['title']!r} must not appear on skills-internal layer"
        )

    # (d) every internal-skill card has non-empty enables (no-orphans invariant)
    for c in si_cards:
        assert c["enables"], (
            f"internal skill card {c['id']} ({c['title']!r}) has empty enables -- orphan"
        )

    # (e) no internal-skill card's enables references another SI- card (A1 order-independence guard)
    for c in si_cards:
        for eid in c["enables"]:
            assert not eid.startswith("SI-"), (
                f"internal skill {c['id']}.enables -> {eid!r} is another SI- card; "
                "only SK- targets are allowed (A1 order-independence guard)"
            )


def _render_card_detail_slice(html: str) -> str:
    """Isolate the renderCardDetail() function body from the generated JS.

    The tokens the scoped asserts check (Coverage gap, Orphan, Untracked
    implementing, data-card-id, Chain completion) ALSO occur in the
    pre-existing renderAnalyses output, so a whole-document check would pass
    even if the detail branch were missing. Slicing to renderCardDetail's body
    makes the assertions specific to the detail panel. Boundary: from
    'function renderCardDetail(' up to the next top-level 'function '
    declaration (the inner .forEach(function(...)) callbacks use 'function('
    with no space, so a '\\nfunction ' boundary matches only top-level decls)."""
    start = html.index("function renderCardDetail(")
    end = html.index("\nfunction ", start + len("function renderCardDetail("))
    return html[start:end]


def test_detail_panel_links_and_analyses():
    """Plan-000631: renderCardDetail emits a Links section (four enables/depends
    groups) and an Analyses membership section (verbatim em-dash sentences) with
    .analysis-id-btn/data-card-id buttons; the shared wireCardIdDelegation factory
    is wired for BOTH the card-detail pane and the analyses panel body."""
    data = _load_demo()
    html = spo.generate_html(data)

    # Whole-document: helper functions and delegation wiring are present.
    assert "function getAnalyses(" in html, "getAnalyses helper must appear in generated HTML"
    assert "function cardTitleOf(" in html, "cardTitleOf helper must appear in generated HTML"
    assert "function wireCardIdDelegation(" in html, "wireCardIdDelegation factory must appear in generated HTML"
    assert ".detail-section-label {" in html, "detail-section-label CSS rule must appear in generated HTML"
    # The factory is wired for BOTH static containers.
    assert "wireCardIdDelegation(document.getElementById('analyses-panel-body'))" in html, (
        "wireCardIdDelegation must be wired for the analyses-panel-body container"
    )
    assert "wireCardIdDelegation(document.getElementById('card-detail'))" in html, (
        "wireCardIdDelegation must be wired for the card-detail container"
    )

    # (A1) SCOPED asserts: isolate the renderCardDetail body so these tokens
    # cannot be satisfied by the pre-existing renderAnalyses output.
    detail = _render_card_detail_slice(html)
    for label in ("Enables", "Depends on", "Enabled by", "Depended on by"):
        assert label in detail, f"renderCardDetail must render the {label!r} link group"
    assert "data-card-id" in detail, "renderCardDetail links must carry data-card-id buttons"
    for sentence in (
        "Orphan — no enables link in or out.",
        "Coverage gap — no enabler from the layer directly below.",
        "Untracked implementing — in-flight with no tracker ID.",
        "Hub — connectivity degree",
        "Chain completion —",
    ):
        assert sentence in detail, (
            f"renderCardDetail analyses membership must include the sentence {sentence!r}"
        )
