# Compress any MP4 in media\ that exceeds 80MB so all files are well below GitHub 100MB limit
$ErrorActionPreference = "Stop"
$mediaFiles = Get-ChildItem "media\*.mp4" | Where-Object { $_.Length -gt 80MB }

foreach ($f in $mediaFiles) {
    $src = $f.FullName
    $tmp = "$($f.DirectoryName)\$($f.BaseName)_opt.mp4"
    $origSizeMB = [math]::Round($f.Length / 1MB, 2)
    Write-Host "Compressing $($f.Name) ($origSizeMB MB)..."
    
    # Scale to 1080p height max, high quality H.264 CRF 23, AAC 192k audio, faststart
    & ffmpeg -y -i $src -vf "scale=-2:'min(1080,ih)'" -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 192k -movflags +faststart $tmp
    
    if (Test-Path $tmp) {
        $newLen = (Get-Item $tmp).Length
        $newSizeMB = [math]::Round($newLen / 1MB, 2)
        Write-Host "Finished: $origSizeMB MB -> $newSizeMB MB"
        if ($newLen -gt 0 -and $newLen -lt $f.Length) {
            Remove-Item -Force $src
            Move-Item -Force $tmp $src
            Write-Host "Replaced $($f.Name) successfully!"
        } else {
            Remove-Item -Force $tmp
            Write-Warning "Optimized file was not smaller or failed."
        }
    }
}
Write-Host "All large video optimizations completed!"
