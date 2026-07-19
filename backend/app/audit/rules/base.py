"""Audit rule base classes and shared context."""
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class AuditContext(BaseModel):
    """Immutable snapshot of network state passed to every audit rule.

    All fields default to empty so rules can run against partial data.
    """

    devices: list[dict[str, Any]] = Field(default_factory=list)
    clients: list[dict[str, Any]] = Field(default_factory=list)
    networks: list[dict[str, Any]] = Field(default_factory=list)  # VLAN / network configs
    wlans: list[dict[str, Any]] = Field(default_factory=list)  # wireless configs
    firewall_rules: list[dict[str, Any]] = Field(default_factory=list)
    port_forwards: list[dict[str, Any]] = Field(default_factory=list)
    routing: list[dict[str, Any]] = Field(default_factory=list)
    dns: dict[str, Any] = Field(default_factory=dict)
    site_stats: dict[str, Any] = Field(default_factory=dict)


class RuleFinding(BaseModel):
    """A finding produced by a rule (pre-persistence representation)."""

    rule_id: str
    rule_name: str
    severity: str
    category: str
    title: str
    description: str
    affected_resource: str | None = None
    evidence: dict[str, Any] | None = None
    recommendation: str | None = None


class BaseRule(ABC):
    """Abstract base class for deterministic audit rules."""

    rule_id: str = "base"
    rule_name: str = "Base Rule"
    severity: str = "info"
    category: str = "security"

    @abstractmethod
    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        """Evaluate the rule against the context and return findings."""
        raise NotImplementedError

    def _finding(
        self,
        title: str,
        description: str,
        affected_resource: str | None = None,
        evidence: dict[str, Any] | None = None,
        recommendation: str | None = None,
        severity: str | None = None,
    ) -> RuleFinding:
        """Helper to construct a RuleFinding using this rule's metadata."""
        return RuleFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            severity=severity or self.severity,
            category=self.category,
            title=title,
            description=description,
            affected_resource=affected_resource,
            evidence=evidence,
            recommendation=recommendation,
        )
