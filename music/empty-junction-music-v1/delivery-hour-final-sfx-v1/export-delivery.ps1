$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$junctionValidationPath = Join-Path $PSScriptRoot 'delivery-validation.json'
$junctionValidation = Get-Content -LiteralPath $junctionValidationPath -Raw | ConvertFrom-Json
if ($junctionValidation.status -ne 'passed' -or $junctionValidation.duration_seconds -ne 3600) {
    throw 'A complete passing one-hour validation is required before delivery.'
}
$junctionProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
$junctionExportRoot = [IO.Path]::GetFullPath((Join-Path $junctionProjectRoot 'exports\11-empty-junction'))
$junctionExpectedParent = [IO.Path]::GetFullPath((Join-Path $junctionProjectRoot 'exports')) + [IO.Path]::DirectorySeparatorChar
if (-not $junctionExportRoot.StartsWith($junctionExpectedParent, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Resolved delivery path is outside the intended exports directory.'
}
$null = New-Item -ItemType Directory -Path $junctionExportRoot -Force
$junctionDelivered = @()
foreach ($junctionOutput in $junctionValidation.outputs) {
    $junctionSourcePath = Join-Path $PSScriptRoot $junctionOutput.file
    $junctionDestinationPath = Join-Path $junctionExportRoot ([IO.Path]::GetFileName($junctionSourcePath))
    if ((Get-FileHash -LiteralPath $junctionSourcePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $junctionOutput.sha256) {
        throw "Source validation hash mismatch: $junctionSourcePath"
    }
    if (-not (Test-Path -LiteralPath $junctionDestinationPath)) {
        [IO.File]::Copy($junctionSourcePath, $junctionDestinationPath, $false)
    }
    $junctionDeliveredHash = (Get-FileHash -LiteralPath $junctionDestinationPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($junctionDeliveredHash -ne $junctionOutput.sha256) {
        throw "Existing or delivered file differs: $junctionDestinationPath"
    }
    $junctionDelivered += [ordered]@{
        path = $junctionDestinationPath
        bytes = (Get-Item -LiteralPath $junctionDestinationPath).Length
        sha256 = $junctionDeliveredHash
        matches_validated_output = $true
    }
}
$junctionReceipt = [ordered]@{
    status = 'delivered'
    duration_seconds = 3600
    outputs = $junctionDelivered
    source_validation = $junctionValidationPath
    local_delivery_only = $true
    remote_backup_performed = $false
}
$junctionReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'delivery-paths.json') -Encoding utf8
$junctionReceipt | ConvertTo-Json -Depth 8
