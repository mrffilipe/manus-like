"""Per-client configuration adapter (DB-backed)."""

from dataclasses import dataclass, field
from typing import Any

from agent.persistence.models import MarketingClient


@dataclass
class ClientConfig:
    id: str
    name: str
    product: str
    description: str = ""
    icp: dict[str, Any] = field(default_factory=dict)
    funnel_stages: list[str] = field(default_factory=list)
    key_metrics: list[str] = field(default_factory=list)
    reference_clients_by_sector: dict[str, list[str]] = field(default_factory=dict)
    reference_clients: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    urls: dict[str, str] = field(default_factory=dict)
    benchmarks: dict[str, str] = field(default_factory=dict)
    cases: list[dict[str, str]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_context_text(self) -> str:
        lines = [
            f"Cliente: {self.name} ({self.product})",
            self.description.strip(),
            "",
            "ICP:",
        ]
        for role in self.icp.get("roles", []):
            lines.append(f"- {role}")
        if self.icp.get("company_profile"):
            lines.append(f"Perfil: {self.icp['company_profile']}")

        if self.funnel_stages:
            lines.append("")
            lines.append(f"Estágios do funil: {', '.join(self.funnel_stages)}")

        if self.key_metrics:
            lines.append("")
            lines.append("Métricas-chave a coletar:")
            for metric in self.key_metrics:
                lines.append(f"- {metric}")

        if self.differentiators:
            lines.append("")
            lines.append("Diferenciais:")
            for item in self.differentiators:
                lines.append(f"- {item}")

        if self.constraints:
            lines.append("")
            lines.append("Restrições operacionais:")
            for item in self.constraints:
                lines.append(f"- {item}")

        if self.urls:
            lines.append("")
            lines.append("URLs:")
            for key, url in self.urls.items():
                lines.append(f"- {key}: {url}")

        if self.benchmarks:
            lines.append("")
            lines.append("Benchmarks:")
            for key, value in self.benchmarks.items():
                lines.append(f"- {key}: {value}")

        if self.reference_clients:
            lines.append("")
            lines.append(f"Clientes de referência: {', '.join(self.reference_clients)}")

        if self.reference_clients_by_sector:
            lines.append("")
            lines.append("Clientes de referência por setor:")
            for sector, clients in self.reference_clients_by_sector.items():
                lines.append(f"- {sector}: {', '.join(clients)}")

        if self.cases:
            lines.append("")
            lines.append("Cases:")
            for case in self.cases:
                lines.append(f"- {case.get('client', '')}: {case.get('result', '')}")

        return "\n".join(lines)


def client_from_model(client: MarketingClient) -> ClientConfig:
    profile = client.profile or {}
    return ClientConfig(
        id=str(client.id),
        name=client.name,
        product=client.product,
        description=client.description or "",
        icp=profile.get("icp", {}),
        funnel_stages=profile.get("funnel_stages", []),
        key_metrics=profile.get("key_metrics", []),
        reference_clients_by_sector=profile.get("reference_clients_by_sector", {}),
        reference_clients=profile.get("reference_clients", []),
        differentiators=profile.get("differentiators", []),
        constraints=profile.get("constraints", []),
        urls=profile.get("urls", {}),
        benchmarks=profile.get("benchmarks", {}),
        cases=profile.get("cases", []),
        raw=profile,
    )
