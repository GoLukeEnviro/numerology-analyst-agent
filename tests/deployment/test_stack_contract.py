"""Static production-stack contracts that do not require a Docker daemon."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _compose() -> dict[str, object]:
    payload = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_wheel_resource_check_runs_in_the_job_that_builds_the_wheel() -> None:
    """Der Wheel-Ressourcen-Test muss dort laufen, wo ``dist/`` entsteht.

    Ohne diese Bindung baut der pytest-Job kein Wheel und der Test überspringt
    sich in jedem Lauf — lokal wie in der Pipeline.
    """
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    )
    assert isinstance(workflow, dict)
    jobs = workflow["jobs"]
    assert isinstance(jobs, dict)

    building_jobs = [
        name
        for name, job in jobs.items()
        if any("uv build" in str(step.get("run", "")) for step in job["steps"])
    ]
    assert building_jobs, "Kein CI-Job baut ein Wheel"

    for name in building_jobs:
        steps = jobs[name]["steps"]
        checking = [
            step
            for step in steps
            if "test_wheel_contains_prompt_templates" in str(step.get("run", ""))
        ]
        assert checking, f"Job {name!r} baut ein Wheel, prüft aber die Paketressourcen nicht"
        assert all(str(step.get("env", {}).get("NUMRA_REQUIRE_WHEEL", "")) for step in checking), (
            f"Job {name!r} prüft das Wheel, ohne es per NUMRA_REQUIRE_WHEEL zu verlangen — "
            "ein fehlendes Wheel würde sich still überspringen"
        )

    # Die Anforderung darf nicht global gelten: Jobs ohne uv build fuehren
    # pytest aus, ohne ein Wheel bauen zu koennen.
    for name, job in jobs.items():
        if name in building_jobs:
            continue
        assert "NUMRA_REQUIRE_WHEEL" not in str(job), (
            f"Job {name!r} verlangt ein Wheel, baut aber keines"
        )


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
    assert "proxy_add_x_forwarded_for" not in config


def test_images_run_as_non_root_and_have_no_embedded_secrets() -> None:
    api_file = (ROOT / "docker" / "api.Dockerfile").read_text(encoding="utf-8")
    web_file = (ROOT / "docker" / "web.Dockerfile").read_text(encoding="utf-8")

    assert "USER 10001:10001" in api_file
    assert "USER 101" in web_file
    assert "NUMRA_DEEPSEEK_API_KEY" not in api_file + web_file
    assert "NUMRA_RATE_LIMIT_HMAC_SECRET" not in api_file + web_file
    assert "--forwarded-allow-ips=*" not in api_file
    assert "--forwarded-allow-ips=172.30.0.10" in api_file


def test_public_proxy_replaces_untrusted_forwarded_for() -> None:
    config = (ROOT / "deploy" / "nginx" / "numra-https.conf.template").read_text(encoding="utf-8")

    assert "proxy_set_header X-Forwarded-For $remote_addr;" in config
    assert "proxy_add_x_forwarded_for" not in config


def test_production_operations_are_documented_without_public_launch_shortcuts() -> None:
    guide = (ROOT / "deploy" / "README.md").read_text(encoding="utf-8")

    assert "/etc/numra/numra.env" in guide
    assert "127.0.0.1:8080" in guide
    assert "ssh -L 8080:127.0.0.1:8080" in guide
    assert "Kein öffentlicher Launch" in guide


def test_rollback_rehearsal_uses_sha_tags_compatible_with_rollback_script() -> None:
    """rollback.sh accepts only 40-hex image tags; rehearsal must supply those."""
    rehearsal = (ROOT / "deploy" / "scripts" / "rollback-rehearsal.sh").read_text(encoding="utf-8")
    rollback = (ROOT / "deploy" / "scripts" / "rollback.sh").read_text(encoding="utf-8")

    assert "rehearsal-baseline-" not in rehearsal
    assert "rehearsal-rc-" not in rehearsal
    assert "git rev-parse --verify HEAD~1" in rehearsal
    assert "git rev-parse --verify HEAD" in rehearsal
    assert r"^[0-9a-f]{40}$" in rehearsal
    assert r"^[0-9a-f]{40}$" in rollback
    assert "NUMRA_RELEASE_DIR" in rollback
    assert 'NUMRA_RELEASE_DIR="$release_dir"' in rehearsal
    assert "NUMRA_RELEASE_DIR" in rehearsal


def test_restore_config_verifies_before_installing_and_matches_backup_paths() -> None:
    """restore.sh muss dieselben Pfade wie backup-config.sh wiederherstellen.

    OPS-001: backup-config.sh entschluesselt bisher nur zur Verifikation,
    das belegt Lesbarkeit, nicht Wiederherstellbarkeit. restore-config.sh
    muss root verlangen, strukturell pruefen (nicht nur `tar -tzf`) und
    atomar installieren statt direkt in die Zielpfade zu schreiben.
    """
    backup = (ROOT / "deploy" / "scripts" / "backup-config.sh").read_text(encoding="utf-8")
    restore_path = ROOT / "deploy" / "scripts" / "restore-config.sh"
    assert restore_path.is_file(), "deploy/scripts/restore-config.sh fehlt (OPS-001)"
    restore = restore_path.read_text(encoding="utf-8")

    assert "etc/numra/numra.env" in backup
    assert "etc/nginx/sites-available/numra" in backup

    assert "id -u" in restore
    assert "AGE_IDENTITY" in restore
    assert "age --decrypt" in restore
    # Strukturelle Pruefung statt reinem tar -tzf: erwartete Mitgliederliste
    # wird gegen die tatsaechliche abgeglichen, nicht nur "laesst sich lesen".
    assert "etc/numra/numra.env" in restore
    assert "etc/nginx/sites-available/numra" in restore
    assert "0600" in restore
    # Atomar installieren: erst in ein Staging-Verzeichnis extrahieren,
    # dann mv in die Zielpfade - kein Schreiben ins Ziel vor Verifikation.
    assert "mktemp -d" in restore
    assert "mv " in restore


def test_release_deploys_a_prebuilt_image_instead_of_building_on_the_host() -> None:
    """release.sh darf nicht auf dem Zielhost neu bauen (OPS-002).

    Ein Docker-Tag ist veraenderlich; zwei separate Builds desselben
    Git-SHA sind nicht garantiert dasselbe Artefakt (Attestation-
    Zeitstempel, BuildKit-Cache-Zustand). release.sh muss das bereits
    gebaute, bereits getestete Image anhand seiner ID/Digest deployen -
    "build once, test once, promote by digest" - statt es auf dem
    Zielhost ein zweites, ungeprueftes Mal zu bauen.
    """
    release = (ROOT / "deploy" / "scripts" / "release.sh").read_text(encoding="utf-8")
    build_once = ROOT / "deploy" / "scripts" / "build-release-image.sh"
    assert build_once.is_file(), "deploy/scripts/build-release-image.sh fehlt (OPS-002)"

    assert 'docker compose --env-file "$env_file" build' not in release
    assert "--pull" not in release
    assert "docker image inspect" in release
    assert "--no-build" in release

    build_once_text = build_once.read_text(encoding="utf-8")
    assert "docker compose" in build_once_text
    assert "build" in build_once_text
    assert ".Id" in build_once_text or "RepoDigests" in build_once_text

    # release.sh, rollback.sh und rollback-rehearsal.sh muessen denselben
    # Release-Verzeichnis-Vertrag teilen (ueberschreibbar statt hartcodiert),
    # sonst laesst sich keines der drei Skripte gegen dasselbe Testverzeichnis
    # pruefen und ihre current/previous-Marker laufen auseinander.
    rollback = (ROOT / "deploy" / "scripts" / "rollback.sh").read_text(encoding="utf-8")
    assert "NUMRA_RELEASE_DIR:-/opt/numra/releases" in release
    assert "NUMRA_RELEASE_DIR:-/opt/numra/releases" in rollback


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
