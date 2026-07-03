[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$skillRoot = Split-Path -Parent $PSScriptRoot

$budgets = @{
    'SKILL.md' = 4800
    'references\bypass.md' = 1200
    'references\briefs.md' = 2800
    'references\session-minimo.md' = 2000
    'references\roteamento.md' = 4000
    'references\quality.md' = 2800
    'references\artefatos\issue.md' = 2800
    'references\artefatos\branch-commit.md' = 2800
    'references\artefatos\pr-release.md' = 2800
    'references\planejamento\diagnose.md' = 2800
    'references\planejamento\start.md' = 2800
    'references\planejamento\status-next.md' = 2800
    'references\planejamento\review.md' = 2800
    'references\planejamento\roadmap.md' = 2800
    'references\planejamento\persistencia.md' = 2800
}

$failed = $false

foreach ($entry in $budgets.GetEnumerator() | Sort-Object Name) {
    $path = Join-Path $skillRoot $entry.Key
    if (-not (Test-Path -LiteralPath $path)) {
        Write-Error "Arquivo obrigatório ausente: $($entry.Key)"
    }

    $content = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    $tokens = [math]::Ceiling($content.Length / 4)
    $limit = [math]::Ceiling($entry.Value / 4)
    $status = if ($content.Length -le $entry.Value) { 'OK' } else { 'EXCEDEU' }

    [pscustomobject]@{
        Arquivo = $entry.Key
        Caracteres = $content.Length
        TokensAproximados = $tokens
        LimiteAproximado = $limit
        Status = $status
    }

    if ($content.Length -gt $entry.Value) {
        $failed = $true
    }
}

$obsolete = @(
    'references\commands.md',
    'references\session.md',
    'references\planejamento.md'
)

foreach ($relative in $obsolete) {
    if (Test-Path -LiteralPath (Join-Path $skillRoot $relative)) {
        Write-Warning "Referência monolítica obsoleta encontrada: $relative"
        $failed = $true
    }
}

if ($failed) {
    throw 'A validação de contexto encontrou violações.'
}

Write-Host 'Validação de contexto concluída.'
