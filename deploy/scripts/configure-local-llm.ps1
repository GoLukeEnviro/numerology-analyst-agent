[CmdletBinding()]
param(
    [string]$OutputPath = (
        Join-Path $PSScriptRoot "..\numra.env.local"
    )
)

$ErrorActionPreference = "Stop"

$apiKey = Read-Host "DeepSeek API-Key (Eingabe wird maskiert)" -MaskInput
if (
    [string]::IsNullOrWhiteSpace($apiKey) -or
    $apiKey.Length -lt 20 -or
    $apiKey.Length -gt 512 -or
    $apiKey.Contains("`r") -or
    $apiKey.Contains("`n")
) {
    throw "Der DeepSeek API-Key ist leer oder besitzt ein ungueltiges Format."
}

$secretBytes = [byte[]]::new(32)
[System.Security.Cryptography.RandomNumberGenerator]::Fill($secretBytes)
$rateLimitSecret = [Convert]::ToHexString($secretBytes).ToLowerInvariant()
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)

$lines = @(
    "NUMRA_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080"
    "NUMRA_LLM_ENABLED=true"
    "NUMRA_DEEPSEEK_BASE_URL=https://api.deepseek.com"
    "NUMRA_DEEPSEEK_MODEL=deepseek-v4-pro"
    "NUMRA_DEEPSEEK_API_KEY=$apiKey"
    "NUMRA_RATE_LIMIT_HMAC_SECRET=$rateLimitSecret"
)

[System.IO.File]::WriteAllLines(
    $resolvedOutput,
    $lines,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Lokale DeepSeek-Konfiguration wurde geschrieben:"
Write-Host $resolvedOutput
Write-Host "Die Datei wird von Git ignoriert. Den API-Key niemals committen."
