"""Tests for runtime file-marker gates."""

from __future__ import annotations

from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from numerology_safety.runtime_gate import (
    GateResult,
    RuntimeGateResult,
    _check_single,
    verify_runtime_gates,
)


class TestGateResult:
    def test_all_passed_when_everything_correct(self) -> None:
        result = GateResult(
            path=Path("/etc/numra/test"),
            exists=True,
            owner_correct=True,
            permissions_correct=True,
        )
        assert result.passed is True

    def test_not_passed_when_missing(self) -> None:
        result = GateResult(
            path=Path("/etc/numra/test"),
            exists=False,
            owner_correct=False,
            permissions_correct=False,
        )
        assert result.passed is False

    def test_not_passed_when_wrong_owner(self) -> None:
        result = GateResult(
            path=Path("/etc/numra/test"),
            exists=True,
            owner_correct=False,
            permissions_correct=True,
        )
        assert result.passed is False

    def test_not_passed_when_wrong_permissions(self) -> None:
        result = GateResult(
            path=Path("/etc/numra/test"),
            exists=True,
            owner_correct=True,
            permissions_correct=False,
        )
        assert result.passed is False


class TestRuntimeGateResult:
    def test_all_passed_true_when_both_gates_pass(self) -> None:
        result = RuntimeGateResult(
            legal_approved=GateResult(
                path=Path("/etc/numra/numra-legal-approved"),
                exists=True,
                owner_correct=True,
                permissions_correct=True,
            ),
            llm_transfer_approved=GateResult(
                path=Path("/etc/numra/llm-transfer-approved"),
                exists=True,
                owner_correct=True,
                permissions_correct=True,
            ),
            platform_skipped=False,
        )
        assert result.all_passed is True
        assert result.failure_reasons == []

    def test_all_passed_true_when_platform_skipped(self) -> None:
        result = RuntimeGateResult(
            legal_approved=GateResult(
                path=Path("/etc/numra/numra-legal-approved"),
                exists=False,
                owner_correct=False,
                permissions_correct=False,
            ),
            llm_transfer_approved=GateResult(
                path=Path("/etc/numra/llm-transfer-approved"),
                exists=False,
                owner_correct=False,
                permissions_correct=False,
            ),
            platform_skipped=True,
        )
        assert result.all_passed is True
        assert result.failure_reasons == []

    def test_failure_reasons_when_legal_missing(self) -> None:
        result = RuntimeGateResult(
            legal_approved=GateResult(
                path=Path("/etc/numra/numra-legal-approved"),
                exists=False,
                owner_correct=False,
                permissions_correct=False,
            ),
            llm_transfer_approved=GateResult(
                path=Path("/etc/numra/llm-transfer-approved"),
                exists=True,
                owner_correct=True,
                permissions_correct=True,
            ),
            platform_skipped=False,
        )
        assert result.all_passed is False
        assert any("numra-legal-approved" in r for r in result.failure_reasons)
        assert any("existiert nicht" in r for r in result.failure_reasons)


class TestVerifyRuntimeGates:
    def test_skips_on_non_linux(self) -> None:
        """On Windows/macOS the gate must skip without error."""
        with patch.object(sys, "platform", "win32"):
            result = verify_runtime_gates()
        assert result.platform_skipped is True
        assert result.all_passed is True

    def test_skips_on_macos(self) -> None:
        with patch.object(sys, "platform", "darwin"):
            result = verify_runtime_gates()
        assert result.platform_skipped is True
        assert result.all_passed is True

    def test_raises_on_linux_when_files_missing(self) -> None:
        """On Linux without marker files, must raise RuntimeError."""
        with (
            patch.object(sys, "platform", "linux"),
            patch.object(Path, "is_file", return_value=False),
            pytest.raises(RuntimeError, match="Runtime-Gate fehlgeschlagen"),
        ):
            verify_runtime_gates()

    def test_raises_on_linux_when_only_legal_missing(self) -> None:
        legal_path = Path("/etc/numra/numra-legal-approved")
        llm_path = Path("/etc/numra/llm-transfer-approved")

        def fake_is_file(self: Path) -> bool:
            return self != legal_path and self == llm_path

        with (
            patch.object(sys, "platform", "linux"),
            patch.object(Path, "is_file", fake_is_file),
            patch.object(Path, "stat", return_value=_fake_stat(root_owned=True)),
            pytest.raises(RuntimeError, match="Runtime-Gate fehlgeschlagen"),
        ):
            verify_runtime_gates()


class TestCheckSingle:
    def test_missing_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent"
        result = _check_single(missing)
        assert result.exists is False
        assert result.passed is False

    def test_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "marker"
        f.write_text("approved")
        result = _check_single(f)
        assert result.exists is True

    def test_existing_file_wrong_owner(self, tmp_path: Path) -> None:
        """On Windows owner check always passes because st_uid is always 0."""
        f = tmp_path / "marker"
        f.write_text("approved")
        result = _check_single(f)
        if sys.platform == "win32":
            # Windows: st_uid is 0, so owner check passes
            assert result.owner_correct is True
        else:
            # Non-root on Linux: owner check fails
            assert result.owner_correct is False


def _fake_stat(*, root_owned: bool = False) -> object:
    """Create a mock stat result."""

    class FakeStat:
        st_uid = 0 if root_owned else 1000
        st_gid = 0 if root_owned else 1000
        st_mode = 0o100600  # Regular file, 0600 permissions

    return FakeStat()
