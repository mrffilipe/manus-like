"""Tests for marketing intake checklist."""

from agent.marketing.intake import evaluate_intake


def test_intake_incomplete_without_metrics():
    result = evaluate_intake(
        goal="Preciso de ajuda com campanhas",
        client_id="ebox",
    )
    assert result.complete is False
    assert result.next_question is not None


def test_intake_complete_with_metrics_text():
    result = evaluate_intake(
        goal="Analise métricas ebox",
        messages_text="Abertura 27% CTR 0.87% leads na LP 4 conversão form",
        client_id="ebox",
        attachments=[{"filename": "report.txt", "extracted_text": "CTR 1.1% abertura 25%"}],
    )
    assert result.collected["metrics_data"] is True
    assert result.collected["client_confirmed"] is True
