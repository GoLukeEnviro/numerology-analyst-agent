"""Static production-stack contracts that do not require a Docker daemon."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _compose() -> dict[str, object]:
    payload = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_only_gateway_is_published_on_loopback() -> None:
    services = _compose()["services"]
    assert isinstance(services, dict)

    gateway = services["gateway"]
    api = services["api"]
    redis = services["redis"]
    assert isinstance(gateway, dict)
    assert isinstance(api, dict)
    assert isinstance(redis, dict)
    assert gateway["ports"] == ["127.0.0.1:8080:8080"]
    assert "ports" not in api
    assert "ports" not in redis


def test_private_staging_accepts_both_browser_loopback_origins() -> None:
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    example_env = (ROOT / "deploy" / "numra.env.example").read_text(encoding="utf-8")
    guide = (ROOT / "deploy" / "README.md").read_text(encoding="utf-8")
    allowed_origins = "NUMRA_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080"

    assert ("${NUMRA_ALLOWED_ORIGINS:-http://localhost:8080,http://127.0.0.1:8080}") in compose
    assert allowed_origins in example_env
    assert allowed_origins in guide


def test_containers_are_hardened_and_redis_is_ephemeral() -> None:
    services = _compose()["services"]
    assert isinstance(services, dict)

    for name in ("gateway", "api", "redis"):
        service = services[name]
        assert isinstance(service, dict)
        assert service["read_only"] is True
        assert service["cap_drop"] == ["ALL"]
        assert service["security_opt"] == ["no-new-privileges:true"]
        assert "healthcheck" in service

    redis = services["redis"]
    assert isinstance(redis, dict)
    assert redis["user"] == "999:1000"
    assert redis["tmpfs"] == ["/data"]
    assert "volumes" not in redis


def test_gateway_disables_sensitive_logs_and_api_caching() -> None:
    config = (ROOT / "docker" / "nginx" / "default.conf").read_text(encoding="utf-8")
    security_headers = (ROOT / "docker" / "nginx" / "security-headers.conf").read_text(
        encoding="utf-8"
    )

    assert "access_log off;" in config
    assert "client_max_body_size 64k;" in config
    assert "proxy_pass http://api:8000;" in config
    assert "proxy_no_cache 1;" in config
    assert "proxy_cache_bypass 1;" in config
    assert config.count("include /etc/nginx/snippets/security-headers.conf;") == 7
    assert "add_header Content-Security-Policy" in security_headers
    assert "try_files $uri $uri/ /index.html;" in config


def test_images_run_as_non_root_and_have_no_embedded_secrets() -> None:
    api_file = (ROOT / "docker" / "api.Dockerfile").read_text(encoding="utf-8")
    web_file = (ROOT / "docker" / "web.Dockerfile").read_text(encoding="utf-8")

    assert "USER 10001:10001" in api_file
    assert "USER 101" in web_file
    assert "NUMRA_DEEPSEEK_API_KEY" not in api_file + web_file
    assert "NUMRA_RATE_LIMIT_HMAC_SECRET" not in api_file + web_file


def test_production_operations_are_documented_without_public_launch_shortcuts() -> None:
    guide = (ROOT / "deploy" / "README.md").read_text(encoding="utf-8")

    assert "/etc/numra/numra.env" in guide
    assert "127.0.0.1:8080" in guide
    assert "ssh -L 8080:127.0.0.1:8080" in guide
    assert "Kein öffentlicher Launch" in guide


def test_local_deepseek_activation_keeps_secrets_out_of_git() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    configure_path = ROOT / "deploy" / "scripts" / "configure-local-llm.ps1"
    smoke_path = ROOT / "deploy" / "scripts" / "deepseek-smoke.ps1"
    assert configure_path.is_file()
    assert smoke_path.is_file()
    configure = configure_path.read_text(encoding="utf-8")
    smoke = smoke_path.read_text(encoding="utf-8")
    guide = (ROOT / "deploy" / "README.md").read_text(encoding="utf-8")

    assert "deploy/*.env.local" in gitignore
    assert "Read-Host" in configure
    assert "-MaskInput" in configure
    assert "RandomNumberGenerator" in configure
    assert "NUMRA_LLM_ENABLED=true" in configure
    assert "NUMRA_DEEPSEEK_MODEL=deepseek-v4-pro" in configure
    assert "/api/v1/profiles/calculate" in smoke
    assert "/api/v1/analyses/report" in smoke
    assert "NUMRA_DEEPSEEK_API_KEY=" not in smoke
    assert "configure-local-llm.ps1" in guide
    assert "deepseek-smoke.ps1" in guide
