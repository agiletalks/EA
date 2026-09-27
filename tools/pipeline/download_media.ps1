$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$mediaDir = "c:\Antigravity\EA\media"
if (-not (Test-Path $mediaDir)) { New-Item -ItemType Directory -Path $mediaDir | Out-Null }

$videos = @(
    @{ Id = "D48TNltBiMM"; FileName = "Slide-016_VID-004_Daily-Life-is-Full-of-Hooks.mp4"; Title = "Daily Life is Full of Hooks" },
    @{ Id = "qjT0-DnExIQ"; FileName = "Slide-032_SOCVID-060_Why-We-Should-Stop-Calling-Human-Skills-Soft-Skills.mp4"; Title = "Why We Should Stop Calling Human Skills Soft Skills" },
    @{ Id = "NDQ1Mi5I4rg"; FileName = "TED-Talk_Full_The-Gift-and-Power-of-Emotional-Courage.mp4"; Title = "Susan David TED Talk Full" },
    @{ Id = "tD_zCS_Ps0w"; FileName = "Slide-058_AUD-002_A-Meditation-for-Self-Compassion.mp4"; Title = "A Meditation for Self-Compassion" },
    @{ Id = "CI9G3EBuIy0"; FileName = "Slide-064_SOCVID-109_How-to-Support-Others-During-Challenging-Times.mp4"; Title = "How to Support Others During Challenging Times" },
    @{ Id = "3FKD2EOL4qU"; FileName = "Slide-075_SOCVID-251_Learning-How-to-See-in-the-Dark.mp4"; Title = "Learning How to See in the Dark" },
    @{ Id = "crKzGzv5hS4"; FileName = "Slide-080_SOCVID-086_Naming-What-You-Feel.mp4"; Title = "Naming What You Feel" },
    @{ Id = "Pgb8I1n6tgA"; FileName = "Slide-071_SOCVID_Quick-Tips-for-Bottlers-and-Brooders.mp4"; Title = "Quick Tips for Bottlers and Brooders" },
    @{ Id = "FbDb2GHYZKo"; FileName = "Slide-154_SOCVID_How-to-Have-a-Difficult-Conversation.mp4"; Title = "How to Have a Difficult Conversation" }
)

Write-Output "Starting download of $($videos.Count) videos to $mediaDir..."

foreach ($v in $videos) {
    $outPath = Join-Path $mediaDir $v.FileName
    if (Test-Path $outPath) {
        Write-Output "Already exists: $($v.FileName)"
        continue
    }
    Write-Output "Downloading: $($v.Title) ($($v.Id)) -> $($v.FileName)..."
    & .\tools\yt-dlp.exe `
        --js-runtimes node:"C:\Program Files\nodejs\node.exe" `
        -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best" `
        --merge-output-format mp4 `
        -o $outPath `
        "https://www.youtube.com/watch?v=$($v.Id)"
}

# Now generate TED Talk segments from the full TED Talk
$tedFull = Join-Path $mediaDir "TED-Talk_Full_The-Gift-and-Power-of-Emotional-Courage.mp4"
if (Test-Path $tedFull) {
    Write-Output "Generating TED Talk lesson clips from full video..."
    $clips = @(
        @{ Out = "Slide-045_VID-001_TED-Talk-Part-1_Showing-Up.mp4"; Start = "00:00:00"; End = "00:10:38" },
        @{ Out = "Slide-088_VID-001_TED-Talk-Part-2_Stepping-Out.mp4"; Start = "00:10:39"; End = "00:13:59" },
        @{ Out = "Slide-149_VID-001_TED-Talk-Part-3_Walking-Your-Why.mp4"; Start = "00:14:00"; End = "00:15:06" },
        @{ Out = "Slide-179_VID-001_TED-Talk-Part-4_Moving-On.mp4"; Start = "00:15:07"; End = "00:16:47" }
    )
    
    foreach ($c in $clips) {
        $clipPath = Join-Path $mediaDir $c.Out
        if (-not (Test-Path $clipPath)) {
            Write-Output "Creating clip: $($c.Out) ($($c.Start) -> $($c.End))..."
            ffmpeg -y -i $tedFull -ss $c.Start -to $c.End -c copy $clipPath
        } else {
            Write-Output "Clip already exists: $($c.Out)"
        }
    }
}

Write-Output "All media tasks completed!"
Get-ChildItem -Path $mediaDir | Select-Object Name, Length
