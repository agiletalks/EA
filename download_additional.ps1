$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$mediaDir = "c:\Antigravity\EA\media"

$additionalVideos = @(
    @{ Slide = 55;  Code = "SOCVID-169";  Id = "bTkaqfY2b4s"; FileName = "Slide-055_SOCVID-169_You-Are-the-Sky.mp4"; Title = "You Are the Sky" },
    @{ Slide = 60;  Code = "SOCVID-090";  Id = "bQwwlzLnUxo"; FileName = "Slide-060_SOCVID-090_3-Steps-to-Show-Yourself-Compassion.mp4"; Title = "3 Steps to Show Yourself Compassion" },
    @{ Slide = 61;  Code = "SOCVID-281";  Id = "WMtlkHtA9No"; FileName = "Slide-061_SOCVID-281_The-Secret-to-Self-Compassion.mp4"; Title = "The Secret to Self-Compassion" },
    @{ Slide = 114; Code = "SOCVID-153";  Id = "oX6ElNm5c_k"; FileName = "Slide-114_SOCVID-153_What-the-Func.mp4"; Title = "What the Func" },
    @{ Slide = 126; Code = "SOCVID-264";  Id = "X090Pb060yE"; FileName = "Slide-126_SOCVID-264_Values-in-Conflict.mp4"; Title = "When values feel in conflict" },
    @{ Slide = 140; Code = "SOCVID-122";  Id = "tFuaPkfPddl"; FileName = "Slide-140_SOCVID-122_Moving-in-Direction-of-Values.mp4"; Title = "Am I moving in direction of my values" },
    @{ Slide = 169; Code = "SOCVID-170A"; Id = "MxXzfpzh3uU"; FileName = "Slide-169_SOCVID-170A_The-Four-Cs.mp4"; Title = "The Four Cs of Emotional Agility" }
)

Write-Output "Downloading 7 additional slide videos..."

foreach ($v in $additionalVideos) {
    $outPath = Join-Path $mediaDir $v.FileName
    if (Test-Path $outPath) {
        Write-Output "Already exists: $($v.FileName)"
        continue
    }
    Write-Output "Downloading Slide $($v.Slide): $($v.Title) ($($v.Id))..."
    & .\tools\yt-dlp.exe `
        --js-runtimes node:"C:\Program Files\nodejs\node.exe" `
        -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best" `
        --merge-output-format mp4 `
        -o $outPath `
        "https://www.youtube.com/watch?v=$($v.Id)"
}

Write-Output "All 7 additional videos downloaded!"
