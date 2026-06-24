"""Tests for marketing tools."""

from agent.tools.marketing_tools import analyze_funnel, audit_email_copy, generate_prompt_package, parse_campaign_report


def test_analyze_funnel_ctr_bottleneck():
    result = analyze_funnel(sent=500, opened=135, clicked=1)
    assert result["rates"]["open_rate"] == 27.0
    assert result["rates"]["ctr"] is not None
    assert result["bottleneck"] == "open_to_click"


def test_audit_email_copy_detects_question_cta():
    result = audit_email_copy("Oi João!\n\nVocê tem esse desafio na empresa?")
    assert result["score"] <= 7
    assert any("pergunta" in issue.lower() for issue in result["issues"])


def test_parse_campaign_report():
    text = "Abertura média 25,7% e CTR médio 0,7% crítico"
    result = parse_campaign_report(text)
    assert "open_rate_pct" in result or "funnel_analysis" in result


def test_generate_prompt_package():
    result = generate_prompt_package(
        client_name="eBox",
        product="eBox Digital",
        differentiators=["ISO 27001"],
        constraints=["Sem links no corpo"],
    )
    assert "knowledge_base" in result
    assert "instruction" in result
    assert "eBox" in result["knowledge_base"]
