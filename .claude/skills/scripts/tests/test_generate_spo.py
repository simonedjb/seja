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
