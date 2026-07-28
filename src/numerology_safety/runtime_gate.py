"""Runtime file-marker gates for legal and data-transfer approvals.

Checks that marker files exist with correct ownership and permissions
before the application allows LLM operations in production.

Spec: /etc/numra/numra-legal-approved and /etc/numra/llm-transfer-approved
must exist, be owned by root:root, and have mode 0600.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import stat
import sys

_LEGAL_APPROVED = Path("/etc/numra/numra-legal-approved")
_LLM_TRANSFER_APPROVED = Path("/etc/numra/llm-transfer-approved")
_REQUIRED_UID = 0  # root
_REQUIRED_GID = 0  # root
_REQUIRED_MODE = 0o600


@dataclass(frozen=True, slots=True)
class GateResult:
    """Outcome of a single file-marker gate check."""

    path: Path
    exists: bool
    owner_correct: bool
    permissions_correct: bool

    @property
    def passed(self) -> bool:
        return self.exists and self.owner_correct and self.permissions_correct


@dataclass(frozen=True, slots=True)
class RuntimeGateResult:
    """Aggregate result of all runtime gate checks."""

    legal_approved: GateResult
    llm_transfer_approved: GateResult
    platform_skipped: bool

    @property
    def all_passed(self) -> bool:
        if self.platform_skipped:
            return True
        return self.legal_approved.passed and self.llm_transfer_approved.passed

    @property
    def failure_reasons(self) -> list[str]:
        reasons: list[str] = []
        if self.platform_skipped:
            return reasons
        for label, gate in [
            ("numra-legal-approved", self.legal_approved),
            ("llm-transfer-approved", self.llm_transfer_approved),
        ]:
            if not gate.passed:
                failures: list[str] = []
                if not gate.exists:
                    failures.append("Datei existiert nicht")
                if gate.exists and not gate.owner_correct:
                    failures.append("Besitzer nicht root:root")
                if gate.exists and not gate.permissions_correct:
                    failures.append(f"Berechtigungen nicht {oct(_REQUIRED_MODE)}")
                reasons.append(f"/etc/numra/{label}: {', '.join(failures)}")
        return reasons


def _check_single(path: Path) -> GateResult:
    """Check a single file-marker for existence, ownership, and permissions."""
    exists = path.is_file()
    owner_correct = False
    permissions_correct = False
    if exists:
        st = path.stat()
        owner_correct = (st.st_uid == _REQUIRED_UID) and (st.st_gid == _REQUIRED_GID)
        permissions_correct = stat.S_IMODE(st.st_mode) == _REQUIRED_MODE
    return GateResult(
        path=path,
        exists=exists,
        owner_correct=owner_correct,
        permissions_correct=permissions_correct,
    )


def verify_runtime_gates() -> RuntimeGateResult:
    """Verify that all required runtime marker files are present and correct.

    On non-Linux platforms (Windows, macOS), the check is skipped
    with ``platform_skipped=True`` to allow local development.

    Raises:
        RuntimeError: If one or more gates fail with a clear message.
    """
    if sys.platform != "linux":
        return RuntimeGateResult(
            legal_approved=GateResult(
                path=_LEGAL_APPROVED, exists=False, owner_correct=False, permissions_correct=False
            ),
            llm_transfer_approved=GateResult(
                path=_LLM_TRANSFER_APPROVED,
                exists=False,
                owner_correct=False,
                permissions_correct=False,
            ),
            platform_skipped=True,
        )

    legal = _check_single(_LEGAL_APPROVED)
    llm = _check_single(_LLM_TRANSFER_APPROVED)
    result = RuntimeGateResult(
        legal_approved=legal, llm_transfer_approved=llm, platform_skipped=False
    )

    if not result.all_passed:
        reasons = "\n".join(f"  - {r}" for r in result.failure_reasons)
        raise RuntimeError(
            "Numra LLM Runtime-Gate fehlgeschlagen.\n"
            "Die folgenden Rechts- und Datenschutz-Freigaben fehlen:\n"
            f"{reasons}\n"
            "Erforderliche Dateien (root:root, 0600):\n"
            f"  {_LEGAL_APPROVED}\n"
            f"  {_LLM_TRANSFER_APPROVED}\n"
            "Ohne diese Freigaben sind LLM-Operationen nicht zulässig.\n"
            "Siehe docs/operations/llm-provider.md - Abschnitt 'Runtime-Gates'."
        )

    return result
