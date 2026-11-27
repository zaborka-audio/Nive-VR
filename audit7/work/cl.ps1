param([Parameter(Mandatory=$true)][string]$Src,[string]$RunArgs='')
$ErrorActionPreference='Stop'
$work='C:\Users\theli\Documents\Codex\ADAU1467+STM32\work'
$eq=Join-Path $work 'neve-vr-eq'
$msvcRoot=Join-Path $eq 'third_party/msvc-portable/msvc'
$vc=(Get-ChildItem -LiteralPath "$msvcRoot/VC/Tools/MSVC" -Directory | Sort-Object Name -Descending | Select-Object -First 1).FullName
$sdk=Join-Path $msvcRoot 'Windows Kits/10'
$sdkVersion=(Get-ChildItem -LiteralPath "$sdk/Include" -Directory | Sort-Object Name -Descending | Select-Object -First 1).Name
$env:PATH="$vc/bin/Hostx64/x64;$sdk/bin/$sdkVersion/x64;"+$env:PATH
$env:INCLUDE="$vc/include;$sdk/Include/$sdkVersion/ucrt;$sdk/Include/$sdkVersion/shared;$sdk/Include/$sdkVersion/um"
$env:LIB="$vc/lib/x64;$sdk/Lib/$sdkVersion/ucrt/x64;$sdk/Lib/$sdkVersion/um/x64"
$here=Split-Path $MyInvocation.MyCommand.Path -Parent
$out=Join-Path $here 'build'
New-Item -ItemType Directory -Force $out | Out-Null
$name=[IO.Path]::GetFileNameWithoutExtension($Src)
Push-Location $out
cl /nologo /O2 /std:c++17 /EHsc /I "$work/neve-vr-dyn/Source" /I "$work/neve-vr-eq/Source" /I "$work/neve-vr-channel/Source" (Join-Path $here $Src) "/Fe:$name.exe" "/Fo:$name.obj" | Out-Host
if($LASTEXITCODE -ne 0){Pop-Location;exit $LASTEXITCODE}
if($RunArgs){ & ".\$name.exe" $RunArgs.Split(' ') } else { & ".\$name.exe" }
$code=$LASTEXITCODE
Pop-Location
exit $code
