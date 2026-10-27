# Private, bounded experiment. Parent workflow owns overall 20-minute timeout.
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$ProjectFolder,
  [Parameter(Mandatory)][string]$ExportFolder,
  [Parameter(Mandatory)][string]$EvidenceFolder,
  [switch]$InstallDesktop
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $EvidenceFolder | Out-Null
$EvidenceFolder = (Resolve-Path $EvidenceFolder).Path
Start-Transcript -Path (Join-Path $EvidenceFolder 'transcript.txt')
$beforePids = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue | ForEach-Object Id)
$stage = 'environment'
$result = [ordered]@{ status='incomplete'; stage=$stage; started=(Get-Date).ToUniversalTime().ToString('o'); desktopRefreshInvoked=$false; renderedValuesVerified=$false }
function Save-Result { $result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 (Join-Path $EvidenceFolder 'result.json') }

try {
  [ordered]@{ os=(Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber); user=[Security.Principal.WindowsIdentity]::GetCurrent().Name; sessionName=$env:SESSIONNAME; interactive=[Environment]::UserInteractive; runnerImage=$env:ImageOS; imageVersion=$env:ImageVersion } | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 (Join-Path $EvidenceFolder 'environment.json')
  query session 2>&1 | Out-File (Join-Path $EvidenceFolder 'sessions.txt')
  if ([Security.Principal.WindowsIdentity]::GetCurrent().IsSystem) { throw 'Desktop must not run as SYSTEM.' }
  $stage='prepare'; $result.stage=$stage; Save-Result
  $ProjectFolder=(Resolve-Path $ProjectFolder).Path
  $reportFolder=Join-Path $ProjectFolder 'AtlasPapeterie.Report'
  $ExportFolder=(Resolve-Path $ExportFolder).Path
  foreach($file in @('dim_product.csv','dim_shop.csv','dim_date.csv','fact_sales.csv','manifest.json')) { if(-not(Test-Path(Join-Path $ExportFolder $file))) { throw "Missing export $file" } }
  $parameterFile=Join-Path $ProjectFolder 'AtlasPapeterie.SemanticModel\definition\expressions.tmdl'
  $mPath=$ExportFolder.Replace('"','""').TrimEnd('\')
  $content=[IO.File]::ReadAllText($parameterFile)
  $content=[regex]::Replace($content,'(?m)^expression CSVFolder = .*$', 'expression CSVFolder = "'+$mPath+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]')
  [IO.File]::WriteAllText($parameterFile,$content,(New-Object Text.UTF8Encoding $false))
  $desktopExe=Join-Path $env:ProgramFiles 'Microsoft Power BI Desktop\bin\PBIDesktop.exe'
  if($InstallDesktop) {
    $stage='install'; $result.stage=$stage; Save-Result
    $installer=Join-Path $env:RUNNER_TEMP 'PBIDesktopSetup_x64.exe'
    Invoke-WebRequest 'https://download.microsoft.com/download/8/8/0/880bca75-79dd-466a-927d-1abf1f5454b0/PBIDesktopSetup_x64.exe' -OutFile $installer
    $sig=Get-AuthenticodeSignature $installer
    [ordered]@{ signatureStatus=$sig.Status.ToString(); signer=$sig.SignerCertificate.Subject; sha256=(Get-FileHash $installer -Algorithm SHA256).Hash } | ConvertTo-Json | Set-Content (Join-Path $EvidenceFolder 'installer-verification.json')
    if($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'Microsoft Corporation') { throw 'Official installer signature did not validate.' }
    $setupLog=Join-Path $EvidenceFolder 'install.log'
    $setup=Start-Process -FilePath $installer -ArgumentList @('-quiet','-norestart','LANGUAGE=en-US','ACCEPT_EULA=1',"-log$setupLog") -PassThru
    if(-not $setup.WaitForExit(540000)) { $setup.Kill(); throw 'Installer timed out after 9 minutes.' }
    $result.installerExitCode=$setup.ExitCode
    if($setup.ExitCode -ne 0) { throw "Installer exited $($setup.ExitCode); no reboot attempted." }
  }
  if(-not(Test-Path $desktopExe)) { throw 'Desktop executable not installed at the expected official location.' }
  $result.desktopVersion=(Get-Item $desktopExe).VersionInfo.FileVersion
  $stage='validator-and-bridge'; $result.stage=$stage; Save-Result
  $toolFolder=Join-Path $env:RUNNER_TEMP 'atlas-report-author'
  npm install --prefix $toolFolder '@microsoft/powerbi-report-authoring-cli@0.5.0' --no-audit --no-fund
  if($LASTEXITCODE -ne 0) { throw 'Official Report Author installation failed.' }
  $author=Join-Path $toolFolder 'node_modules\.bin\powerbi-report-author.cmd'
  & $author --version | Out-File (Join-Path $EvidenceFolder 'report-author-version.txt')
  & $author validate $ProjectFolder --format json | Tee-Object -FilePath (Join-Path $EvidenceFolder 'source-validation.json')
  if($LASTEXITCODE -ne 0) { throw 'Report source validation failed.' }
  # Recommended Report Author interface uses Desktop Bridge internally.
  & $author preview $reportFolder --host desktop --status | Tee-Object -FilePath (Join-Path $EvidenceFolder 'preview-status-before.json')
  $stage='open'; $result.stage=$stage; Save-Result
  & $author preview $reportFolder --host desktop | Tee-Object -FilePath (Join-Path $EvidenceFolder 'preview-open.json')
  if($LASTEXITCODE -ne 0) { throw 'Desktop preview open failed; no alternative CLI used to bypass it.' }
  $desktop=$null
  for($i=0;$i -lt 30;$i++) {
    $desktop=Get-Process PBIDesktop -ErrorAction SilentlyContinue | Where-Object { $_.Id -notin $beforePids -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if($desktop) { break }; Start-Sleep 2
  }
  if(-not $desktop) { throw 'No new Desktop GUI window within 60 seconds.' }
  $result.desktopPid=$desktop.Id
  # Metadata-only PBIP has no cache. No supported CLI data-refresh command is established.
  # Do not use TOM processing, UI input, remote desktop, or simulated screenshots here.
  $result.initialDataRefresh='not-established; inspect real Desktop render for empty visuals'
  $stage='capture'; $result.stage=$stage; Save-Result
  & $author preview $reportFolder --host desktop --screenshot (Join-Path $EvidenceFolder 'rapport.png') | Tee-Object -FilePath (Join-Path $EvidenceFolder 'preview-screenshot.json')
  if($LASTEXITCODE -ne 0) { throw 'Desktop rendering/capture failed.' }
  $result.status='capture-produced-initial-data-refresh-not-established'
} catch {
  $result.status='not-established'; $result.error=$_.Exception.Message
  Write-Host "Experiment stopped at ${stage}: $($_.Exception.Message)"
} finally {
  $result.stage=$stage; $result.finished=(Get-Date).ToUniversalTime().ToString('o'); Save-Result
  foreach($process in @(Get-Process PBIDesktop -ErrorAction SilentlyContinue | Where-Object { $_.Id -notin $beforePids })) {
    try { $null=$process.CloseMainWindow(); if(-not $process.WaitForExit(8000)) { Stop-Process -Id $process.Id -Force } } catch { Write-Host "Cleanup: $_" }
  }
  Stop-Transcript
}
