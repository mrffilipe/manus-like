"""Tests for critic deliverable merge with visuals."""

from langchain_core.messages import AIMessage, HumanMessage

from agent.graph.nodes.critic import _parse_deliverable
from agent.marketing.metrics_auto_detector import auto_detect_marketing_tool_results, collect_marketing_context
from agent.marketing.report_formatter import merge_deliverable_with_visuals
from agent.tools.marketing_tools import analyze_funnel

CAMP_4_VS_5_TEXT = """
Campanha 4 vs Campanha 5
Campanha 4: 199 envios, 46 lidos, 8 visitas na LP, 2 rolaram, 0 leads.
Campanha 5: 199 envios, 50 lidos, 14 visitas na LP, 9 rolaram, 1.5 leads.
Escala 1.000 envios: média de 8 leads.
"""


def test_merge_includes_chart_in_final_deliverable():
    funnel = analyze_funnel(sent=500, opened=135, clicked=5, client_name="eBox")
    tool_results = [{"tool": "analyze_funnel", "result": funnel}]
    narrative = "## Alertas críticos\n\nCTR abaixo do ideal."
    final = merge_deliverable_with_visuals(narrative, tool_results)
    assert "```chart" in final
    assert "Alertas críticos" in final


def test_parse_deliverable_multiline():
    text = """DECISION: DONE
DELIVERABLE: ## Hipóteses

1. CTA fraco
SUMMARY: done"""
    parsed = _parse_deliverable(text)
    assert parsed is not None
    assert "Hipóteses" in parsed


def test_auto_merge_from_history_when_tool_results_empty():
    state = {
        "messages": [
            HumanMessage(content=CAMP_4_VS_5_TEXT),
            HumanMessage(content="Quero isso em gráficos"),
        ],
        "attachments": [],
        "client_context": "",
    }
    context = collect_marketing_context(state)  # type: ignore[arg-type]
    auto = auto_detect_marketing_tool_results(context)
    final = merge_deliverable_with_visuals("## Relatório visual\n\nAnálise.", auto)
    assert "```chart" in final
