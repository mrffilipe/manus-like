"""Proactive intake checklist for marketing consultant mode."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntakeItem:
    key: str
    label: str
    question: str
    options: list[str] = field(default_factory=list)


INTAKE_ITEMS: list[IntakeItem] = [
    IntakeItem(
        key="client_confirmed",
        label="Cliente identificado",
        question="Qual cliente vamos trabalhar agora?",
        options=["Ebox", "Dochr", "Ambos em paralelo", "Outro"],
    ),
    IntakeItem(
        key="funnel_stage",
        label="Estágio do funil",
        question="Qual estágio do funil você quer atacar primeiro?",
        options=[
            "Atenção",
            "Consideração",
            "Decisão",
            "O problema atravessa todos os estágios",
        ],
    ),
    IntakeItem(
        key="has_metrics",
        label="Métricas disponíveis",
        question="Você tem métricas de campanha para compartilhar agora?",
        options=["Sim, tenho dados concretos", "Tenho parcialmente", "Ainda não"],
    ),
    IntakeItem(
        key="metrics_data",
        label="Dados de métricas",
        question=(
            "Envie as métricas (pode colar tabela, texto ou anexar relatório). "
            "Preciso por cliente: abertura, CTR, leads na LP, conversão no form, "
            "tamanho da base e ICP predominante."
        ),
    ),
    IntakeItem(
        key="email_samples",
        label="Copies de email",
        question="Pode enviar exemplos de emails do fluxo (atenção, consideração ou decisão)?",
    ),
    IntakeItem(
        key="landing_page",
        label="Landing page",
        question="Envie o conteúdo ou URL da landing page para auditoria.",
    ),
    IntakeItem(
        key="prompts",
        label="Prompts do gerador",
        question="Se usa IA 1:1, envie os arquivos de base de conhecimento e instrução.",
    ),
]


@dataclass
class IntakeChecklist:
    collected: dict[str, bool] = field(default_factory=dict)
    complete: bool = False
    missing: list[str] = field(default_factory=list)
    next_question: str | None = None
    next_options: list[str] | None = None
    next_key: str | None = None


def _text_blob(goal: str, messages_text: str, attachments: list[dict[str, Any]]) -> str:
    parts = [goal, messages_text]
    for attachment in attachments:
        parts.append(attachment.get("filename", ""))
        parts.append(attachment.get("extracted_text", ""))
    return "\n".join(parts).lower()


def _has_metrics_in_text(blob: str) -> bool:
    indicators = ["ctr", "abertura", "clique", "lp", "convers", "leads", "%", "taxa"]
    hits = sum(1 for word in indicators if word in blob)
    return hits >= 2


def _has_email_copy(blob: str) -> bool:
    return any(
        token in blob
        for token in ["assunto:", "subject:", "email 1", "e-mail", "oi ", "olá"]
    )


def _has_landing_page(blob: str) -> bool:
    return any(
        token in blob
        for token in ["landing", "lp ", "formulário", "headline", "vercel.app", "lp."]
    )


def _has_prompts(blob: str) -> bool:
    return any(
        token in blob
        for token in ["sequência", "base de conhecimento", "instrução", "system", "prompt"]
    )


def evaluate_intake(
    *,
    goal: str,
    messages_text: str = "",
    attachments: list[dict[str, Any]] | None = None,
    client_id: str | None = None,
    require_full: bool = False,
) -> IntakeChecklist:
    attachments = attachments or []
    blob = _text_blob(goal, messages_text, attachments)
    collected: dict[str, bool] = {}

    collected["client_confirmed"] = bool(client_id) or any(
        name in blob for name in ["ebox", "dochr", "ambos"]
    )

    collected["funnel_stage"] = any(
        stage in blob
        for stage in ["atenção", "consideração", "decisão", "todos os estágios", "funil"]
    )

    has_metrics = _has_metrics_in_text(blob)
    collected["has_metrics"] = has_metrics or "tenho dados" in blob or "métricas" in blob
    collected["metrics_data"] = has_metrics

    collected["email_samples"] = _has_email_copy(blob)
    collected["landing_page"] = _has_landing_page(blob)
    collected["prompts"] = _has_prompts(blob)

    required_keys = ["client_confirmed", "funnel_stage", "has_metrics"]
    if require_full:
        required_keys.extend(["metrics_data", "email_samples"])

    missing = [item.key for item in INTAKE_ITEMS if item.key in required_keys and not collected.get(item.key)]

    next_item: IntakeItem | None = None
    for item in INTAKE_ITEMS:
        if item.key in missing:
            next_item = item
            break
        if item.key == "metrics_data" and collected.get("has_metrics") and not collected.get("metrics_data"):
            next_item = item
            break

    complete = next_item is None

    return IntakeChecklist(
        collected=collected,
        complete=complete,
        missing=missing,
        next_question=next_item.question if next_item else None,
        next_options=next_item.options or None if next_item else None,
        next_key=next_item.key if next_item else None,
    )
