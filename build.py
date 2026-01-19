#!/usr/bin/env python
"""
Cross-platform build script for Hospital PDF Manager.

Usage:
    python build.py                  # Build for current platform
    python build.py --platform windows  # Build for Windows
    python build.py --platform macos    # Build for macOS
    python build.py --clean             # Clean build artifacts
    python build.py --help              # Show help
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


class Builder:
    """Build Hospital PDF Manager executables."""

    def __init__(self, project_dir=None):
        """Initialize builder."""
        self.project_dir = Path(project_dir or Path(__file__).parent).resolve()
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        self.spec_file = self.project_dir / "homerpdf.spec"
        self.platform = sys.platform

    def print_header(self, text):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70 + "\n")

    def run_command(self, cmd, description, shell=False):
        """Run a command and handle errors."""
        print(f"[*] {description}...")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                shell=shell,
                check=True,
                capture_output=False,
            )
            print(f"[OK] {description} completed\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {description} failed with exit code {e.returncode}\n")
            return False
        except Exception as e:
            print(f"[ERROR] {description} failed: {str(e)}\n")
            return False

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        self.print_header("Checking Dependencies")

        # Map package names to import names (handle casing differences)
        required = {
            "PyInstaller": "pyinstaller",
            "PySide6": "pyside6",
            "pypdf": "pypdf",
            "reportlab": "reportlab"
        }
        missing = []

        for import_name, display_name in required.items():
            try:
                __import__(import_name)
                print(f"[OK] {display_name} is installed")
            except ImportError:
                print(f"[ERROR] {display_name} is not installed")
                missing.append(display_name)

        if missing:
            print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
            print("Install with: pip install -e '.[build]'")
            return False

        print("\n[OK] All dependencies are installed\n")
        return True

    def clean(self):
        """Clean build artifacts."""
        self.print_header("Cleaning Build Artifacts")

        dirs_to_remove = [self.dist_dir, self.build_dir]
        for directory in dirs_to_remove:
            if directory.exists():
                print(f"[*] Removing {directory}...")
                shutil.rmtree(directory)
                print(f"[OK] Removed {directory}")

        # Remove spec-generated files
        spec_build = self.project_dir / "Hospital PDF Manager"
        if spec_build.exists():
            shutil.rmtree(spec_build)
            print(f"[OK] Removed {spec_build}")

        print("\n[OK] Clean complete\n")

    def build(self, platform=None):
        """Build executable for specified platform."""
        if platform is None:
            platform = self.platform

        self.print_header(f"Building for {platform}")

        # Check dependencies first
        if not self.check_dependencies():
            return False

        # Run PyInstaller with spec file (no extra flags needed)
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            str(self.spec_file),
        ]

        if not self.run_command(cmd, "PyInstaller build"):
            return False

        # Platform-specific post-processing
        if platform == "darwin":
            return self._post_process_macos()
        elif platform == "win32":
            return self._post_process_windows()
        elif platform == "linux":
            return self._post_process_linux()

        return True

    def _post_process_windows(self):
        """Post-process Windows build."""
        self.print_header("Post-processing Windows Build")

        # Find the executable
        exe_path = self.dist_dir / "Hospital PDF Manager" / "Hospital PDF Manager.exe"
        if exe_path.exists():
            print(f"[OK] Found executable: {exe_path}")
            print(f"[OK] Executable size: {exe_path.stat().st_size / (1024 * 1024):.2f} MB\n")
            return True
        else:
            print(f"[ERROR] Executable not found at {exe_path}\n")
            return False

    def _post_process_macos(self):
        """Post-process macOS build."""
        self.print_header("Post-processing macOS Build")

        # Find the app bundle
        app_path = self.dist_dir / "Hospital PDF Manager.app"
        if app_path.exists():
            print(f"[OK] Found app bundle: {app_path}")
            exe_path = app_path / "Contents" / "MacOS" / "Hospital PDF Manager"
            if exe_path.exists():
                print(f"[OK] Found executable: {exe_path}")
                print(f"[OK] App bundle ready for distribution\n")
                return True
            else:
                print(f"[ERROR] Executable not found in app bundle\n")
                return False
        else:
            print(f"[ERROR] App bundle not found at {app_path}\n")
            return False

    def _post_process_linux(self):
        """Post-process Linux build."""
        self.print_header("Post-processing Linux Build")

        # Find the executable
        exe_path = self.dist_dir / "Hospital PDF Manager" / "Hospital PDF Manager"
        if exe_path.exists():
            print(f"[OK] Found executable: {exe_path}")
            # Make executable
            os.chmod(exe_path, 0o755)
            print(f"[OK] Made executable: {exe_path}\n")
            return True
        else:
            print(f"[ERROR] Executable not found at {exe_path}\n")
            return False

    def create_installer_info(self):
        """Create installer information file."""
        info_file = self.dist_dir / "BUILD_INFO.txt"
        with open(info_file, "w") as f:
            import platform
            f.write("Hospital PDF Manager Build Info\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Platform: {platform.system()}\n")
            f.write(f"Architecture: {platform.machine()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"PyInstaller: {self._get_pyinstaller_version()}\n")
            f.write(f"\nBuild Directory: {self.dist_dir}\n")

    def _get_pyinstaller_version(self):
        """Get PyInstaller version."""
        try:
            import PyInstaller
            return PyInstaller.__version__
        except:
            return "Unknown"

    def show_build_info(self):
        """Show build information."""
        self.print_header("Build Complete")

        if self.dist_dir.exists():
            print(f"Build artifacts location: {self.dist_dir}\n")

            # Show directory structure
            print("Contents:")
            for item in self.dist_dir.iterdir():
                if item.is_dir():
                    size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                    size_mb = size / (1024 * 1024)
                    print(f"  [DIR] {item.name}/ ({size_mb:.2f} MB)")
                else:
                    size = item.stat().st_size / (1024 * 1024)
                    print(f"  [FILE] {item.name} ({size:.2f} MB)")

            print(f"\n[OK] Build successful!\n")
        else:
            print("[ERROR] Build directory not found\n")

    def run(self, args):
        """Run the build process."""
        if args.clean:
            self.clean()
            if not args.build:
                return True

        if args.build:
            success = self.build(args.platform)
            if success:
                self.create_installer_info()
                self.show_build_info()
            return success

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Hospital PDF Manager executables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build for current platform
  python build.py --platform windows # Build for Windows x64
  python build.py --platform macos   # Build for macOS (Intel/Apple Silicon)
  python build.py --clean            # Clean build artifacts
  python build.py --clean --build    # Clean and rebuild
        """,
    )

    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux"],
        help="Target platform (defaults to current system)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        default=True,
        help="Build executable (default: True)",
    )

    args = parser.parse_args()

    # Map platform names to sys.platform values
    platform_map = {
        "windows": "win32",
        "macos": "darwin",
        "linux": "linux",
    }

    if args.platform:
        args.platform = platform_map[args.platform]

    builder = Builder()
    success = builder.run(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
