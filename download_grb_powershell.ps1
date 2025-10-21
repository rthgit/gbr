# Download GRB files using PowerShell
Write-Host "==============================================="
Write-Host "DOWNLOAD TUTTI I GRB REALI FERMI LAT"
Write-Host "==============================================="

Write-Host "Scaricando GRB090902 (3972 fotoni)..."
Invoke-WebRequest -Uri "https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161615F357373F52_EV00.fits" -OutFile "L251020161615F357373F52_EV00.fits"

Write-Host "Scaricando GRB090510 (2371 fotoni)..."
Invoke-WebRequest -Uri "https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161912F357373F19_EV00.fits" -OutFile "L251020161912F357373F19_EV00.fits"

Write-Host "Scaricando GRB130427A (16 fotoni)..."
Invoke-WebRequest -Uri "https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020162012F357373F30_EV00.fits" -OutFile "L251020162012F357373F30_EV00.fits"

Write-Host "==============================================="
Write-Host "DOWNLOAD COMPLETATO!"
Write-Host "==============================================="

# Verifica file scaricati
Write-Host "Verifica file scaricati:"
$files = @(
    "L251020154246F357373F64_EV00.fits",
    "L251020161615F357373F52_EV00.fits",
    "L251020161912F357373F19_EV00.fits",
    "L251020162012F357373F30_EV00.fits"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "$file : OK ($([math]::Round($size/1024, 1)) KB)"
    } else {
        Write-Host "$file : MANCANTE"
    }
}

Write-Host "Premi un tasto per continuare..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
