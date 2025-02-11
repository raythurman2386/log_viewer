# Log Viewer

A high-performance log file viewer built with Python and C++. Combines the ease of use of PyQt6 with the performance of C++ for file operations.

## Features

- **High Performance File Handling**
  - C++ backend for efficient file operations
  - Python fallback when C++ module is unavailable
  - Memory-efficient handling of large files
  - Smart caching of line positions

- **Real-time Monitoring**
  - Automatic detection of file changes
  - Directory monitoring for new log files
  - Handles file creation, modification, and deletion

- **Modern User Interface**
  - Multi-tab interface for viewing multiple logs
  - Monospace font for better readability
  - No line wrapping for log files
  - Maintains scroll position during updates

- **Error Handling**
  - Graceful fallback to Python implementation
  - Clear error messages
  - Robust file watching with proper cleanup

## Requirements

- Python 3.8 or higher
- PyQt6
- CMake 3.15 or higher
- C++ compiler with C++17 support
- pybind11 (installed via pip)
- watchdog

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/log_viewer.git
cd log_viewer
```

2. Use the automated build scripts:

### Windows (PowerShell):
```powershell
# Allow script execution if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Build C++ and setup Python environment
.\build.ps1

# Or build everything and create executable
.\build.ps1 -BuildExe

# Additional options:
.\build.ps1 -BuildCpp:$false    # Skip C++ build
.\build.ps1 -BuildPython:$false # Skip Python setup
.\build.ps1 -BuildType "Debug"  # Build in debug mode
```

### Linux/Mac:
```bash
# Give execution permission
chmod +x build.sh

# Build C++ and setup Python environment
./build.sh

# Or build everything and create executable
./build.sh --build-exe

# Additional options:
./build.sh --no-cpp         # Skip C++ build
./build.sh --no-python      # Skip Python setup
./build.sh --build-type Debug  # Build in debug mode
```

The build scripts will:
- Check for required dependencies (CMake, Python)
- Build the C++ component
- Set up a Python virtual environment
- Install required Python packages
- Optionally create a standalone executable

### Manual Installation:

If you prefer to install manually:

1. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Build the C++ module:
```bash
cmake -B build -S . -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

## Usage

### Running from Source:
```bash
python src/python/main.py
```

### Running the Executable:
After building with `-BuildExe` or `--build-exe`, find the standalone executable in the `dist` directory.

### Features:
- Open individual log files via File -> Open File
- Monitor directories for log files via File -> Open Directory
- Files are automatically refreshed when changes are detected
- New log files in monitored directories are automatically added
- Deleted files are automatically removed from the viewer

## Project Structure

```
log_viewer/
├── src/
│   ├── python/
│   │   ├── core/
│   │   │   ├── file_loader.py   # Python/C++ hybrid file loading
│   │   │   └── file_watcher.py  # File system monitoring
│   │   ├── gui/
│   │   │   └── main_window.py   # PyQt6 user interface
│   │   └── main.py             # Application entry point
│   └── cpp/
│       ├── file_loader/
│       │   ├── file_loader.hpp  # C++ file loading interface
│       │   └── file_loader.cpp  # C++ implementation
│       └── bindings/
│           └── bindings.cpp     # pybind11 bindings
├── CMakeLists.txt              # CMake build configuration
└── README.md
```

## Roadmap

The following features and improvements are planned for future releases:

- **Enhanced Log Formatting**
  - Improve log format detection and parsing
  - Add support for common log formats
  - Implement customizable format templates

- **Advanced Filtering and Search**
  - Real-time log filtering capabilities
  - Full-text search with regex support
  - Customizable highlighting rules

- **Cross-Platform Optimization**
  - Enhanced support for Linux and macOS
  - Platform-specific performance improvements
  - Native look and feel on each OS

- **Additional Tools and Features**
  - Log analysis tools
  - Statistical insights
  - Export and reporting capabilities
  - Customizable dashboards

## Development

- Python code is formatted using black
- C++ code follows modern C++17 practices
- Uses pybind11 for Python/C++ interop
- PyQt6 for the GUI components

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.