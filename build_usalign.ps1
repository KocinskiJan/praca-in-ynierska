
# Prekompilacja USalign dla Windows
$usalignUrl = "https://zhanggroup.org/US-align/bin/module/USalign.cpp"
$usalignCpp = "USalign.cpp"
$usalignExe = "USalign.exe"

Write-Output "Pobieranie USalign.cpp..."
Invoke-WebRequest -Uri $usalignUrl -OutFile $usalignCpp

# Sprawdź czy g++ jest w PATH (musisz mieć zainstalowany np. MinGW)
$gpp = Get-Command g++ -ErrorAction SilentlyContinue
if (-not $gpp) {
    Write-Output "g++ nie znaleziono w PATH. Zainstaluj MinGW lub dodaj g++ do PATH."
    exit 1
}

# Kompilacja USalign
Write-Output "Kompilacja USalign..."
& g++ -O3 -ffast-math -o $usalignExe $usalignCpp

# Sprawdzenie czy USalign.exe istnieje
if (Test-Path -Path $usalignExe) {
    Write-Output "USalign został poprawnie skompilowany: $usalignExe"
    Remove-Item $usalignCpp
} else {
    Write-Output "Błąd podczas kompilacji USalign!"
    exit 1
}
