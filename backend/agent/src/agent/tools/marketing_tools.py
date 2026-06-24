"""Marketing domain tools for funnel analysis, copy audit, and prompt generation."""

from __future__ import annotations

import json
import re
from typing import Any

from agent.marketing.report_formatter import build_campaign_comparison_visuals, build_chart_stages


def _safe_rate(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 2)


def analyze_funnel(
    *,
    sent: int | None = None,
    opened: int | None = None,
    clicked: int | None = None,
    lp_visits: int | None = None,
    form_fills: int | None = None,
    qualified: int | None = None,
    scheduled: int | None = None,
    sales: int | None = None,
    open_rate_pct: float | None = None,
    ctr_pct: float | None = None,
    client_name: str | None = None,
    title: str | None = None,
    leads_generated: int | None = None,
    email_waves: int | None = None,
) -> dict[str, Any]:
    """Compute funnel rates and identify the main bottleneck."""
    rates: dict[str, float | None] = {}

    if open_rate_pct is not None:
        rates["open_rate"] = open_rate_pct
    elif sent and opened is not None:
        rates["open_rate"] = _safe_rate(opened, sent)

    if ctr_pct is not None:
        rates["ctr"] = ctr_pct
    elif opened and clicked is not None:
        rates["ctr"] = _safe_rate(clicked, opened)

    if clicked and lp_visits is not None:
        rates["click_to_lp"] = _safe_rate(lp_visits, clicked)

    if lp_visits and form_fills is not None:
        rates["lp_conversion"] = _safe_rate(form_fills, lp_visits)

    if form_fills and qualified is not None:
        rates["qualification_rate"] = _safe_rate(qualified, form_fills)

    bottleneck = "unknown"
    recommendations: list[str] = []

    ctr = rates.get("ctr")
    open_rate = rates.get("open_rate")
    lp_conv = rates.get("lp_conversion")

    if open_rate is not None and open_rate >= 20 and ctr is not None and ctr < 1.5:
        bottleneck = "open_to_click"
        recommendations.append(
            "Abertura saudável mas CTR baixo: foco no corpo do email e CTA antes do botão."
        )
    elif ctr is not None and ctr >= 1.5 and lp_conv is not None and lp_conv < 3:
        bottleneck = "lp_conversion"
        recommendations.append(
            "CTR aceitável mas LP converte pouco: revisar prova social, headline e formulário."
        )
    elif open_rate is not None and open_rate < 20:
        bottleneck = "open_rate"
        recommendations.append("Taxa de abertura baixa: revisar assunto e segmentação.")

    if ctr is not None and ctr < 2:
        recommendations.append(f"Meta de CTR: 2-3%. Atual: {ctr}%.")

    chart_stages = build_chart_stages(
        sent=sent,
        opened=opened,
        clicked=clicked,
        lp_visits=lp_visits,
        form_fills=form_fills,
        open_rate_pct=open_rate_pct,
        ctr_pct=ctr_pct,
    )

    return {
        "rates": rates,
        "bottleneck": bottleneck,
        "recommendations": recommendations,
        "chart_stages": chart_stages,
        "chart_title": title or "Onde o funil quebra",
        "client_name": client_name,
        "leads_generated": leads_generated,
        "email_waves": email_waves,
        "lp_leads": lp_visits,
        "qualified": qualified,
        "scheduled": scheduled,
        "sales": sales,
        "summary": (
            f"Gargalo principal: {bottleneck}. "
            + "; ".join(recommendations[:2])
            if recommendations
            else "Dados insuficientes para diagnóstico completo."
        ),
    }


def compare_campaign_scenarios(
    *,
    baseline_name: str = "Campanha baseline",
    projected_name: str = "Campanha projetada",
    baseline_sent: int,
    baseline_opened: int | None = None,
    baseline_lp_visits: int | None = None,
    baseline_hero_bounces: int | None = None,
    baseline_scrolled: int | None = None,
    baseline_leads: float | None = None,
    projected_sent: int | None = None,
    projected_opened: int | None = None,
    projected_lp_visits: int | None = None,
    projected_hero_bounces: int | None = None,
    projected_scrolled: int | None = None,
    projected_leads: float | None = None,
    projected_leads_range: list[float] | None = None,
    scale_sent: int | None = None,
    scale_leads: float | None = None,
    scale_leads_range: list[float] | None = None,
) -> dict[str, Any]:
    """Compare baseline vs optimized campaign and emit chart blocks for the UI."""
    baseline = {
        "name": baseline_name,
        "sent": baseline_sent,
        "opened": baseline_opened,
        "lp_visits": baseline_lp_visits,
        "hero_bounces": baseline_hero_bounces,
        "scrolled": baseline_scrolled,
        "leads": baseline_leads,
    }
    projected = {
        "name": projected_name,
        "sent": projected_sent or baseline_sent,
        "opened": projected_opened,
        "lp_visits": projected_lp_visits,
        "hero_bounces": projected_hero_bounces,
        "scrolled": projected_scrolled,
        "leads": projected_leads,
    }
    if projected_leads_range and len(projected_leads_range) == 2:
        projected["leads_range"] = projected_leads_range

    scale_projected = None
    if scale_sent and scale_leads is not None:
        scale_projected = {"sent": scale_sent, "leads": scale_leads}
        if scale_leads_range and len(scale_leads_range) == 2:
            scale_projected["leads_range"] = scale_leads_range

    visual_blocks = build_campaign_comparison_visuals(baseline, projected, scale_projected=scale_projected)

    open_b = _safe_rate(baseline_opened or 0, baseline_sent) if baseline_opened else None
    open_p = _safe_rate(projected_opened or 0, projected_sent or baseline_sent) if projected_opened else None
    ctr_b = _safe_rate(baseline_lp_visits or 0, baseline_sent) if baseline_lp_visits else None
    ctr_p = _safe_rate(projected_lp_visits or 0, projected_sent or baseline_sent) if projected_lp_visits else None

    return {
        "baseline": baseline,
        "projected": projected,
        "scale_projected": scale_projected,
        "visual_blocks": visual_blocks,
        "rates": {
            "baseline_open_rate": open_b,
            "projected_open_rate": open_p,
            "baseline_ctr": ctr_b,
            "projected_ctr": ctr_p,
        },
        "summary": (
            f"Comparação {baseline_name} vs {projected_name}: "
            f"abertura {open_b or '—'}% → {open_p or '—'}%, "
            f"CTR {ctr_b or '—'}% → {ctr_p or '—'}%."
        ),
    }


def parse_campaign_report(text: str) -> dict[str, Any]:
    """Extract numeric metrics from pasted report text."""
    numbers = [float(n.replace(",", ".")) for n in re.findall(r"(\d+[.,]?\d*)%", text)]
    ints = [int(n.replace(".", "").replace(",", "")) for n in re.findall(r"\b(\d{1,6})\b", text)]

    metrics: dict[str, Any] = {"raw_percentages": numbers[:10], "raw_integers": ints[:20]}

    open_match = re.search(r"abertura[^0-9]*(\d+[.,]?\d*)%?", text, re.I)
    ctr_match = re.search(r"ctr[^0-9]*(\d+[.,]?\d*)%?", text, re.I)
    leads_match = re.search(r"leads?\s+gerados?[^0-9]*(\d[\d.,]*)", text, re.I)
    waves_match = re.search(r"ondas?\s+de\s+email[^0-9]*(\d+)", text, re.I)
    lp_match = re.search(r"leads?\s+na\s+lp[^0-9]*(\d+)", text, re.I)

    if open_match:
        metrics["open_rate_pct"] = float(open_match.group(1).replace(",", "."))
    if ctr_match:
        metrics["ctr_pct"] = float(ctr_match.group(1).replace(",", "."))
    if leads_match:
        metrics["leads_generated"] = int(leads_match.group(1).replace(".", "").replace(",", ""))
    if waves_match:
        metrics["email_waves"] = int(waves_match.group(1))
    if lp_match:
        metrics["lp_leads"] = int(lp_match.group(1))

    client_match = re.search(r"\b(ebox|dochr)\b", text, re.I)
    if client_match:
        metrics["client_name"] = client_match.group(1).capitalize()

    sent = ints[0] if ints and ints[0] >= 100 else None
    if metrics.get("open_rate_pct") or metrics.get("ctr_pct") or sent:
        funnel = analyze_funnel(
            sent=sent,
            open_rate_pct=metrics.get("open_rate_pct"),
            ctr_pct=metrics.get("ctr_pct"),
            lp_visits=metrics.get("lp_leads"),
            client_name=metrics.get("client_name"),
            leads_generated=metrics.get("leads_generated"),
            email_waves=metrics.get("email_waves"),
        )
        metrics["funnel_analysis"] = funnel
        metrics["chart_stages"] = funnel.get("chart_stages", [])

    return metrics


def audit_email_copy(text: str, *, stage: str = "Atenção") -> dict[str, Any]:
    """Rule-based + structural email copy audit."""
    issues: list[str] = []
    strengths: list[str] = []
    score = 7

    lower = text.lower()
    if "?" in text and "assunto" not in lower[:20]:
        issues.append("CTA ou encerramento em forma de pergunta aberta — reduz cliques em B2B.")
        score -= 2

    if "saiba mais" in lower or "tudo bem?" in lower:
        issues.append("Frases genéricas ou de template detectadas.")
        score -= 1

    if any(client in text for client in ["Ambev", "Pirelli", "Hapvida", "GOL"]):
        strengths.append("Uso de prova social com cliente de referência.")

    if re.search(r"\d+%", text):
        strengths.append("Número concreto presente no corpo.")

    if len(text.split()) > 120:
        issues.append("Email longo demais para outbound B2B frio (ideal ~70-90 palavras).")
        score -= 1

    if "—" in text or "–" in text:
        issues.append("Travessão detectado — evitar conforme guidelines Belgos.")
        score -= 1

    score = max(1, min(10, score))

    return {
        "stage": stage,
        "score": score,
        "strengths": strengths or ["Tom consultivo detectado."],
        "issues": issues or ["Nenhum problema estrutural crítico detectado."],
        "recommendations": [
            "Encerrar direcionando para o botão, sem pedir resposta verbal.",
            "Criar tensão antes do CTA com consequência concreta de não agir.",
        ],
    }


def audit_landing_page(text: str) -> dict[str, Any]:
    """Audit LP content for B2B conversion patterns."""
    issues: list[str] = []
    strengths: list[str] = []
    score = 6
    lower = text.lower()

    if re.search(r"\bagora\b", lower) and text.isupper() is False:
        if text.upper() != text and "AGORA" in text:
            issues.append("Urgência em maiúsculas (AGORA) — tom de e-commerce, não B2B enterprise.")
            score -= 1

    if not any(word in lower for word in ["ambev", "pirelli", "gol", "hapvida", "depoimento", "logo"]):
        issues.append("Prova social fraca ou ausente — adicionar logos e depoimentos reais.")
        score -= 2

    if any(word in lower for word in ["cnpj", "telefone", "empresa"]) and "email" in lower:
        issues.append("Formulário com múltiplos campos — alto atrito para lead frio de outbound.")
        score -= 1

    if re.search(r"\d+%", text):
        strengths.append("Números concretos na página.")

    if "iso" in lower:
        strengths.append("Certificação ISO destacada.")

    score = max(1, min(10, score))

    return {
        "score": score,
        "strengths": strengths or ["Estrutura básica de LP presente."],
        "issues": issues,
        "priority_changes": [
            "Adicionar logo bar de clientes logo abaixo da headline.",
            "Subir headline com número concreto para o topo.",
            "Reduzir tom agressivo (maiúsculas, URGÊNCIA).",
        ],
    }


def rewrite_sequence(
    *,
    sequence_type: str,
    client_name: str,
    product: str,
) -> dict[str, Any]:
    """Return fixed email/WhatsApp templates for common reactivation sequences."""
    templates: dict[str, dict[str, str]] = {
        "reativacao_email_1": {
            "assunto": "Sobre o que você viu por aqui",
            "corpo": (
                f"Oi!\nVi que você passou pela {client_name} há algum tempo e queria retomar o contato.\n"
                f"Se o momento for agora, o botão abaixo leva direto para o próximo passo."
            ),
        },
        "reativacao_email_2": {
            "assunto": "Antes de fechar por aqui",
            "corpo": (
                f"Fica a dúvida se o que trava é implementação ou timing.\n"
                f"A {product} tem processo estruturado desde o início.\n"
                f"Se fizer sentido retomar, o botão abaixo ainda está lá."
            ),
        },
        "whatsapp": {
            "corpo": (
                f"Oi! Vi que você conheceu a {client_name} recentemente.\n"
                f"Se fizer sentido explorar para sua empresa, toque no botão abaixo."
            ),
            "botao": f"Ver como a {client_name} funciona",
        },
    }
    key = sequence_type.lower().replace(" ", "_")
    if key not in templates:
        return {
            "available": list(templates.keys()),
            "message": "Tipo de sequência não encontrado. Use reativacao_email_1, reativacao_email_2 ou whatsapp.",
        }
    return {"sequence_type": key, "template": templates[key]}


def generate_prompt_package(
    *,
    client_name: str,
    product: str,
    differentiators: list[str],
    constraints: list[str],
    funnel_stage: str = "Atenção",
) -> dict[str, str]:
    """Generate base + instruction prompt package for 1:1 email generator."""
    diff_text = "\n".join(f"- {item}" for item in differentiators)
    constraints_text = "\n".join(f"- {item}" for item in constraints)

    knowledge_base = f"""Você é um especialista em comunicação B2B que escreve e-mails de prospecção para {client_name}.

## O que é {product}
{product} atende empresas de médio e grande porte com foco em conversão outbound B2B.

## Diferenciais
{diff_text}

## Restrições
{constraints_text}
"""

    instruction = f"""Gere uma sequência de 3 e-mails de prospecção para o lead informado.

Estágio alvo: {funnel_stage}

REGRAS:
- 3 parágrafos curtos por email (~70 palavras, máx 90)
- Assunto dinâmico por setor/cargo no email 1
- Não fazer pergunta nos emails 1 e 2; direcionar para o botão
- Email 3: única pergunta permitida (mostrar entendimento da dor, não pedir resposta)
- Nunca incluir links no corpo
- Texto puro, sem HTML

FORMATO:
Assunto: (texto)
(corpo)
"""

    return {"knowledge_base": knowledge_base.strip(), "instruction": instruction.strip()}


MARKETING_TOOLS = [
    {
        "name": "analyze_funnel",
        "description": "Analyze email marketing funnel metrics and find bottleneck",
        "parameters": {
            "type": "object",
            "properties": {
                "sent": {"type": "integer"},
                "opened": {"type": "integer"},
                "clicked": {"type": "integer"},
                "lp_visits": {"type": "integer"},
                "form_fills": {"type": "integer"},
                "open_rate_pct": {"type": "number"},
                "ctr_pct": {"type": "number"},
                "client_name": {"type": "string"},
                "title": {"type": "string"},
                "leads_generated": {"type": "integer"},
                "email_waves": {"type": "integer"},
            },
        },
    },
    {
        "name": "audit_email_copy",
        "description": "Audit email copy for B2B outbound best practices",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "stage": {"type": "string"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "audit_landing_page",
        "description": "Audit landing page copy for conversion issues",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "rewrite_sequence",
        "description": "Get fixed email or WhatsApp templates for reactivation sequences",
        "parameters": {
            "type": "object",
            "properties": {
                "sequence_type": {"type": "string"},
                "client_name": {"type": "string"},
                "product": {"type": "string"},
            },
            "required": ["sequence_type", "client_name"],
        },
    },
    {
        "name": "generate_prompt_package",
        "description": "Generate knowledge base + instruction prompts for 1:1 email generator",
        "parameters": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string"},
                "product": {"type": "string"},
                "differentiators": {"type": "array", "items": {"type": "string"}},
                "constraints": {"type": "array", "items": {"type": "string"}},
                "funnel_stage": {"type": "string"},
            },
            "required": ["client_name", "product"],
        },
    },
    {
        "name": "compare_campaign_scenarios",
        "description": (
            "Compare baseline vs optimized campaign metrics and generate comparative chart blocks "
            "(funnel_compare, bar_compare, projection) for the report UI"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "baseline_name": {"type": "string"},
                "projected_name": {"type": "string"},
                "baseline_sent": {"type": "integer"},
                "baseline_opened": {"type": "integer"},
                "baseline_lp_visits": {"type": "integer"},
                "baseline_hero_bounces": {"type": "integer"},
                "baseline_scrolled": {"type": "integer"},
                "baseline_leads": {"type": "number"},
                "projected_sent": {"type": "integer"},
                "projected_opened": {"type": "integer"},
                "projected_lp_visits": {"type": "integer"},
                "projected_hero_bounces": {"type": "integer"},
                "projected_scrolled": {"type": "integer"},
                "projected_leads": {"type": "number"},
                "projected_leads_range": {"type": "array", "items": {"type": "number"}},
                "scale_sent": {"type": "integer"},
                "scale_leads": {"type": "number"},
                "scale_leads_range": {"type": "array", "items": {"type": "number"}},
            },
            "required": ["baseline_sent"],
        },
    },
    {
        "name": "parse_campaign_report",
        "description": "Parse pasted campaign report text and extract metrics",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]


def execute_marketing_tool(name: str, arguments: dict[str, Any], client_context: dict[str, Any] | None = None) -> Any:
    client_context = client_context or {}

    if name == "analyze_funnel":
        return analyze_funnel(**arguments)

    if name == "compare_campaign_scenarios":
        return compare_campaign_scenarios(**arguments)

    if name == "audit_email_copy":
        return audit_email_copy(**arguments)

    if name == "audit_landing_page":
        return audit_landing_page(**arguments)

    if name == "parse_campaign_report":
        return parse_campaign_report(arguments.get("text", ""))

    if name == "rewrite_sequence":
        args = dict(arguments)
        if not args.get("product") and client_context.get("product"):
            args["product"] = client_context["product"]
        if not args.get("client_name") and client_context.get("name"):
            args["client_name"] = client_context["name"]
        return rewrite_sequence(**args)

    if name == "generate_prompt_package":
        args = dict(arguments)
        if not args.get("differentiators") and client_context.get("differentiators"):
            args["differentiators"] = client_context["differentiators"]
        if not args.get("constraints") and client_context.get("constraints"):
            args["constraints"] = client_context["constraints"]
        if not args.get("client_name") and client_context.get("name"):
            args["client_name"] = client_context["name"]
        if not args.get("product") and client_context.get("product"):
            args["product"] = client_context["product"]
        return generate_prompt_package(**args)

    return {"error": f"Unknown tool: {name}"}


def format_tool_result(name: str, result: Any) -> str:
    return f"### {name}\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
