"""Public-launch automation contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_host_nginx_terminates_tls_and_keeps_application_on_loopback() -> None:
    config = _read("deploy/nginx/numra-https.conf.template")

    assert "listen 443 ssl" in config
    assert "proxy_pass http://127.0.0.1:8080;" in config
    assert "ssl_certificate /etc/letsencrypt/live/${NUMRA_DOMAIN}/fullchain.pem;" in config
    assert "Strict-Transport-Security" in config
    assert "access_log off;" in config
    assert "client_max_body_size 64k;" in config


def test_https_bootstrap_validates_domain_and_renewal() -> None:
    script = _read("deploy/scripts/enable-https.sh")

    assert "certbot certonly" in script
    assert "certbot renew --dry-run" in script
    assert "nginx -t" in script
    assert "NUMRA_DOMAIN" in script
    assert "NUMRA_TLS_EMAIL" in script
    assert "systemctl reload nginx" in script


def test_release_and_rollback_use_immutable_commit_tags() -> None:
    release = _read("deploy/scripts/release.sh")
    rollback = _read("deploy/scripts/rollback.sh")

    assert "^[0-9a-f]{40}$" in release
    assert "git rev-parse --verify HEAD" in release
    assert "NUMRA_IMAGE_TAG" in release
    assert "/opt/numra/releases/previous" in release
    assert "docker compose --env-file" in release
    assert "up -d --wait --wait-timeout 60" in release
    assert "docker image inspect" in rollback
    assert "up -d --no-build --wait --wait-timeout 60" in rollback


def test_configuration_backup_is_encrypted_without_plaintext_archive() -> None:
    script = _read("deploy/scripts/backup-config.sh")

    assert "age --encrypt" in script
    assert "/etc/numra/numra.env" in script
    assert "/var/backups/numra" in script
    assert "tar -czf -" in script
    assert ".tar.gz.age" in script
    assert '.tar.gz"' not in script


def test_public_launch_check_fails_closed_on_external_gates() -> None:
    script = _read("deploy/scripts/public-launch-check.sh")
    checklist = _read("docs/operations/launch-checklist.md")

    assert "NUMRA_DOMAIN" in script
    assert "numra-legal-approved" in script
    assert "öffentlichen Launch gesperrt" in script
    assert "llm-transfer-approved" in script
    assert "certbot certificates" in script
    assert "Betreiberanschrift" in checklist
    assert "DNS-A/AAAA" in checklist
    assert "geschlossene Beta" in checklist
    assert "Rollback" in checklist
    assert "Wiederherstellung" in checklist
