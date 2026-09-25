"""Prompt injection defense and adversarial request filter for OlistIQ AI Analyst."""

import re
import logging
from typing import Tuple

logger = logging.getLogger("olistiq.ai_analyst.security")

ADVERSARIAL_PATTERNS = [
    r"\bignore\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules|guardrails|restrictions)\b",
    r"\bdelete\s+(?:the\s+)?(?:database|all|table|from)\b",
    r"\bdrop\s+(?:all\s+)?(?:table|tables|database|view|index|schema)\b",
    r"\bshow\s+(?:me\s+)?(?:the\s+)?(?:database\s+)?(?:password|credentials|api_key|secret)\b",
    r"\bbypass\s+(?:all\s+)?(?:security|restrictions|guardrails|rules)\b",
    r"\bexecute\s+(?:arbitrary\s+)?(?:sql|command|script)\b",
    r"\bsystem\s+prompt\b",
    r"\bjailbreak\b",
    r"\bformat\s+(?:c:|c|drive|disk)\b",
    r"\bformat\b.*\b(?:drive|disk|c:)\b",
    r"\bupdate\s+\w+\s+set\b",
    r"\binsert\s+into\b",
    r"\btruncate\s+(?:table)?\b",
    r"\balter\s+table\b",
    r"\battach\s+database\b",
    r"\bpragma\b",
    r"\bexec(?:ute)?\s+(?:immediate|xp_)\b",
    r"\bunion\s+select\b",
]


class SecurityGuardrails:
    """Detects and safely rejects malicious prompt injection and system override requests."""

    @staticmethod
    def inspect_input(question: str) -> Tuple[bool, str]:
        """Returns (is_safe: bool, reason: str)."""
        if not question or not question.strip():
            return False, "Query question is empty."

        q_lower = question.lower()

        for pattern in ADVERSARIAL_PATTERNS:
            if re.search(pattern, q_lower, flags=re.IGNORECASE):
                logger.warning("Adversarial prompt injection pattern detected: '%s' in question '%s'", pattern, question)
                return False, (
                    "Security Notice: Your request contained administrative, system-level, or potentially unsafe keywords. "
                    "The OlistIQ AI Analyst only processes read-only e-commerce decision intelligence queries."
                )

        return True, ""


security_guardrails = SecurityGuardrails()
