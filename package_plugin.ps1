# FHDS Decky Plugin Packager
# Creates a zip file ready for Decky Loader installation (from URL or manual)

$src = "D:\ds_work\fhds-in-decky-loader"
$tmp = "D:\ds_work\fhds-decky"
$out = "D:\ds_work\fhds-decky-v0.1.0.zip"

if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
if (Test-Path $out) { Remove-Item -Force $out }

New-Item -ItemType Directory -Force -Path "$tmp\fhds-decky" | Out-Null

Write-Output "Copying files..."

Copy-Item "$src\plugin.json" "$tmp\fhds-decky\"
Copy-Item "$src\package.json" "$tmp\fhds-decky\"
Copy-Item "$src\main.py" "$tmp\fhds-decky\"
Copy-Item "$src\LICENSE" "$tmp\fhds-decky\"
Copy-Item "$src\README.md" "$tmp\fhds-decky\"
Copy-Item -Recurse "$src\dist" "$tmp\fhds-decky\"
Copy-Item -Recurse "$src\fhds_engine" "$tmp\fhds-decky\"
Copy-Item -Recurse "$src\defaults" "$tmp\fhds-decky\"
Copy-Item -Recurse "$src\py_modules" "$tmp\fhds-decky\"

Write-Output "Creating zip..."
Compress-Archive -Path "$tmp\fhds-decky" -DestinationPath $out

Remove-Item -Recurse -Force $tmp

Write-Output ""
Write-Output "Done!"
Get-Item $out | Select-Object Name, @{N='Size(KB)';E={[math]::Round($_.Length/1KB,1)}}
Write-Output ""
Write-Output "Install on Steam Deck:"
Write-Output "  Decky settings -> Install from URL -> file:///path/to/fhds-decky-v0.1.0.zip"
Write-Output "  Or extract to ~/homebrew/plugins/fhds-decky/"
