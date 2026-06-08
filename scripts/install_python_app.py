#!/usr/bin/env python3
"""Install and run Dragon's Lair RPG with the Python already on this device.

This is the no-APK path. It can either use game files that are already on this
device or download the latest repo files from GitHub. Then it installs the
Python packages, writes a launcher, and starts `main.py`.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REPO_ZIP_URL = "https://github.com/Tboy450/Tboy450-new-rpg-update/archive/refs/heads/{branch}.zip"
DEFAULT_BRANCH = "main"
DEFAULT_FOLDER_NAME = "Tboy450-new-rpg-update-python"
ACTIVE_PATHS = (
    "README.md",
    "run_android.py",
    "main.py",
    "requirements.txt",
    "game_data",
    "systems",
    "assets",
    "scripts",
)


def is_windows() -> bool:
    return os.name == "nt"


def is_android_python() -> bool:
    markers = ("ANDROID_ROOT", "ANDROID_DATA", "ANDROID_STORAGE")
    return any(os.environ.get(name) for name in markers)


def documents_dir() -> Path:
    if is_windows():
        user_profile = Path(os.environ.get("USERPROFILE", str(Path.home())))
        for candidate in (
            Path(os.environ.get("OneDrive", "")) / "Documents",
            user_profile / "Documents",
        ):
            if str(candidate) and candidate.exists():
                return candidate
    return Path.home()


def default_install_dir() -> Path:
    if is_android_python():
        return Path.home() / DEFAULT_FOLDER_NAME
    return documents_dir() / DEFAULT_FOLDER_NAME


def run_checked(command: list[str], cwd: Path | None = None) -> None:
    printable = " ".join(command)
    print(f"\n> {printable}")
    subprocess.check_call(command, cwd=str(cwd) if cwd else None)


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def script_repo_root() -> Path:
    """Return the repo root when this script is being run from inside the repo."""
    try:
        return Path(__file__).resolve().parent.parent
    except NameError:
        return Path.cwd().resolve()


def copy_active_paths(source_dir: Path, install_dir: Path) -> None:
    """Copy only active game paths from one local folder to another."""
    source_dir = source_dir.resolve()
    install_dir = install_dir.resolve()

    if source_dir == install_dir:
        if not (install_dir / "main.py").exists():
            raise RuntimeError(f"Local game folder is missing main.py: {install_dir}")
        return

    install_dir.mkdir(parents=True, exist_ok=True)
    for relative_name in ACTIVE_PATHS:
        source = source_dir / relative_name
        target = install_dir / relative_name
        if not source.exists():
            continue
        remove_path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def download_repo(branch: str, install_dir: Path) -> None:
    url = REPO_ZIP_URL.format(branch=branch)
    install_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        zip_path = temp_dir / "repo.zip"
        print(f"Downloading game files from {url}")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(temp_dir)

        extracted_roots = [path for path in temp_dir.iterdir() if path.is_dir()]
        if not extracted_roots:
            raise RuntimeError("Downloaded archive did not contain a repository folder.")
        repo_root = extracted_roots[0]

        copy_active_paths(repo_root, install_dir)


def venv_python(install_dir: Path) -> Path:
    if is_windows():
        return install_dir / ".venv" / "Scripts" / "python.exe"
    return install_dir / ".venv" / "bin" / "python"


def ensure_python_environment(install_dir: Path, skip_packages: bool) -> Path:
    if is_android_python():
        # Android Python apps such as Pydroid already run inside their own
        # interpreter environment. Creating venvs there is unreliable.
        python_exe = Path(sys.executable)
    else:
        python_exe = venv_python(install_dir)
        if not python_exe.exists():
            print("Creating local Python environment...")
            run_checked([sys.executable, "-m", "venv", str(install_dir / ".venv")])

    if not skip_packages:
        requirements = install_dir / "requirements.txt"
        print("Installing game packages...")
        run_checked([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
        run_checked([str(python_exe), "-m", "pip", "install", "-r", str(requirements)])

    return python_exe


def write_launcher(install_dir: Path, python_exe: Path) -> Path:
    if is_windows():
        launcher = install_dir / "Run Dragons Lair RPG.cmd"
        launcher.write_text(
            "@echo off\n"
            "setlocal\n"
            f'"{python_exe}" "%~dp0main.py"\n'
            "if errorlevel 1 pause\n",
            encoding="ascii",
        )
        return launcher

    launcher = install_dir / "run-dragons-lair-rpg.sh"
    launcher.write_text(
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        f'cd "{install_dir}"\n'
        f'exec "{python_exe}" "main.py"\n',
        encoding="ascii",
    )
    launcher.chmod(0o755)
    return launcher


def launch_game(install_dir: Path, python_exe: Path) -> None:
    print("\nStarting Dragon's Lair RPG...")
    if is_android_python():
        # Pydroid initializes SDL/Pygame for the Python process it launches.
        # Starting a child `python main.py` process loses that display context,
        # causing pygame.display.set_mode() to fail. Execute main.py in this
        # same process instead.
        game_file = install_dir / "main.py"
        os.chdir(install_dir)
        sys.path.insert(0, str(install_dir))
        sys.argv = [str(game_file)]
        code = compile(game_file.read_text(encoding="utf-8"), str(game_file), "exec")
        exec(code, {"__name__": "__main__", "__file__": str(game_file)})
        return

    run_checked([str(python_exe), "main.py"], cwd=install_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install and run Dragon's Lair RPG.")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--install-dir", default="")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use the local repo files already on this device instead of downloading GitHub.",
    )
    parser.add_argument(
        "--source-dir",
        default="",
        help="Local source folder to copy from when --local is used.",
    )
    parser.add_argument("--no-run", action="store_true")
    parser.add_argument("--skip-packages", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve() if args.source_dir else script_repo_root()
    if args.local and not args.install_dir:
        install_dir = source_dir
    else:
        install_dir = Path(args.install_dir).expanduser() if args.install_dir else default_install_dir()
        install_dir = install_dir.resolve()

    print(f"Installing Dragon's Lair RPG to {install_dir}")
    print(f"Using Python: {sys.executable}")
    print(f"Platform: {platform.platform()}")

    if args.local:
        print(f"Using local game files from {source_dir}")
        copy_active_paths(source_dir, install_dir)
    else:
        download_repo(args.branch, install_dir)

    python_exe = ensure_python_environment(install_dir, args.skip_packages)
    launcher = write_launcher(install_dir, python_exe)

    print("\nDragon's Lair RPG is installed.")
    print(f"Launcher: {launcher}")

    if not args.no_run:
        launch_game(install_dir, python_exe)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
