#!/bin/bash

# Default values
BUILD_CPP=true
BUILD_PYTHON=true
BUILD_EXE=false
BUILD_TYPE="Release"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cpp)
            BUILD_CPP=false
            shift
            ;;
        --no-python)
            BUILD_PYTHON=false
            shift
            ;;
        --build-exe)
            BUILD_EXE=true
            shift
            ;;
        --build-type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Error handling
set -e

# Print step message
print_step() {
    echo -e "\n==> $1"
}

# Check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is not installed. Please install it first."
        exit 1
    fi
}

# Build C++ component
build_cpp() {
    print_step "Building C++ component..."
    
    # Create build directory if it doesn't exist
    mkdir -p build
    
    # Configure and build
    cd build
    cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE ..
    cmake --build . --config $BUILD_TYPE
    cd ..
}

# Setup Python environment
setup_python() {
    print_step "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    if [ "$BUILD_EXE" = true ]; then
        print_step "Installing PyInstaller..."
        pip install pyinstaller
    fi
}

# Build executable using PyInstaller
build_executable() {
    print_step "Building executable with PyInstaller..."
    
    # Activate virtual environment if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source .venv/bin/activate
    fi
    
    # Create spec file
    cat > LogViewer.spec << EOL
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/python/main.py'],
    pathex=[],
    binaries=[('build/Release/*.so', '.')],  # .so for Linux
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
    icon='src/resources/icon.ico'  # Add an icon if you have one
)
EOL
    
    # Build executable
    pyinstaller LogViewer.spec --clean
}

# Main execution
main() {
    if [ "$BUILD_CPP" = true ]; then
        check_command cmake
        build_cpp
    fi
    
    if [ "$BUILD_PYTHON" = true ]; then
        check_command python3
        setup_python
    fi
    
    if [ "$BUILD_EXE" = true ]; then
        build_executable
    fi
    
    echo -e "\nBuild completed successfully!"
}

main
