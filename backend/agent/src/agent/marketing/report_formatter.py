"""Build visual markdown blocks (charts, KPIs, tables) for funnel diagnostics."""

from __future__ import annotations

import json
import re
from typing import Any


def build_chart_stages(
    *,
    sent: int | None = None,
    opened: int | None = None,
    clicked: int | None = None,
    lp_visits: int | None = None,
    form_fills: int | None = None,
    open_rate_pct: float | None = None,
    ctr_pct: float | None = None,
) -> list[dict[str, Any]]:
    """Build funnel stage data for chart rendering."""
    stages: list[dict[str, Any]] = []

    if sent is not None and sent > 0:
        stages.append({"label": "Enviados", "pct": 100.0, "absolute": sent})
        if opened is not None:
            pct = round((opened / sent) * 100, 2)
            stages.append({"label": "Abriram", "pct": pct, "absolute": opened})
        elif open_rate_pct is not None:
            abs_opened = round(sent * open_rate_pct / 100)
            stages.append({"label": "Abriram", "pct": open_rate_pct, "absolute": abs_opened})
            opened = abs_opened
    elif open_rate_pct is not None:
        stages.append({"label": "Enviados", "pct": 100.0, "absolute": sent})
        stages.append({"label": "Abriram", "pct": open_rate_pct, "absolute": opened})

    open_base = opened
    if open_base is None and open_rate_pct is not None and sent:
        open_base = round(sent * open_rate_pct / 100)

    if clicked is not None and open_base and open_base > 0:
        pct = round((clicked / open_base) * 100, 2)
        stages.append({"label": "Clicaram", "pct": pct, "absolute": clicked})
    elif ctr_pct is not None:
        abs_clicked = clicked
        if abs_clicked is None and open_base:
            abs_clicked = max(1, round(open_base * ctr_pct / 100)) if ctr_pct > 0 else 0
        stages.append({"label": "Clicaram", "pct": ctr_pct, "absolute": abs_clicked})
        clicked = abs_clicked

    if lp_visits is not None and clicked and clicked > 0:
        pct = round((lp_visits / clicked) * 100, 2)
        stages.append({"label": "LP (visitas)", "pct": pct, "absolute": lp_visits})
    elif lp_visits is not None:
        stages.append({"label": "LP (visitas)", "pct": 0.0, "absolute": lp_visits})

    if form_fills is not None:
        if lp_visits and lp_visits > 0:
            pct = round((form_fills / lp_visits) * 100, 2)
        else:
            pct = 0.0
        stages.append({"label": "Converteu (form)", "pct": pct, "absolute": form_fills})

    return stages


def build_funnel_chart_block(
    stages: list[dict[str, Any]],
    *,
    title: str = "Onde o funil quebra",
) -> str:
    if not stages:
        return ""
    payload = {"type": "funnel", "title": title, "stages": stages}
    return f"```chart\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"


def build_funnel_compare_block(
    series: list[dict[str, Any]],
    *,
    title: str = "Funil de Conversão Comparativo",
) -> str:
    if len(series) < 2:
        return ""
    payload = {"type": "funnel_compare", "title": title, "series": series}
    return f"```chart\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"


def build_bar_compare_block(
    metrics: list[dict[str, Any]],
    *,
    title: str = "Comparativo de Taxas (%)",
    y_axis_label: str = "%",
) -> str:
    if not metrics:
        return ""
    payload = {"type": "bar_compare", "title": title, "yAxisLabel": y_axis_label, "metrics": metrics}
    return f"```chart\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"


def build_projection_block(
    scenarios: list[dict[str, Any]],
    *,
    title: str = "Projeção de Geração de Leads",
    unit: str = "leads",
) -> str:
    if not scenarios:
        return ""
    payload = {"type": "projection", "title": title, "unit": unit, "scenarios": scenarios}
    return f"```chart\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"


def _safe_pct(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round((float(numerator) / float(denominator)) * 100, 2)


def _improvement_note(baseline: float | None, projected: float | None) -> str | None:
    if baseline is None or projected is None or baseline <= 0:
        return None
    delta = round(((projected - baseline) / baseline) * 100)
    if delta > 0:
        return f"Melhoria de +{delta}%"
    if delta < 0:
        return f"Queda de {delta}%"
    return None


def build_detailed_funnel_stages(
    *,
    sent: int,
    opened: int | None = None,
    lp_visits: int | None = None,
    hero_bounces: int | None = None,
    scrolled: int | None = None,
    leads: float | int | None = None,
    highlight_bottlenecks: bool = False,
    highlight_successes: bool = False,
) -> list[dict[str, Any]]:
    """Build detailed campaign funnel stages (% relative to sent for bar width)."""
    stages: list[dict[str, Any]] = [{"label": "Disparos", "pct": 100.0, "absolute": sent}]

    if opened is not None:
        open_pct = _safe_pct(opened, sent) or 0.0
        stage: dict[str, Any] = {"label": "Lidos", "pct": open_pct, "absolute": opened}
        stages.append(stage)

    if lp_visits is not None:
        lp_pct = _safe_pct(lp_visits, sent) or 0.0
        stage = {"label": "Visitas na LP", "pct": lp_pct, "absolute": lp_visits}
        if highlight_successes and lp_pct > 5:
            stage["highlight"] = "success"
        stages.append(stage)

    if hero_bounces is not None and lp_visits:
        bounce_pct = _safe_pct(hero_bounces, lp_visits) or 0.0
        stage = {
            "label": "Abandonaram no Hero",
            "pct": _safe_pct(hero_bounces, sent) or 0.0,
            "absolute": hero_bounces,
        }
        if highlight_bottlenecks and bounce_pct >= 50:
            stage["highlight"] = "bottleneck"
        elif highlight_successes and bounce_pct < 50:
            stage["highlight"] = "neutral"
        stages.append(stage)

    if scrolled is not None:
        scroll_pct = _safe_pct(scrolled, sent) or 0.0
        stage = {"label": "Rolaram a LP", "pct": scroll_pct, "absolute": scrolled}
        if highlight_bottlenecks and lp_visits and scrolled / lp_visits < 0.35:
            stage["highlight"] = "bottleneck"
        if highlight_successes and lp_visits and scrolled / lp_visits >= 0.5:
            stage["highlight"] = "success"
        stages.append(stage)

    if leads is not None:
        lead_abs = round(float(leads), 1) if isinstance(leads, float) else leads
        lead_pct = _safe_pct(leads, lp_visits) if lp_visits else _safe_pct(leads, sent)
        stage = {"label": "Leads Gerados", "pct": lead_pct or 0.0, "absolute": lead_abs}
        if highlight_bottlenecks and (leads == 0 or leads == 0.0):
            stage["highlight"] = "bottleneck"
        elif highlight_successes and leads and float(leads) > 0:
            stage["highlight"] = "success"
        stages.append(stage)

    return stages


def build_bar_compare_metrics(
    baseline_name: str,
    projected_name: str,
    *,
    sent: int,
    baseline_opened: int | None = None,
    baseline_lp_visits: int | None = None,
    baseline_scrolled: int | None = None,
    baseline_leads: float | int | None = None,
    projected_opened: int | None = None,
    projected_lp_visits: int | None = None,
    projected_scrolled: int | None = None,
    projected_leads: float | int | None = None,
) -> list[dict[str, Any]]:
    """Build grouped bar metrics comparing baseline vs projected campaigns."""
    metrics: list[dict[str, Any]] = []

    def _metric(label: str, b_num: float | int | None, b_den: float | int, p_num: float | int | None, p_den: float | int) -> None:
        b_val = _safe_pct(b_num, b_den)
        p_val = _safe_pct(p_num, p_den)
        if b_val is None and p_val is None:
            return
        note = _improvement_note(b_val, p_val)
        metrics.append(
            {
                "label": label,
                "series": [
                    {"name": baseline_name, "value": b_val or 0.0},
                    {"name": projected_name, "value": p_val or 0.0, **({"note": note} if note else {})},
                ],
            }
        )

    _metric("Taxa de Abertura", baseline_opened, sent, projected_opened, sent)
    _metric("Taxa de Cliques/CTR", baseline_lp_visits, sent, projected_lp_visits, sent)
    if baseline_lp_visits and projected_lp_visits:
        _metric(
            "Taxa de Rolagem na LP",
            baseline_scrolled,
            baseline_lp_visits,
            projected_scrolled,
            projected_lp_visits,
        )
        _metric(
            "Taxa de Conversão Final",
            baseline_leads,
            baseline_lp_visits,
            projected_leads,
            projected_lp_visits,
        )

    return metrics


def build_campaign_comparison_visuals(
    baseline: dict[str, Any],
    projected: dict[str, Any],
    *,
    scale_projected: dict[str, Any] | None = None,
) -> list[str]:
    """Build funnel_compare, bar_compare, and projection chart blocks from campaign dicts."""
    blocks: list[str] = []

    baseline_name = str(baseline.get("name", "Campanha baseline"))
    projected_name = str(projected.get("name", "Campanha projetada"))
    sent = int(baseline.get("sent") or projected.get("sent") or 0)
    if sent <= 0:
        return blocks

    proj_sent = int(projected.get("sent") or sent)

    baseline_stages = build_detailed_funnel_stages(
        sent=sent,
        opened=baseline.get("opened"),
        lp_visits=baseline.get("lp_visits"),
        hero_bounces=baseline.get("hero_bounces"),
        scrolled=baseline.get("scrolled"),
        leads=baseline.get("leads"),
        highlight_bottlenecks=True,
    )
    projected_stages = build_detailed_funnel_stages(
        sent=proj_sent,
        opened=projected.get("opened"),
        lp_visits=projected.get("lp_visits"),
        hero_bounces=projected.get("hero_bounces"),
        scrolled=projected.get("scrolled"),
        leads=projected.get("leads"),
        highlight_successes=True,
    )

    funnel_block = build_funnel_compare_block(
        [
            {"name": baseline_name, "stages": baseline_stages},
            {"name": projected_name, "stages": projected_stages},
        ]
    )
    if funnel_block:
        blocks.append(funnel_block)

    bar_metrics = build_bar_compare_metrics(
        baseline_name,
        projected_name,
        sent=sent,
        baseline_opened=baseline.get("opened"),
        baseline_lp_visits=baseline.get("lp_visits"),
        baseline_scrolled=baseline.get("scrolled"),
        baseline_leads=baseline.get("leads"),
        projected_opened=projected.get("opened"),
        projected_lp_visits=projected.get("lp_visits"),
        projected_scrolled=projected.get("scrolled"),
        projected_leads=projected.get("leads"),
    )
    bar_block = build_bar_compare_block(bar_metrics)
    if bar_block:
        blocks.append(bar_block)

    scenarios: list[dict[str, Any]] = [
        {
            "label": f"{baseline_name} ({sent} envios)",
            "value": float(baseline.get("leads") or 0),
        },
        {
            "label": f"{projected_name} ({proj_sent} envios)",
            "value": float(projected.get("leads") or 0),
        },
    ]
    if projected.get("leads_range"):
        lo, hi = projected["leads_range"]
        scenarios[-1]["range"] = [lo, hi]

    if scale_projected:
        scale_sent = int(scale_projected.get("sent", 1000))
        scale_leads = float(scale_projected.get("leads", 0))
        scenario: dict[str, Any] = {
            "label": f"{projected_name} (escala de {scale_sent:,} envios)".replace(",", "."),
            "value": scale_leads,
        }
        if scale_projected.get("leads_range"):
            scenario["range"] = scale_projected["leads_range"]
        scenarios.append(scenario)

    projection_block = build_projection_block(scenarios)
    if projection_block:
        blocks.append(projection_block)

    return blocks


def build_kpi_strip_block(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    payload = {"type": "kpi", "items": items}
    return f"```kpi\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"


def build_comparison_table_block(clients: list[dict[str, Any]]) -> str:
    if len(clients) < 2:
        return ""

    headers = [
        "Métrica",
        *[str(c.get("client_name", f"Cliente {i + 1}")) for i, c in enumerate(clients)],
    ]
    rows = [
        ("Leads gerados", "leads_generated"),
        ("Ondas de email", "email_waves"),
        ("Abertura média", "open_rate"),
        ("CTR médio", "ctr"),
        ("Leads na LP", "lp_leads"),
        ("Qualificados", "qualified"),
        ("Agendamentos", "scheduled"),
        ("Vendas", "sales"),
    ]

    lines = [
        "## Funil comparado",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for label, key in rows:
        cells = [label]
        for client in clients:
            value = client.get(key)
            if value is None:
                cells.append("—")
            elif key in ("open_rate", "ctr") and isinstance(value, (int, float)):
                cells.append(f"{value}%")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _format_pct(value: float | None, suffix: str = "%") -> str:
    if value is None:
        return "—"
    return f"{value:g}{suffix}"


def _funnel_snapshot(result: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize analyze_funnel or nested funnel_analysis into a snapshot."""
    if "rates" in result or "chart_stages" in result:
        return result
    nested = result.get("funnel_analysis")
    if isinstance(nested, dict):
        return {**nested, **{k: v for k, v in result.items() if k != "funnel_analysis"}}
    return None


def extract_metrics_from_tool_results(tool_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate funnel metrics from marketing tool execution results."""
    snapshots: list[dict[str, Any]] = []
    kpi_items: list[dict[str, str]] = []
    total_leads = 0
    open_rates: list[float] = []
    ctr_rates: list[float] = []

    for entry in tool_results:
        tool_name = entry.get("tool", "")
        result = entry.get("result")
        if not isinstance(result, dict):
            continue

        if tool_name == "analyze_funnel":
            snapshots.append(result)
        elif tool_name == "compare_campaign_scenarios":
            snapshots.append(result)
        elif tool_name == "parse_campaign_report":
            snap = _funnel_snapshot(result)
            if snap:
                merged = {**snap}
                if result.get("leads_generated"):
                    merged["leads_generated"] = result["leads_generated"]
                if result.get("email_waves"):
                    merged["email_waves"] = result["email_waves"]
                if result.get("lp_leads") is not None:
                    merged["lp_leads"] = result["lp_leads"]
                snapshots.append(merged)

        if tool_name in ("analyze_funnel", "parse_campaign_report"):
            leads = result.get("leads_generated")
            if isinstance(leads, int):
                total_leads += leads
            rates = result.get("rates") or (result.get("funnel_analysis") or {}).get("rates") or {}
            if rates.get("open_rate") is not None:
                open_rates.append(float(rates["open_rate"]))
            if rates.get("ctr") is not None:
                ctr_rates.append(float(rates["ctr"]))
            if result.get("open_rate_pct") is not None:
                open_rates.append(float(result["open_rate_pct"]))
            if result.get("ctr_pct") is not None:
                ctr_rates.append(float(result["ctr_pct"]))

    if total_leads > 0:
        kpi_items.append({"label": "Leads gerados", "value": f"{total_leads:,}".replace(",", ".")})
    if open_rates:
        avg_open = round(sum(open_rates) / len(open_rates), 1)
        kpi_items.append({"label": "Abertura média", "value": _format_pct(avg_open)})
    if ctr_rates:
        avg_ctr = round(sum(ctr_rates) / len(ctr_rates), 2)
        kpi_items.append({"label": "CTR médio", "value": _format_pct(avg_ctr)})

    lp_values = [s.get("lp_leads") for s in snapshots if s.get("lp_leads") is not None]
    if lp_values:
        kpi_items.append({"label": "Leads na LP", "value": str(sum(lp_values))})

    return {"snapshots": snapshots, "kpi_items": kpi_items}


def build_visual_preamble(tool_results: list[dict[str, Any]]) -> str:
    """Build KPI strip, funnel chart(s), and comparison table from tool results."""
    if not tool_results:
        return ""

    sections: list[str] = ["## Visão consolidada — métricas"]

    for entry in tool_results:
        result = entry.get("result")
        if entry.get("tool") == "compare_campaign_scenarios" and isinstance(result, dict):
            visual_blocks = result.get("visual_blocks") or []
            for block in visual_blocks:
                if isinstance(block, str) and block.strip():
                    sections.append(block.strip())
            if len(sections) > 1:
                return "\n\n".join(sections)

    aggregated = extract_metrics_from_tool_results(tool_results)
    snapshots: list[dict[str, Any]] = aggregated["snapshots"]
    if not snapshots:
        return ""

    kpi_block = build_kpi_strip_block(aggregated["kpi_items"])
    if kpi_block:
        sections.append(kpi_block)

    client_rows: list[dict[str, Any]] = []
    funnel_series: list[dict[str, Any]] = []
    for snap in snapshots:
        rates = snap.get("rates") or {}
        row: dict[str, Any] = {
            "client_name": snap.get("client_name") or snap.get("name") or "Cliente",
            "leads_generated": snap.get("leads_generated"),
            "email_waves": snap.get("email_waves"),
            "open_rate": rates.get("open_rate") or snap.get("open_rate_pct"),
            "ctr": rates.get("ctr") or snap.get("ctr_pct"),
            "lp_leads": snap.get("lp_leads"),
            "qualified": snap.get("qualified"),
            "scheduled": snap.get("scheduled"),
            "sales": snap.get("sales"),
        }
        if any(v is not None for k, v in row.items() if k != "client_name"):
            client_rows.append(row)

        stages = snap.get("chart_stages") or snap.get("funnel_stages") or []
        if stages:
            name = snap.get("client_name") or snap.get("name") or snap.get("chart_title") or "Campanha"
            funnel_series.append({"name": str(name), "stages": stages})

    if len(funnel_series) >= 2:
        compare_block = build_funnel_compare_block(funnel_series)
        if compare_block:
            sections.append(compare_block)

    comparison = build_comparison_table_block(client_rows)
    if comparison and len(funnel_series) < 2:
        sections.append(comparison)

    if len(funnel_series) < 2:
        for snap in snapshots:
            stages = snap.get("chart_stages") or []
            if not stages:
                continue
            title = snap.get("chart_title") or "Onde o funil quebra"
            if snap.get("client_name"):
                title = f"{title} ({snap['client_name']})"
            chart = build_funnel_chart_block(stages, title=title)
            if chart:
                sections.append(chart)
    elif len(client_rows) >= 2:
        comparison = build_comparison_table_block(client_rows)
        if comparison:
            sections.append(comparison)

    projections = []
    for snap in snapshots:
        if snap.get("projections"):
            projections.extend(snap["projections"])
    if projections:
        proj_block = build_projection_block(projections)
        if proj_block:
            sections.append(proj_block)

    if len(sections) <= 1:
        return ""

    return "\n\n".join(sections)


def merge_deliverable_with_visuals(deliverable: str | None, tool_results: list[dict[str, Any]]) -> str:
    """Prefix deliverable with auto-generated visual blocks when metrics exist."""
    visual = build_visual_preamble(tool_results).strip()
    narrative = (deliverable or "").strip()
    if not visual:
        return narrative
    if not narrative:
        return visual
    return f"{visual}\n\n---\n\n{narrative}"
