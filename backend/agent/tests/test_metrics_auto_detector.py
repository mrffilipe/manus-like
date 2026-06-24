"""Tests for automatic marketing metrics detection."""

from agent.marketing.metrics_auto_detector import (
    auto_detect_marketing_tool_results,
    collect_marketing_context,
    context_has_marketing_metrics,
    merge_tool_results,
)
from agent.marketing.report_formatter import merge_deliverable_with_visuals
from agent.tools.marketing_tools import analyze_funnel

CAMP_4_VS_5_TEXT = """
Relatório Campanha 4 vs Campanha 5

Campanha 4 (Histórico Real):
199 envios
46 lidos (23.1% abertura)
8 visitas na LP (CTR 4.02%)
6 abandonaram no hero
2 rolaram a LP
0 leads gerados

Campanha 5 (Projetada - Pós-Otimização):
199 envios
50 lidos (~25% abertura)
14 visitas na LP (~7% CTR)
5 abandonaram no hero
9 rolaram a LP
1.5 leads gerados

Projeção escala de 1.000 envios: média de 8 leads comerciais prontos para abordagem.
"""


def test_context_has_marketing_metrics():
    assert context_has_marketing_metrics(CAMP_4_VS_5_TEXT)
    assert not context_has_marketing_metrics("Olá, como posso ajudar?")


def test_auto_detect_compare_campaign_scenarios():
    results = auto_detect_marketing_tool_results(CAMP_4_VS_5_TEXT)
    assert len(results) == 1
    assert results[0]["tool"] == "compare_campaign_scenarios"
    assert results[0]["result"].get("visual_blocks")
    assert any("funnel_compare" in block for block in results[0]["result"]["visual_blocks"])


def test_auto_detect_single_funnel():
    text = "Campanha atual: 500 envios, 135 lidos, taxa de abertura 27%, CTR 1.2%, 5 visitas na LP."
    results = auto_detect_marketing_tool_results(text)
    assert len(results) == 1
    assert results[0]["tool"] in ("analyze_funnel", "parse_campaign_report")
    result = results[0]["result"]
    assert result.get("chart_stages") or (result.get("funnel_analysis") or {}).get("chart_stages")


def test_merge_tool_results_manual_priority():
    manual = [{"tool": "analyze_funnel", "result": analyze_funnel(sent=100, opened=30)}]
    auto = auto_detect_marketing_tool_results(CAMP_4_VS_5_TEXT)
    merged = merge_tool_results(manual, auto)
    assert len(merged) == 1
    assert merged[0]["tool"] == "analyze_funnel"


def test_merge_tool_results_fills_compare_gap():
    manual: list[dict] = []
    auto = auto_detect_marketing_tool_results(CAMP_4_VS_5_TEXT)
    merged = merge_tool_results(manual, auto)
    assert len(merged) == 1
    assert merged[0]["tool"] == "compare_campaign_scenarios"


def test_merge_from_conversation_history_without_tools():
    """Simulates critic safety net: metrics only in prior messages, no tool_results."""
    from langchain_core.messages import AIMessage, HumanMessage

    state = {
        "messages": [
            HumanMessage(content=CAMP_4_VS_5_TEXT),
            AIMessage(content="Análise preliminar das campanhas."),
            HumanMessage(content="Quero isso em gráficos"),
        ],
        "attachments": [],
        "client_context": "",
    }
    context = collect_marketing_context(state)  # type: ignore[arg-type]
    auto = auto_detect_marketing_tool_results(context)
    final = merge_deliverable_with_visuals("## Análise\n\nResumo narrativo.", auto)
    assert "```chart" in final
    assert "funnel_compare" in final or "bar_compare" in final
