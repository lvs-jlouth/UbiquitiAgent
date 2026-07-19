"""Deterministic audit engine that runs a set of rules against a context."""
from app.audit.rules import default_rules
from app.audit.rules.base import AuditContext, BaseRule, RuleFinding
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditEngine:
    """Runs deterministic audit rules. Never uses AI."""

    def __init__(self, rules: list[BaseRule] | None = None):
        self.rules = rules if rules is not None else default_rules()

    async def run_audit(self, context: AuditContext) -> list[RuleFinding]:
        """Evaluate every rule against the context and aggregate findings."""
        findings: list[RuleFinding] = []
        for rule in self.rules:
            try:
                result = await rule.evaluate(context)
                findings.extend(result)
            except Exception as exc:  # noqa: BLE001 - a bad rule must not abort the audit
                logger.error(
                    "audit_rule_failed",
                    rule_id=getattr(rule, "rule_id", "unknown"),
                    error=str(exc),
                )
        return findings
