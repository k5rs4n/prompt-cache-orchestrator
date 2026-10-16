# Prompt Cache Orchestrator - Windows Installer for Antigravity

$TargetGlobal = "$env:USERPROFILE\.gemini\config\skills\prompt-cache-orchestrator"
$SourceSkill = Join-Path $PSScriptRoot "skills\prompt-cache-orchestrator\SKILL.md"

Write-Host "⚡ Installing Prompt Cache Orchestrator into Antigravity..." -ForegroundColor Cyan

if (-not (Test-Path $SourceSkill)) {
    Write-Error "Skill source not found at: $SourceSkill"
    exit 1
}

New-Item -ItemType Directory -Path $TargetGlobal -Force | Out-Null
Copy-Item -Path $SourceSkill -Destination "$TargetGlobal\SKILL.md" -Force

Write-Host "✅ Successfully installed globally at:" -ForegroundColor Green
Write-Host "   $TargetGlobal\SKILL.md" -ForegroundColor Gray
Write-Host "`nAntigravity can now automatically use the 'prompt-cache-orchestrator' skill!" -ForegroundColor Yellow
