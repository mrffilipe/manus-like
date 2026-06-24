"""Tests for marketing report visual formatter."""

from agent.marketing.report_formatter import (
    build_bar_compare_block,
    build_campaign_comparison_visuals,
    build_funnel_chart_block,
    build_funnel_compare_block,
    build_projection_block,
    build_visual_preamble,
    merge_deliverable_with_visuals,
)
from agent.tools.marketing_tools import analyze_funnel, compare_campaign_scenarios


def test_build_funnel_chart_block_contains_chart_fence():
    stages = [
        {"label": "Enviados", "pct": 100.0, "absolute": 500},
        {"label": "Abriram", "pct": 27.5, "absolute": 135},
    ]
    block = build_funnel_chart_block(stages, title="Onde o funil quebra")
    assert "```chart" in block
    assert '"type": "funnel"' in block
    assert "Onde o funil quebra" in block


def test_build_funnel_compare_block():
    series = [
        {"name": "Camp. 4", "stages": [{"label": "Disparos", "pct": 100, "absolute": 199}]},
        {"name": "Camp. 5", "stages": [{"label": "Disparos", "pct": 100, "absolute": 199}]},
    ]
    block = build_funnel_compare_block(series)
    assert '"type": "funnel_compare"' in block
    assert "Camp. 4" in block


def test_build_bar_compare_block():
    metrics = [
        {
            "label": "Taxa de Abertura",
            "series": [
                {"name": "Camp. 4", "value": 23.1},
                {"name": "Camp. 5", "value": 25.0, "note": "Melhoria de +8%"},
            ],
        }
    ]
    block = build_bar_compare_block(metrics)
    assert '"type": "bar_compare"' in block
    assert "Melhoria de +8%" in block


def test_build_projection_block():
    scenarios = [
        {"label": "Camp. 4 (199 envios)", "value": 0},
        {"label": "Camp. 5 (199 envios)", "value": 1.5, "range": [1, 2]},
    ]
    block = build_projection_block(scenarios)
    assert '"type": "projection"' in block
    assert '"range"' in block


def test_build_campaign_comparison_visuals():
    baseline = {
        "name": "Campanha 4",
        "sent": 199,
        "opened": 46,
        "lp_visits": 8,
        "hero_bounces": 6,
        "scrolled": 2,
        "leads": 0,
    }
    projected = {
        "name": "Campanha 5",
        "sent": 199,
        "opened": 50,
        "lp_visits": 14,
        "hero_bounces": 5,
        "scrolled": 9,
        "leads": 1.5,
        "leads_range": [1, 2],
    }
    blocks = build_campaign_comparison_visuals(
        baseline,
        projected,
        scale_projected={"sent": 1000, "leads": 8},
    )
    assert len(blocks) == 3
    assert all("```chart" in block for block in blocks)
    assert any("funnel_compare" in block for block in blocks)
    assert any("bar_compare" in block for block in blocks)
    assert any("projection" in block for block in blocks)


def test_build_visual_preamble_empty_without_tools():
    assert build_visual_preamble([]) == ""


def test_build_visual_preamble_from_analyze_funnel():
    funnel = analyze_funnel(sent=500, opened=135, clicked=5, client_name="eBox")
    preamble = build_visual_preamble([{"tool": "analyze_funnel", "result": funnel}])
    assert "Visão consolidada" in preamble
    assert "```chart" in preamble
    assert "Abertura média" in preamble or "CTR médio" in preamble


def test_build_visual_preamble_from_compare_campaign_scenarios():
    comparison = compare_campaign_scenarios(
        baseline_name="Campanha 4",
        projected_name="Campanha 5",
        baseline_sent=199,
        baseline_opened=46,
        baseline_lp_visits=8,
        baseline_scrolled=2,
        baseline_leads=0,
        projected_opened=50,
        projected_lp_visits=14,
        projected_scrolled=9,
        projected_leads=1.5,
    )
    preamble = build_visual_preamble([{"tool": "compare_campaign_scenarios", "result": comparison}])
    assert "Visão consolidada" in preamble
    assert "funnel_compare" in preamble
    assert "bar_compare" in preamble
    assert "projection" in preamble


def test_merge_deliverable_with_visuals():
    funnel = analyze_funnel(sent=500, opened=135, clicked=5)
    merged = merge_deliverable_with_visuals(
        "## Alertas\n\nCTR crítico.",
        [{"tool": "analyze_funnel", "result": funnel}],
    )
    assert "```chart" in merged
    assert "---" in merged
    assert "Alertas" in merged
