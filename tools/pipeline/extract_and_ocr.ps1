Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Runtime.WindowsRuntime

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

[Windows.Globalization.Language,Windows.Foundation.Primitives,ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine,Windows.Foundation.Primitives,ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation.Primitives,ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile,Windows.Foundation.Primitives,ContentType=WindowsRuntime] | Out-Null

$lang = New-Object Windows.Globalization.Language("en-US")
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)

$zipPath = "EA Workshop Slides V2 - Percy Pofeng Hsu - EAC-C04-0061.pptx"
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)

$mediaDir = "slides_extracted"
if (-not (Test-Path $mediaDir)) { New-Item -ItemType Directory -Path $mediaDir | Out-Null }

$results = @()

for ($i = 1; $i -le 180; $i++) {
    $relEntry = $zip.Entries | Where-Object { $_.FullName -eq "ppt/slides/_rels/slide$i.xml.rels" }
    $mediaTarget = $null
    if ($relEntry) {
        $s = $relEntry.Open()
        $r = New-Object System.IO.StreamReader($s)
        $c = $r.ReadToEnd()
        $s.Close()
        if ($c -match 'Target="\.\./media/(image\d+\.[a-zA-Z]+)"') {
            $mediaTarget = $matches[1]
        }
    }
    
    $imagePath = $null
    if ($mediaTarget) {
        $imgEntry = $zip.Entries | Where-Object { $_.FullName -eq "ppt/media/$mediaTarget" }
        if ($imgEntry) {
            $imagePath = (Join-Path $mediaDir "slide_$($i.ToString('000')).png")
            if (-not (Test-Path $imagePath)) {
                [System.IO.Compression.ZipFileExtensions]::ExtractToFile($imgEntry, $imagePath, $true)
            }
        }
    }
    
    # OCR
    $ocrText = ""
    if ($imagePath -and (Test-Path $imagePath)) {
        try {
            $fullPath = [System.IO.Path]::GetFullPath($imagePath)
            $fileTask = [Windows.Storage.StorageFile]::GetFileFromPathAsync($fullPath)
            $file = Await $fileTask ([Windows.Storage.StorageFile])
            $streamTask = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read)
            $stream = Await $streamTask ([Windows.Storage.Streams.IRandomAccessStream])
            $decoderTask = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
            $decoder = Await $decoderTask ([Windows.Graphics.Imaging.BitmapDecoder])
            $bitmapTask = $decoder.GetSoftwareBitmapAsync()
            $bitmap = Await $bitmapTask ([Windows.Graphics.Imaging.SoftwareBitmap])
            $ocrTask = $engine.RecognizeAsync($bitmap)
            $ocrResult = Await $ocrTask ([Windows.Media.Ocr.OcrResult])
            $ocrText = ($ocrResult.Lines | ForEach-Object { $_.Text }) -join "`n"
            $stream.Dispose()
        } catch {
            $ocrText = "OCR_ERROR: $_"
        }
    }
    
    # Check notes
    $noteText = ""
    # find note rel
    $noteRel = $zip.Entries | Where-Object { $_.FullName -like "ppt/notesSlides/_rels/notesSlide*.xml.rels" }
    foreach ($nr in $noteRel) {
        $s = $nr.Open()
        $r = New-Object System.IO.StreamReader($s)
        $nc = $r.ReadToEnd()
        $s.Close()
        if ($nc -match "Target=`"\.\./slides/slide$i\.xml`"") {
            $noteBaseName = [System.IO.Path]::GetFileNameWithoutExtension($nr.FullName)
            $noteXmlName = "ppt/notesSlides/$noteBaseName.xml" -replace '\.rels$', ''
            $ne = $zip.Entries | Where-Object { $_.FullName -eq $noteXmlName }
            if ($ne) {
                $ns = $ne.Open()
                $nr2 = New-Object System.IO.StreamReader($ns)
                $nxml = $nr2.ReadToEnd()
                $ns.Close()
                $m = [regex]::Matches($nxml, '<a:t[^>]*>(.*?)</a:t>')
                $noteText = ($m | ForEach-Object { $_.Groups[1].Value.Trim() } | Where-Object { $_ -ne "" }) -join " "
            }
            break
        }
    }
    
    $results += [PSCustomObject]@{
        slideNumber = $i
        media = $mediaTarget
        ocrText = $ocrText
        notes = $noteText
    }
    
    if ($i % 20 -eq 0 -or $i -eq 180) {
        Write-Output "Processed $i / 180 slides..."
    }
}

$zip.Dispose()
$results | ConvertTo-Json -Depth 5 | Set-Content -Path "slides_summary.json" -Encoding UTF8
Write-Output "Saved slides_summary.json successfully!"
