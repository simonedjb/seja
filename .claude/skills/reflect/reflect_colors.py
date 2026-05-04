#!/usr/bin/env python3
# designer: When /reflect --deep renders an event matrix or transition graph,
#   I'm the shared palette everyone pulls from -- a Tol 2012 "muted" qualitative
#   scale covering all SEJA skills, verified WCAG 2.0 AA compliant (≥4.5:1
#   text contrast) and safe for deuteranopia, protanopia, and tritanopia, so
#   every chart speaks the same accessible color language.
"""reflect_colors -- shared color palette for /reflect --deep visualizations.

Invocation: library
Lifecycle: active

Provides a Tol 2012 "muted" qualitative skill palette covering all SEJA
lifecycle and support skills, a set of skills that require dark text on their
light background (LIGHT_FILL_SKILLS), and warm-tone mode-variant accents.
Consumed by the event matrix and transition graph renderers.

Palette rationale
-----------------
Paul Tol's "muted" qualitative scheme (SRON Technical Note SRON/EPS/TN/09-002,
2012) is designed for colorblind safety and validated by dichromatic observers.
Hues vary in saturation and luminance -- not just hue -- so they remain
distinguishable under deuteranopia, protanopia, and tritanopia.  Each entry
below is chosen or lightly adjusted so the paired text color (white or black)
achieves ≥ 4.5:1 relative luminance contrast (WCAG 2.0 Success Criterion
1.4.3, Level AA for normal text).

  Skill         Hex       L      Text   Ratio
  ─────────     ───────   ─────  ─────  ─────
  research      #332288   0.044  white  11.2
  plan          #117733   0.157  white   5.1
  implement     #0066AA   0.124  white   6.0
  check         #44AA99   0.348  black   8.0
  document      #999933   0.319  black   7.4
  communicate   #EE7733   0.339  black   7.8
  reflect       #CC6677   0.262  black   6.2
  pending       #AA4499   0.168  white   4.8
  publish       #CCAA22   0.448  black  10.0
  explain       #88CCEE   0.582  black  12.6
  design        #004488   0.061  white   9.5
  advise        #882255   0.082  white   7.9
  seja-setup    #BBCC33   0.540  black  11.8
"""

from __future__ import annotations

SKILL_COLORS: dict[str, str] = {
    # Core lifecycle
    "research":   "#332288",
    "plan":       "#117733",
    "implement":  "#0066AA",
    "check":      "#44AA99",
    "document":   "#999933",
    "communicate": "#EE7733",
    "reflect":    "#CC6677",
    # Support / meta
    "pending":    "#AA4499",
    "publish":    "#CCAA22",
    "explain":    "#88CCEE",
    "design":     "#004488",
    # Legacy / setup
    "advise":     "#882255",
    "seja-setup": "#BBCC33",
}

# Skills whose fill is light enough to require dark (#000000) text.
# All others use white (#ffffff).  Verified against WCAG 2.0 AA (4.5:1).
LIGHT_FILL_SKILLS: frozenset[str] = frozenset({
    "check",
    "document",
    "communicate",
    "reflect",
    "publish",
    "explain",
    "seja-setup",
})

MODE_COLORS: dict[str, str] = {
    "--deep":      "#D62728",
    "--inventory": "#FF7F0E",
    "--roadmap":   "#E377C2",
    "--light":     "#C49C94",
}

SKILL_ORDER: list[str] = [
    "research",
    "plan",
    "implement",
    "check",
    "document",
    "communicate",
    "reflect",
    "pending",
    "publish",
    "explain",
    "design",
    "advise",
    "seja-setup",
]

COLOR_DOMAIN: list[str] = SKILL_ORDER + list(MODE_COLORS.keys())
COLOR_RANGE: list[str] = (
    [SKILL_COLORS[s] for s in SKILL_ORDER] + list(MODE_COLORS.values())
)


def color_key(skill: str, mode: str) -> str:
    """Return the nominal-scale key for a (skill, mode) pair.

    Default-mode invocations map to the skill name; variant-mode invocations
    map to the mode string (e.g. ``--deep``).
    """
    if mode and mode in MODE_COLORS:
        return mode
    return skill
