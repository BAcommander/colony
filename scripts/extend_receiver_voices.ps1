param([Parameter(Mandatory=$true)][string]$Original, [Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$radioPoolOut = [IO.Path]::GetFullPath($Out)
$radioPoolOriginal = [IO.Path]::GetFullPath($Original)
if (Test-Path -LiteralPath $radioPoolOut) { throw 'Choose a new voice-pool directory.' }
[IO.Directory]::CreateDirectory($radioPoolOut) | Out-Null
$radioPoolRecord = [IO.File]::ReadAllText((Join-Path $radioPoolOriginal 'voice-sources.json')) | ConvertFrom-Json
$radioPoolResults = @()
foreach ($radioPoolItem in $radioPoolRecord.sources) {
    $radioPoolSource = Join-Path $radioPoolOriginal $radioPoolItem.file
    if ((Get-FileHash -LiteralPath $radioPoolSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $radioPoolItem.sha256) { throw 'Original voice source hash changed.' }
    Copy-Item -LiteralPath $radioPoolSource -Destination (Join-Path $radioPoolOut $radioPoolItem.file)
    $radioPoolResults += $radioPoolItem
}
$radioPoolPhrases = @(
    @{voice='Microsoft George'; rate=0; text='Shava nesh. Doran vela, sevan torak. Nesh valun.'},
    @{voice='Microsoft Hazel Desktop'; rate=1; text='Mera shovan. Kela nesh, tora van. Vesh dalun.'},
    @{voice='Microsoft George'; rate=-1; text='Kesh varena. Dalan shora, navik tal. Sovan nesh.'},
    @{voice='Microsoft Hazel Desktop'; rate=0; text='Talun vera, shen malok. Nara vesh. Sela tavan.'},
    @{voice='Microsoft George'; rate=1; text='Saro nesh, kelan voru. Sha daren. Nesh valok.'},
    @{voice='Microsoft Hazel Desktop'; rate=-1; text='Vena shalun. Meran tora, kesh valen. Shora ven.'},
    @{voice='Microsoft George'; rate=0; text='Daro shen. Velan kora, nesh tavi. Sovan taro.'},
    @{voice='Microsoft Hazel Desktop'; rate=1; text='Sha melun, vena torak. Kesh daren. Talo vesh.'}
)
$radioPoolFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
foreach ($radioPoolPhrase in $radioPoolPhrases) {
    $radioPoolName = 'voice-{0:d2}.wav' -f ($radioPoolResults.Count+1)
    $radioPoolPath = Join-Path $radioPoolOut $radioPoolName
    $radioPoolSynth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    try {
        $radioPoolSynth.SelectVoice($radioPoolPhrase.voice)
        $radioPoolSynth.Rate = $radioPoolPhrase.rate
        $radioPoolSynth.SetOutputToWaveFile($radioPoolPath, $radioPoolFormat)
        $radioPoolSynth.Speak($radioPoolPhrase.text)
    } finally { $radioPoolSynth.Dispose() }
    $radioPoolResults += @{file=$radioPoolName; voice=$radioPoolPhrase.voice; rate=$radioPoolPhrase.rate; text=$radioPoolPhrase.text; sha256=(Get-FileHash -LiteralPath $radioPoolPath -Algorithm SHA256).Hash.ToLowerInvariant()}
}
$radioPoolJson = @{source='Local Windows System.Speech installed voices'; words='Fourteen distinct invented phonetic phrases; no meaningful dialogue or franchise recordings'; paid_service=$false; sources=$radioPoolResults} | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText((Join-Path $radioPoolOut 'voice-sources.json'), $radioPoolJson, [Text.UTF8Encoding]::new($false))
Write-Output ('Prepared {0} distinct voice sources.' -f $radioPoolResults.Count)
