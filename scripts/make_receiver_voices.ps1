param([Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$receiverVoiceOut = [IO.Path]::GetFullPath($Out)
if (Test-Path -LiteralPath $receiverVoiceOut) {
    throw 'Choose a new voice-source directory.'
}
[IO.Directory]::CreateDirectory($receiverVoiceOut) | Out-Null
$receiverPhrases = @(
    @{voice='Microsoft George'; rate=0; text='Vesha nara, sovek talun. Kesh varo, nesh tavan.'},
    @{voice='Microsoft Hazel Desktop'; rate=0; text='Sha veran. Talo nesh, mena darok. Vesh taren.'},
    @{voice='Microsoft George'; rate=1; text='Nera. Kesh valun, shora ven. Daro sovek talan.'},
    @{voice='Microsoft Hazel Desktop'; rate=-1; text='Sova kesh. Vena shoran, tavi melun. Nesh varo.'},
    @{voice='Microsoft George'; rate=-1; text='Talan veresh, nora shan. Vesha valun.'},
    @{voice='Microsoft Hazel Desktop'; rate=1; text='Kora nesh, taven saro. Mena, sha vesh.'}
)
$receiverVoiceFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$receiverVoiceResults = @()
for ($receiverVoiceIndex=0; $receiverVoiceIndex -lt $receiverPhrases.Count; $receiverVoiceIndex++) {
    $receiverPhrase = $receiverPhrases[$receiverVoiceIndex]
    $receiverVoiceName = 'voice-{0:d2}.wav' -f ($receiverVoiceIndex+1)
    $receiverVoicePath = Join-Path $receiverVoiceOut $receiverVoiceName
    $receiverVoiceSynth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    try {
        $receiverVoiceSynth.SelectVoice($receiverPhrase.voice)
        $receiverVoiceSynth.Rate = $receiverPhrase.rate
        $receiverVoiceSynth.SetOutputToWaveFile($receiverVoicePath, $receiverVoiceFormat)
        $receiverVoiceSynth.Speak($receiverPhrase.text)
    } finally {
        $receiverVoiceSynth.Dispose()
    }
    $receiverVoiceResults += @{file=$receiverVoiceName; voice=$receiverPhrase.voice; rate=$receiverPhrase.rate; text=$receiverPhrase.text; sha256=(Get-FileHash -LiteralPath $receiverVoicePath -Algorithm SHA256).Hash.ToLowerInvariant()}
}
$receiverVoiceRecord = @{source='Local Windows System.Speech installed voices'; words='Invented phonetic phrases, no meaningful dialogue or franchise lines'; paid_service=$false; sources=$receiverVoiceResults}
$receiverVoiceJson = $receiverVoiceRecord | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText((Join-Path $receiverVoiceOut 'voice-sources.json'), $receiverVoiceJson, [Text.UTF8Encoding]::new($false))
$receiverVoiceJson
