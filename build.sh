#!/bin/bash

# Hospital PDF Manager - macOS/Linux Build Script
# Usage: ./build.sh [clean|rebuild|help]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Functions
print_header() {
    echo ""
    echo "========================================================================"
    echo "  $1"
    echo "========================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[*]${NC} $1"
}

show_help() {
    cat << 'EOF'

Hospital PDF Manager - macOS/Linux Build Script

Usage:
  ./build.sh              - Build executable
  ./build.sh clean        - Remove build artifacts
  ./build.sh rebuild      - Clean and rebuild
  ./build.sh help         - Show this help

Examples:
  ./build.sh rebuild      - Clean and build fresh executable

EOF
    exit 0
}

# Parse arguments
CLEAN_BUILD=0
for arg in "$@"; do
    case "$arg" in
        clean)
            CLEAN_BUILD=1
            ;;
        rebuild)
            CLEAN_BUILD=1
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown argument: $arg"
            show_help
            ;;
    esac
done

# Main build process
print_header "Hospital PDF Manager - Build for $(uname -s)"

# Check Python installation
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Found $PYTHON_VERSION"
echo ""

# Check dependencies
print_info "Checking dependencies..."
if ! python3 -m pip list 2>/dev/null | grep -q -i "pyinstaller"; then
    print_error "PyInstaller not installed"
    print_info "Installing build dependencies..."
    python3 -m pip install -e ".[build]" || exit 1
fi
print_success "Dependencies are installed"
echo ""

# Clean if requested
if [ "$CLEAN_BUILD" = "1" ]; then
    print_info "Cleaning build artifacts..."

    if [ -d "dist" ]; then
        rm -rf dist
        print_success "Removed dist/ directory"
    fi

    if [ -d "build" ]; then
        rm -rf build
        print_success "Removed build/ directory"
    fi

    if [ -d "Hospital PDF Manager" ]; then
        rm -rf "Hospital PDF Manager"
        print_success "Removed Hospital PDF Manager/ directory"
    fi

    # Remove __pycache__
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    echo ""
fi

# Build executable
print_info "Building executable with PyInstaller..."
if python3 -m PyInstaller --onedir homerpdf.spec; then
    print_success "Build completed"
else
    print_error "PyInstaller failed"
    exit 1
fi
echo ""

# Post-processing for macOS
if [ "$(uname)" = "Darwin" ]; then
    print_info "Post-processing macOS build..."

    # Check for app bundle
    if [ -d "dist/Hospital PDF Manager.app" ]; then
        print_success "Found app bundle: dist/Hospital PDF Manager.app"

        # Verify executable
        if [ -f "dist/Hospital PDF Manager.app/Contents/MacOS/Hospital PDF Manager" ]; then
            # Make it executable
            chmod +x "dist/Hospital PDF Manager.app/Contents/MacOS/Hospital PDF Manager"
            print_success "App bundle is ready"
            echo ""
        else
            print_error "Executable not found in app bundle"
            exit 1
        fi
    else
        print_error "App bundle not found"
        exit 1
    fi
fi

# Verify build
print_info "Verifying build..."
if [ "$(uname)" = "Darwin" ]; then
    if [ -f "dist/Hospital PDF Manager.app/Contents/MacOS/Hospital PDF Manager" ]; then
        EXE_SIZE=$(du -sh "dist/Hospital PDF Manager.app" | cut -f1)
        print_success "App bundle size: $EXE_SIZE"
    else
        print_error "Executable not found"
        exit 1
    fi
else
    if [ -f "dist/Hospital PDF Manager/Hospital PDF Manager" ]; then
        EXE_SIZE=$(du -sh "dist/Hospital PDF Manager" | cut -f1)
        print_success "Build size: $EXE_SIZE"
    else
        print_error "Executable not found"
        exit 1
    fi
fi
echo ""

# Show build info
print_header "Build Complete"

echo "Build location: $(pwd)/dist"
echo ""
echo "Contents:"
if [ "$(uname)" = "Darwin" ]; then
    ls -lh dist/
else
    du -sh dist/* 2>/dev/null || ls -lh dist/
fi
echo ""

if [ "$(uname)" = "Darwin" ]; then
    echo "To run the application:"
    echo "  open dist/Hospital\ PDF\ Manager.app"
    echo ""
    echo "Or execute directly:"
    echo "  dist/Hospital\ PDF\ Manager.app/Contents/MacOS/Hospital\ PDF\ Manager"
else
    echo "To run the application:"
    echo "  ./dist/Hospital\ PDF\ Manager/Hospital\ PDF\ Manager"
fi
echo ""

exit 0
