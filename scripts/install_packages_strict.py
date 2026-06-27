"""Install desktop game-development packages with stricter pip flags.

Beginner note:
    This is a desktop setup helper, not the game runtime and not the Android
    APK build list. It tries binary wheels or prerelease builds for packages
    that can be difficult to compile on newer Python versions.
"""

import sys
import subprocess
import os
from importlib import util

# Updated package list with alternatives and binary-only installs
GAME_DEV_PACKAGES = {
    # Core packages
    "pygame": "",
    "pymunk": "",
    "pyopengl": "--pre",  # Pre-release for Python 3.13 support
    "opensimplex": "",    # Alternative to noise
    
    # Audio
    "pyaudio": "",
    "sounddevice": "",
    
    # Graphics
    "pillow": "--only-binary :all:",
    "pytmx": "",
    "pyganim": "",
    
    # Utilities
    "pyinstaller": "--pre",
    "psutil": "",
    "matplotlib": "--only-binary :all:",
    "moviepy": "",
    "numba": "--only-binary :all:",
    "pyperclip": "",
    "screeninfo": "",
    "pyautogui": "",
    "configparser": ""
}

def install_packages():
    python_executable = sys.executable
    print(f"\n🔧 Setting up Python Game Dev Environment for {python_executable}")
    print(f"🐍 Python version: {sys.version.split()[0]}\n")
    
    # First upgrade pip and setuptools
    print("🔄 Upgrading pip and setuptools...")
    subprocess.call([python_executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    # Install each package with appropriate flags
    for package, flags in GAME_DEV_PACKAGES.items():
        print(f"\n📦 Installing {package}...")
        install_cmd = [python_executable, "-m", "pip", "install"]
        if flags:
            install_cmd.extend(flags.split())
        install_cmd.append(package)
        
        try:
            subprocess.check_call(install_cmd)
            print(f"✅ {package} installed successfully!")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package}. Trying with --user flag...")
            try:
                subprocess.check_call(install_cmd + ["--user"])
                print(f"✅ {package} installed with --user flag!")
            except subprocess.CalledProcessError:
                print(f"❌ Could not install {package}. You may need to:")
                print(f"   1. Install Visual Studio Build Tools")
                print(f"   2. Try: python -m pip install {package} --no-binary :all:")

def post_install_checks():
    print("\n✅ Essential Game Dev Setup Complete!")
    print("\nRecommended next steps:")
    print("1. Install Visual Studio Build Tools (for future packages):")
    print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("2. Create a virtual environment:")
    print("   python -m venv game_dev")
    print("3. Test PyGame:")
    print("   python -m pygame.examples.aliens")

if __name__ == "__main__":
    install_packages()
    post_install_checks()
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to exit...")
