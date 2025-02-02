param(
    [switch]$BuildCpp = $true,
    [switch]$BuildPython = $true,
    [switch]$BuildExe = $false,
    [string]$BuildType = "Release"
)

# Error handling
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

# Check if cmake is installed
function Check-CMake {
    try {
        cmake --version | Out-Null
        return $true
    }
    catch {
        Write-Host "CMake is not installed. Please install CMake and add it to your PATH." -ForegroundColor Red
        exit 1
    }
}

# Check if Python is installed
function Check-Python {
    try {
        python --version | Out-Null
        return $true
    }
    catch {
        Write-Host "Python is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
        exit 1
    }
}

# Build C++ component
function Build-Cpp {
    Write-Step "Building C++ component..."
    
    # Create build directory if it doesn't exist
    if (-not (Test-Path "build")) {
        New-Item -ItemType Directory -Path "build" | Out-Null
    }
    
    # Configure and build
    Push-Location build
    try {
        cmake -DCMAKE_BUILD_TYPE=$BuildType ..
        cmake --build . --config $BuildType
        if ($LASTEXITCODE -ne 0) {
            throw "CMake build failed"
        }
    }
    finally {
        Pop-Location
    }
}

# Setup Python environment
function Setup-Python {
    Write-Step "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path ".venv")) {
        python -m venv .venv
    }
    
    # Activate virtual environment
    . .\.venv\Scripts\Activate.ps1
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    if ($BuildExe) {
        Write-Step "Installing PyInstaller..."
        pip install pyinstaller
    }
}

# Build executable using PyInstaller
function Build-Executable {
    Write-Step "Building executable with PyInstaller..."
    
    # Activate virtual environment if not already activated
    if (-not ($env:VIRTUAL_ENV)) {
        . .\.venv\Scripts\Activate.ps1
    }
    
    # Create spec file if it doesn't exist
    $specContent = @"
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/python/main.py'],
    pathex=[],
    binaries=[('build/Release/*.pyd', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LogViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/icon.ico'
)
"@
    
    Set-Content -Path "LogViewer.spec" -Value $specContent
    
    # Build executable
    pyinstaller LogViewer.spec --clean
}

# Main execution
try {
    if ($BuildCpp) {
        Check-CMake
        Build-Cpp
    }
    
    if ($BuildPython) {
        Check-Python
        Setup-Python
    }
    
    if ($BuildExe) {
        Build-Executable
    }
    
    Write-Host "`nBuild completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "`nBuild failed: $_" -ForegroundColor Red
    exit 1
}
