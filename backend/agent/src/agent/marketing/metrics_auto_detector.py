"""Automatically detect marketing metrics in conversation context and run tools."""

from __future__ import annotations

import re
from typing import Any

from agent.graph.state import AgentState
from agent.tools.marketing_tools import analyze_funnel, compare_campaign_scenarios, parse_campaign_report

_CAMPAIGN_LABEL = re.compile(
    r"(?:campanha|camp\.?)\s*(?P<num>\d+|[A-Za-z]+)|"
    r"(?P<role>baseline|hist[oó]ric[oa]|projetad[oa]|otimizad[oa])",
    re.I,
)
_SENT = re.compile(r"(?P<n>\d{1,6})\s*(?:envios|disparos)", re.I)
_OPENED = re.compile(r"(?P<n>\d{1,6})\s*(?:lidos|aberturas?)", re.I)
_LP_VISITS = re.compile(r"(?P<n>\d{1,6})\s*(?:visitas?\s+(?:na\s+)?lp|cliques)", re.I)
_HERO_BOUNCE = re.compile(r"(?P<n>\d{1,6})\s*(?:abandonaram|abandonos?).*?(?:hero|topo)", re.I)
_SCROLLED = re.compile(r"(?P<n>\d{1,6})\s*(?:rolaram|rolagem)", re.I)
_LEADS = re.compile(r"(?P<n>[\d.,]+)\s*(?:leads?\s+gerados?|convers(?:ões|oes))", re.I)
_OPEN_RATE = re.compile(r"(?:abertura|taxa de abertura)[^0-9]*(?P<pct>\d+[.,]?\d*)\s*%", re.I)
_CTR = re.compile(r"(?:ctr|taxa de cliques?)[^0-9]*(?P<pct>\d+[.,]?\d*)\s*%", re.I)
_SCALE = re.compile(
    r"(?:(?:escala|proje(?:ç|c)[ãa]o).*?(?P<scale_sent>1[\d.,]*000|mil)\s*envios|"
    r"(?P<scale_sent2>1[\d.,]*000|mil)\s*envios.*?leads?)",
    re.I,
)
_SCALE_LEADS = re.compile(
    r"(?:m[eé]dia de|proje(?:ç|c)[ãa]o de|gerar(?:ia)?)\s*(?P<n>[\d.,]+)\s*(?:leads?|oportunidades?)",
    re.I,
)
_COMPARE_HINT = re.compile(
    r"(?:campanha|camp\.?)\s*\d+.*?(?:vs\.?|versus|x|contra).*?(?:campanha|camp\.?)\s*\d+|"
    r"baseline.*?projetad|hist[oó]ric.*?projetad|campanha\s*\d+.*?campanha\s*\d+",
    re.I,
)


def _parse_int(value: str | None) -> int | None:
    if not value:
        return None
    cleaned = value.replace(".", "").replace(",", "")
    try:
        return int(cleaned)
    except ValueError:
        return None


def _parse_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def collect_marketing_context(state: AgentState) -> str:
    """Concatenate messages, attachments, and client context for metric detection."""
    parts: list[str] = []
    for msg in state.get("messages", []):
        content = getattr(msg, "content", None)
        if isinstance(content, str) and content.strip():
            parts.append(content)
    for attachment in state.get("attachments", []):
        text = attachment.get("extracted_text", "")
        if text.strip():
            filename = attachment.get("filename", "anexo")
            parts.append(f"\n### {filename}\n{text}")
    client_context = state.get("client_context", "")
    if client_context.strip():
        parts.append(client_context)
    return "\n\n".join(parts)


def _split_campaign_sections(text: str) -> list[tuple[str, str]]:
    """Split text into named campaign sections."""
    markers = list(_CAMPAIGN_LABEL.finditer(text))
    if len(markers) < 2:
        return []

    sections: list[tuple[str, str]] = []
    for index, match in enumerate(markers):
        start = match.start()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        label = match.group(0).strip()
        if match.group("num"):
            label = f"Campanha {match.group('num')}"
        elif match.group("role"):
            role = match.group("role").lower()
            if "hist" in role or role == "baseline":
                label = "Campanha baseline (Histórico)"
            else:
                label = "Campanha projetada (Otimizada)"
        sections.append((label, text[start:end]))
    return sections


def _extract_campaign_metrics(block: str) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    sent = _SENT.search(block)
    if sent:
        metrics["sent"] = _parse_int(sent.group("n"))

    opened = _OPENED.search(block)
    if opened:
        metrics["opened"] = _parse_int(opened.group("n"))

    lp = _LP_VISITS.search(block)
    if lp:
        metrics["lp_visits"] = _parse_int(lp.group("n"))

    bounce = _HERO_BOUNCE.search(block)
    if bounce:
        metrics["hero_bounces"] = _parse_int(bounce.group("n"))

    scrolled = _SCROLLED.search(block)
    if scrolled:
        metrics["scrolled"] = _parse_int(scrolled.group("n"))

    leads = _LEADS.search(block)
    if leads:
        metrics["leads"] = _parse_float(leads.group("n"))

    open_rate = _OPEN_RATE.search(block)
    if open_rate and metrics.get("sent") and not metrics.get("opened"):
        pct = _parse_float(open_rate.group("pct"))
        if pct is not None:
            metrics["opened"] = round(metrics["sent"] * pct / 100)

    ctr = _CTR.search(block)
    if ctr and metrics.get("sent") and not metrics.get("lp_visits"):
        pct = _parse_float(ctr.group("pct"))
        if pct is not None:
            metrics["lp_visits"] = max(0, round(metrics["sent"] * pct / 100))

    return metrics


def _extract_scale_projection(text: str) -> dict[str, Any] | None:
    scale_match = _SCALE.search(text)
    scale_sent_raw = None
    if scale_match:
        scale_sent_raw = scale_match.group("scale_sent") or scale_match.group("scale_sent2")
    if not scale_sent_raw:
        thousand = re.search(r"1[\d.,]*000\s*envios", text, re.I)
        if thousand:
            scale_sent_raw = thousand.group(0)

    if not scale_sent_raw:
        return None

    scale_sent = 1000 if "mil" in scale_sent_raw.lower() else _parse_int(re.sub(r"\D", "", scale_sent_raw))
    if not scale_sent:
        return None

    leads_match = _SCALE_LEADS.search(text)
    scale_leads = _parse_float(leads_match.group("n")) if leads_match else None
    if scale_leads is None:
        plain = re.search(rf"{scale_sent}[^0-9]{{0,40}}(?P<n>[\d.,]+)\s*leads?", text, re.I)
        if plain:
            scale_leads = _parse_float(plain.group("n"))

    if scale_leads is None:
        return None

    return {"sent": scale_sent, "leads": scale_leads}


def _extract_campaigns_by_number(text: str) -> list[tuple[str, dict[str, Any]]]:
    """Extract metrics per campaign number from text blocks."""
    pattern = re.compile(
        r"(?:campanha|camp\.?)\s*(?P<num>\d+)[^\n]*\n(.*?)(?=(?:campanha|camp\.?)\s*\d+|\Z)",
        re.I | re.S,
    )
    by_num: dict[str, tuple[str, dict[str, Any]]] = {}
    for match in pattern.finditer(text):
        num = match.group("num")
        block = match.group(0)
        metrics = _extract_campaign_metrics(block)
        if metrics.get("sent") or metrics.get("opened") or metrics.get("lp_visits"):
            by_num[num] = (f"Campanha {num}", metrics)
    return [by_num[num] for num in sorted(by_num.keys(), key=int)]


def _try_compare_campaigns(text: str) -> dict[str, Any] | None:
    campaigns = _extract_campaigns_by_number(text)
    if len(campaigns) < 2 and _COMPARE_HINT.search(text):
        nums = sorted(set(re.findall(r"(?:campanha|camp\.?)\s*(\d+)", text, re.I)), key=int)
        if len(nums) >= 2:
            campaigns = [(f"Campanha {nums[0]}", _extract_campaign_metrics(text)), (f"Campanha {nums[1]}", _extract_campaign_metrics(text))]

    if len(campaigns) < 2:
        sections = _split_campaign_sections(text)
        if len(sections) >= 2:
            campaigns = [(sections[0][0], _extract_campaign_metrics(sections[0][1])), (sections[1][0], _extract_campaign_metrics(sections[1][1]))]

    if len(campaigns) < 2:
        return None

    (baseline_name, baseline_metrics), (projected_name, projected_metrics) = campaigns[0], campaigns[1]
    baseline_sent = baseline_metrics.get("sent")
    if not baseline_sent:
        return None

    scale = _extract_scale_projection(text)
    kwargs: dict[str, Any] = {
        "baseline_name": baseline_name,
        "projected_name": projected_name,
        "baseline_sent": baseline_sent,
        "baseline_opened": baseline_metrics.get("opened"),
        "baseline_lp_visits": baseline_metrics.get("lp_visits"),
        "baseline_hero_bounces": baseline_metrics.get("hero_bounces"),
        "baseline_scrolled": baseline_metrics.get("scrolled"),
        "baseline_leads": baseline_metrics.get("leads"),
        "projected_sent": projected_metrics.get("sent") or baseline_sent,
        "projected_opened": projected_metrics.get("opened"),
        "projected_lp_visits": projected_metrics.get("lp_visits"),
        "projected_hero_bounces": projected_metrics.get("hero_bounces"),
        "projected_scrolled": projected_metrics.get("scrolled"),
        "projected_leads": projected_metrics.get("leads"),
    }
    if scale:
        kwargs["scale_sent"] = scale["sent"]
        kwargs["scale_leads"] = scale["leads"]

    if not any(
        kwargs.get(key) is not None
        for key in (
            "baseline_opened",
            "baseline_lp_visits",
            "projected_opened",
            "projected_lp_visits",
        )
    ):
        return None

    return compare_campaign_scenarios(**kwargs)


def _try_single_funnel(text: str) -> dict[str, Any] | None:
    sent_match = _SENT.search(text)
    if not sent_match:
        return None

    sent = _parse_int(sent_match.group("n"))
    if not sent:
        return None

    metrics = _extract_campaign_metrics(text)
    opened = metrics.get("opened")
    lp_visits = metrics.get("lp_visits")
    leads = metrics.get("leads")

    open_rate = _OPEN_RATE.search(text)
    ctr = _CTR.search(text)

    if not any([opened, lp_visits, leads, open_rate, ctr]):
        return None

    return analyze_funnel(
        sent=sent,
        opened=opened,
        clicked=lp_visits,
        lp_visits=lp_visits,
        form_fills=int(leads) if leads is not None and leads == int(leads) else None,
        open_rate_pct=_parse_float(open_rate.group("pct")) if open_rate else None,
        ctr_pct=_parse_float(ctr.group("pct")) if ctr else None,
        leads_generated=int(leads) if leads is not None and leads == int(leads) else None,
    )


def auto_detect_marketing_tool_results(text: str) -> list[dict[str, Any]]:
    """Detect metrics in text and return synthetic marketing_tool_results entries."""
    if not text.strip():
        return []

    results: list[dict[str, Any]] = []

    comparison = _try_compare_campaigns(text)
    if comparison and comparison.get("visual_blocks"):
        results.append({"tool": "compare_campaign_scenarios", "result": comparison, "source": "auto"})
        return results

    parsed = parse_campaign_report(text)
    if parsed.get("chart_stages") or parsed.get("funnel_analysis"):
        results.append({"tool": "parse_campaign_report", "result": parsed, "source": "auto"})
        return results

    funnel = _try_single_funnel(text)
    if funnel and funnel.get("chart_stages"):
        results.append({"tool": "analyze_funnel", "result": funnel, "source": "auto"})

    return results


def context_has_marketing_metrics(text: str) -> bool:
    """Lightweight check whether text likely contains funnel/campaign metrics."""
    if not text.strip():
        return False
    if _COMPARE_HINT.search(text):
        return True
    if _SENT.search(text) and (_OPENED.search(text) or _OPEN_RATE.search(text) or _CTR.search(text)):
        return True
    if _SENT.search(text) and (_LP_VISITS.search(text) or _LEADS.search(text)):
        return True
    return bool(auto_detect_marketing_tool_results(text))


def _tool_names(results: list[dict[str, Any]]) -> set[str]:
    return {str(item.get("tool", "")) for item in results}


def merge_tool_results(manual: list[dict[str, Any]], auto: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge manual tool results with auto-detected ones; manual takes priority."""
    if not manual:
        return list(auto)
    if not auto:
        return list(manual)

    merged = list(manual)
    manual_tools = _tool_names(manual)

    for item in auto:
        tool = item.get("tool")
        if tool == "compare_campaign_scenarios" and "compare_campaign_scenarios" not in manual_tools:
            if "analyze_funnel" not in manual_tools:
                merged.append(item)
        elif tool == "analyze_funnel" and "analyze_funnel" not in manual_tools and "compare_campaign_scenarios" not in manual_tools:
            merged.append(item)
        elif tool == "parse_campaign_report" and not manual_tools & {
            "parse_campaign_report",
            "analyze_funnel",
            "compare_campaign_scenarios",
        }:
            merged.append(item)

    return merged
