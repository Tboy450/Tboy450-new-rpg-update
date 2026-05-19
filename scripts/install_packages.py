import sys
import subprocess
import os
from importlib import util

# Core game development packages to install
GAME_DEV_PACKAGES = [
    "pygame",          # Main game engine
    "numpy",           # Fast math/arrays
    "pymunk",          # Physics engine
    "pyopengl",        # 3D graphics
    "pyaudio",         # Advanced audio
    "pillow",          # Image processing
    "noise",           # Perlin noise generation
    "pyinstaller",     # Game packaging
    "psutil",          # System monitoring
    "pytmx",           # Tiled map support
    "pyganim",         # Sprite animations
    "opensimplex",     # Better noise generation
    "matplotlib",      # Debug visualizations
    "sounddevice",     # Low-latency audio
    "moviepy",         # Cutscenes/video
    "numba",           # Performance optimization
    "pyperclip",       # Clipboard handling
    "screeninfo",      # Multi-monitor support
    "pyautogui",       # Input simulation
    "configparser"     # Config files
]

# Map pip package names to their import names for verification
PACKAGE_IMPORT_NAMES = {
    "pygame": "pygame",
    "numpy": "numpy",
    "pymunk": "pymunk",
    "pyopengl": "OpenGL",
    "pyaudio": "pyaudio",
    "pillow": "PIL",
    "noise": "noise",  # Requires C++ Build Tools if build fails
    "pyinstaller": "PyInstaller",
    "psutil": "psutil",
    "pytmx": "pytmx",
    "pyganim": "pyganim",
    "opensimplex": "opensimplex",
    "matplotlib": "matplotlib",
    "sounddevice": "sounddevice",
    "moviepy": "moviepy",
    "numba": "numba",
    "pyperclip": "pyperclip",
    "screeninfo": "screeninfo",
    "pyautogui": "pyautogui",
    "configparser": "configparser"
}

def install_packages():
    python_executable = sys.executable
    print(f"\n🔧 Setting up Python Game Dev Environment for {python_executable}")
    print(f"🐍 Python version: {sys.version.split()[0]}\n")
    
    # First upgrade pip
    print("🔄 Upgrading pip...")
    subprocess.call([python_executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install each package
    for package in GAME_DEV_PACKAGES:
        print(f"\n📦 Installing {package}...")
        try:
            subprocess.check_call([python_executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully!")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package}. Trying with --user flag...")
            try:
                subprocess.check_call([python_executable, "-m", "pip", "install", "--user", package])
                print(f"✅ {package} installed with --user flag!")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package} completely")
    
    # Verify installations
    print("\n🔍 Verifying installations...")
    for package in GAME_DEV_PACKAGES:
        import_name = PACKAGE_IMPORT_NAMES.get(package, package)
        try:
            if util.find_spec(import_name):
                print(f"✔️ {package} is available")
            else:
                print(f"❌ {package} NOT installed properly")
        except Exception as e:
            print(f"❌ {package} NOT installed properly: {e}")

def post_install_checks():
    print("\n🎮 Game Dev Setup Complete!")
    print("Recommended next steps:")
    print("1. Create a virtual environment: python -m venv game_dev")
    print("2. Activate it:")
    print("   - Windows: game_dev\\Scripts\\activate")
    print("   - Mac/Linux: source game_dev/bin/activate")
    print("3. Test PyGame: python -m pygame.examples.aliens")

if __name__ == "__main__":
    install_packages()
    post_install_checks()
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to exit...")