[CmdletBinding()]
param(
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
$apiRoot = $BaseUrl.TrimEnd("/")
$meta = Invoke-RestMethod -Uri "$apiRoot/api/v1/meta" -Method Get
if (-not $meta.llm.enabled -or $meta.llm.provider -ne "deepseek") {
    throw "DeepSeek ist im laufenden API-Container nicht aktiviert."
}

$profileRequest = @{
    person = @{
        core_name = "Numra Beispiel"
        active_name = $null
        birth_date = "1990-04-12"
        as_of_date = "2026-07-26"
        locale = "de"
        consent_given = $false
    }
    policy = @{
        system = "pythagorean"
        version = "v1"
        y_mode = "phonetic"
        umlaut_policy = "de-direct-v1"
        name_basis = "both_separate"
        date_method = "both"
        locale = "de"
        master_numbers = @(11, 22, 33)
    }
}

$profile = Invoke-RestMethod `
    -Uri "$apiRoot/api/v1/profiles/calculate" `
    -Method Post `
    -ContentType "application/json" `
    -Body ($profileRequest | ConvertTo-Json -Depth 12 -Compress)

$reportRequest = @{
    consent = $true
    device_id = "deepseek-smoke-$([guid]::NewGuid())"
    profile = $profile
}
$report = Invoke-RestMethod `
    -Uri "$apiRoot/api/v1/analyses/report" `
    -Method Post `
    -ContentType "application/json" `
    -Body ($reportRequest | ConvertTo-Json -Depth 100 -Compress)

if ($report.provenance.model -ne "deepseek-v4-pro") {
    throw "Unerwartetes Provider-Modell: $($report.provenance.model)"
}
if ($report.provenance.calculation_hash -ne $profile.deterministic_hash) {
    throw "Der Bericht referenziert nicht den berechneten Profilhash."
}
if ([string]::IsNullOrWhiteSpace($report.summary)) {
    throw "DeepSeek hat keinen validierten Bericht geliefert."
}

[pscustomobject]@{
    status = "ok"
    provider = $report.provenance.provider
    model = $report.provenance.model
    thinking = $report.provenance.thinking
    temperature = $report.provenance.temperature
    prompt_tokens = $report.provenance.prompt_tokens
    completion_tokens = $report.provenance.completion_tokens
    calculation_hash = $profile.deterministic_hash
} | Format-List
