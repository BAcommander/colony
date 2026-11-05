# Refresh only this scene's documentation from current settings and verified reports.
# Run again after final encoded validation. This never renders, commits or pushes.
$ErrorActionPreference = 'Stop'
$taskSceneDirectory = Split-Path -Parent $PSScriptRoot
$taskRepoDirectory = ([System.IO.DirectoryInfo]$PSScriptRoot).Parent.Parent.Parent.FullName
$taskManifestPath = Join-Path $taskRepoDirectory 'final/18-back-before-dawn/manifest.json'
$taskReadmePath = Join-Path $taskRepoDirectory 'final/18-back-before-dawn/README.md'
$taskSettingsPath = Join-Path $taskSceneDirectory 'settings.json'
$taskUtf8 = [System.Text.UTF8Encoding]::new($false)

function Read-TaskJson([string]$taskPath) {
    return [System.IO.File]::ReadAllText($taskPath) | ConvertFrom-Json
}

function Write-TaskJson([string]$taskPath, $taskValue) {
    $taskText = ($taskValue | ConvertTo-Json -Depth 100) + "`n"
    [System.IO.File]::WriteAllText($taskPath, $taskText, $taskUtf8)
}

function Get-TaskHash([string]$taskPath) {
    return (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-TaskReportInputs($taskReport) {
    $taskStaleInputs = @()
    $taskProperties = @($taskReport.input_hashes.PSObject.Properties)
    foreach ($taskProperty in $taskProperties) {
        $taskInput = Join-Path $taskRepoDirectory $taskProperty.Name
        if (-not (Test-Path -LiteralPath $taskInput -PathType Leaf)) {
            $taskStaleInputs += $taskProperty.Name
        } elseif ((Get-TaskHash $taskInput) -ne $taskProperty.Value) {
            $taskStaleInputs += $taskProperty.Name
        }
    }
    return [pscustomobject]@{
        verified = ($taskProperties.Count -gt 0 -and $taskStaleInputs.Count -eq 0)
        checked = $taskProperties.Count
        stale = $taskStaleInputs
    }
}

$taskSettings = Read-TaskJson $taskSettingsPath
$taskManifest = Read-TaskJson $taskManifestPath
$taskSettingsHash = Get-TaskHash $taskSettingsPath
$taskSourcePath = Join-Path $taskRepoDirectory $taskSettings.source
if ((Get-TaskHash $taskSourcePath) -ne $taskSettings.source_sha256) {
    throw 'The source hash does not match the current scene settings.'
}
$taskManifest.animation.clocks.production_attention_status = 'Implemented via --attention-mode production600; full600s playback and user acceptance pending.'
$taskManifest.animation | Add-Member -NotePropertyName effect_groups -NotePropertyValue @('foliage','rain','road','drips','cabin','scope','lamp','dust','traffic') -Force
$taskManifest.animation | Add-Member -NotePropertyName settings -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/settings.json';sha256=$taskSettingsHash}) -Force
$taskManifest.animation | Add-Member -NotePropertyName support_assets -NotePropertyValue ([ordered]@{manifest='music/back-before-dawn-animation-v1/assets/asset-manifest.json';manifest_sha256=(Get-TaskHash (Join-Path $taskSceneDirectory 'assets/asset-manifest.json'));usage='Generated RGBA1980s sedan with measured actual headlamp centroids is consumed. Generated tree-clean sky is retained as a rejected experiment, not consumed by the current renderer. Foliage uses fixed-boundary original-source deformation with source-tap/Jacobian audit. Whole hero source untouched.'}) -Force
$taskManifest.animation | Add-Member -NotePropertyName cue_sheet -NotePropertyValue 'music/back-before-dawn-animation-v1/documentation/cue-sheet.json' -Force
$taskManifest.animation | Add-Member -NotePropertyName physical_omissions -NotePropertyValue @('No steam from lidded bench vessel.','No unmotivated rear exhaust, sparks or time-travel burst.','Parked hero body, wheels and gullwing door remain fixed.') -Force

$taskCueSheet = [ordered]@{
    date = '2026-11-05'
    status = 'Exact implemented visual settings; no sound or gains approved.'
    source = $taskSettings.source
    source_sha256 = $taskSettings.source_sha256
    settings_path = 'music/back-before-dawn-animation-v1/settings.json'
    settings_sha256 = $taskSettingsHash
    environment_period_seconds = $taskSettings.environment_period_seconds
    default_attention_mode = $taskSettings.attention_mode
    schedule_tuple_units = [ordered]@{gusts='onset,rise,hold,fall seconds';lamp_dips='onset seconds,depth';panel_starts='one start per cabin_banks index, seconds'}
    lamp_envelope_seconds = [ordered]@{rise=0.055;hold=0.10;fall=0.33}
    diagnostic_duration_seconds = 12
    passing_car_duration_seconds = $taskSettings.passing_car.duration_seconds
    cabin_banks = $taskSettings.cabin_banks
    schedules = $taskSettings.schedules
    sound_policy = 'Use actual visual visibility and source-attached events for later sound; not every light change needs a sound. No transferred Snowline gains.'
    production600_review_status = 'Mode implemented; full ten-minute playback and music/SFX balance pending.'
}
Write-TaskJson (Join-Path $PSScriptRoot 'cue-sheet.json') $taskCueSheet

$taskNativePath = Join-Path $taskSceneDirectory 'native-validation.json'
$taskNativeCurrent = $false
$taskManifest.animation | Add-Member -NotePropertyName native_checks -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/native-validation.json';status='current native evidence pending';input_hashes_current=$false}) -Force
if (Test-Path -LiteralPath $taskNativePath -PathType Leaf) {
    $taskNative = Read-TaskJson $taskNativePath
    $taskNativeInputs = Test-TaskReportInputs $taskNative
    $taskNativeCurrent = $taskNativeInputs.verified
    $taskManifest.animation | Add-Member -NotePropertyName native_checks -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/native-validation.json';report_sha256=(Get-TaskHash $taskNativePath);status=$taskNative.status;input_hashes_current=$taskNativeCurrent;input_files_checked=$taskNativeInputs.checked;stale_inputs=$taskNativeInputs.stale}) -Force
}

$taskProductionNativePath = Join-Path $taskSceneDirectory 'native-validation-production600.json'
$taskProductionNativeCurrent = $false
$taskManifest.animation | Add-Member -NotePropertyName production_attention_native_checks -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/native-validation-production600.json';status='current native600s evidence pending';input_hashes_current=$false;full_encoded600s_review='pending';user_visual_verdict='pending'}) -Force
if (Test-Path -LiteralPath $taskProductionNativePath -PathType Leaf) {
    $taskProductionNative = Read-TaskJson $taskProductionNativePath
    $taskProductionNativeInputs = Test-TaskReportInputs $taskProductionNative
    $taskProductionNativeCurrent = $taskProductionNativeInputs.verified
    $taskManifest.animation | Add-Member -NotePropertyName production_attention_native_checks -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/native-validation-production600.json';report_sha256=(Get-TaskHash $taskProductionNativePath);status=$taskProductionNative.status;input_hashes_current=$taskProductionNativeCurrent;input_files_checked=$taskProductionNativeInputs.checked;stale_inputs=$taskProductionNativeInputs.stale;full_encoded600s_review='pending';user_visual_verdict='pending'}) -Force
}

$taskSemanticPath = Join-Path $taskSceneDirectory 'source-audit/correction-validation.json'
$taskSemanticCurrent = $false
$taskManifest.animation | Add-Member -NotePropertyName semantic_source_checks -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/source-audit/correction-validation.json';status='current fin/palette evidence pending';renderer_settings_current=$false}) -Force
if (Test-Path -LiteralPath $taskSemanticPath -PathType Leaf) {
    $taskSemantic = Read-TaskJson $taskSemanticPath
    $taskSemanticCurrent = $taskSemantic.status -eq 'passed' -and $taskSemantic.settings_sha256 -eq $taskSettingsHash -and $taskSemantic.renderer_sha256 -eq (Get-TaskHash (Join-Path $taskSceneDirectory 'render.py'))
    $taskManifest.animation | Add-Member -NotePropertyName semantic_source_checks -NotePropertyValue ([ordered]@{path='music/back-before-dawn-animation-v1/source-audit/correction-validation.json';report_sha256=(Get-TaskHash $taskSemanticPath);status=$taskSemantic.status;renderer_settings_current=$taskSemanticCurrent;scope='Dedicated small-fin rain guard and original-local-palette foliage checks; supplements broad allowed-mask protection.'}) -Force
}

$taskDeliveryPath = Join-Path $taskSceneDirectory 'delivery-validation.json'
$taskDelivered = $false
if (Test-Path -LiteralPath $taskDeliveryPath -PathType Leaf) {
    $taskDelivery = Read-TaskJson $taskDeliveryPath
    $taskDeliveryInputs = Test-TaskReportInputs $taskDelivery
    $taskMediaPath = [System.IO.Path]::GetFullPath((Join-Path $taskRepoDirectory $taskDelivery.path))
    if (-not $taskMediaPath.StartsWith($taskSceneDirectory + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Delivery media is outside the expected scene folder.'
    }
    $taskDelivered = $taskDelivery.status -eq 'technical_checks_passed_user_visual_review_pending' -and $taskDeliveryInputs.verified -and (Test-Path -LiteralPath $taskMediaPath -PathType Leaf)
    if ($taskDelivered) {
        $taskMediaInfo = Get-Item -LiteralPath $taskMediaPath
        $taskDelivered = (Get-TaskHash $taskMediaPath) -eq $taskDelivery.sha256 -and $taskMediaInfo.Length -eq $taskDelivery.bytes
    }
    if ($taskDelivered) {
        $taskManifest.status = 'Complete120s silent720p30 visual draft technically verified; user artistic review, full600s schedule review, audio and4K pending.'
        $taskManifest.animation.delivery = [ordered]@{status=$taskDelivery.status;path=$taskDelivery.path;sha256=$taskDelivery.sha256;bytes=$taskDelivery.bytes;seconds=$taskDelivery.seconds;fps=$taskDelivery.fps;decoded_frames=$taskDelivery.decoded_frames;validation='music/back-before-dawn-animation-v1/delivery-validation.json';validation_sha256=(Get-TaskHash $taskDeliveryPath);input_hashes_current=$true;user_visual_verdict='pending'}
    }
}

if (-not $taskDelivered) {
    $taskManifest.animation.delivery = [ordered]@{status=$(if($taskNativeCurrent){'native_checks_passed_encoded_review_pending'}else{'current native/encoded evidence pending'});sha256=$null;bytes=$null;validation=$null;user_visual_verdict='pending'}
}
Write-TaskJson $taskManifestPath $taskManifest

$taskReadme = [System.IO.File]::ReadAllText($taskReadmePath)
$taskStatusPattern = '(?s)<!-- delivery-status -->.*?<!-- /delivery-status -->'
$taskStatusText = if ($taskDelivered) {
    '<!-- delivery-status -->' + "`n" + 'Current delivery: [watch the120s visual draft](../../music/back-before-dawn-animation-v1/Back-Before-Dawn-v1-first-draft-120s.mp4). The complete encoded delivery and source checks passed against the current files. User full-speed artistic review, full600s schedule playback, audio and4K remain pending. [Technical evidence](../../music/back-before-dawn-animation-v1/delivery-validation.json).' + "`n" + '<!-- /delivery-status -->'
} elseif ($taskNativeCurrent) {
    '<!-- delivery-status -->' + "`n" + 'Current checkpoint: native source/protection/phase checks passed against the current input hashes; complete encoded-delivery review remains pending. [Native evidence](../../music/back-before-dawn-animation-v1/native-validation.json).' + "`n" + '<!-- /delivery-status -->'
} else {
    '<!-- delivery-status -->' + "`n" + 'Current checkpoint: implementation/settings are recorded; current native and complete encoded-delivery evidence remains pending.' + "`n" + '<!-- /delivery-status -->'
}
if ([regex]::IsMatch($taskReadme,$taskStatusPattern)) {
    $taskReadme = [regex]::Replace($taskReadme,$taskStatusPattern,[System.Text.RegularExpressions.MatchEvaluator]{param($taskMatch) $taskStatusText})
} else {
    $taskReadme = $taskReadme.Replace('## Current build', '## Current build' + "`n`n" + $taskStatusText)
}
if ($taskDelivered) {
    $taskReadme = $taskReadme.Replace('The first complete review is being built as a silent 120-second', 'The complete first review is a silent 120-second')
}
[System.IO.File]::WriteAllText($taskReadmePath,$taskReadme,$taskUtf8)
Write-TaskJson (Join-Path $PSScriptRoot 'documentation-sync.json') ([ordered]@{date='2026-11-05';settings_sha256=$taskSettingsHash;native_inputs_current=$taskNativeCurrent;production600_native_inputs_current=$taskProductionNativeCurrent;semantic_fin_palette_checks_current=$taskSemanticCurrent;encoded_delivery_verified=$taskDelivered;manifest_sha256=(Get-TaskHash $taskManifestPath);cue_sheet_sha256=(Get-TaskHash (Join-Path $PSScriptRoot 'cue-sheet.json'));user_visual_verdict='pending';production600_full_playback='pending'})
Write-Output "Scene18 docs refreshed: native evidence current=$taskNativeCurrent; encoded delivery verified=$taskDelivered."
