"""
Build the desktop app into a Windows executable with PyInstaller.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAIN_SCRIPT = ROOT / "main.py"
APP_NAME = ROOT.name
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
REEXEC_FLAG = "PNSERVEX_BUILD_REEXEC"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package this project as a Windows exe.")
    parser.add_argument("--name", default=APP_NAME, help="Executable name. Default: project folder name.")
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Build a one-dir bundle instead of the default single-file executable.",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Show a console window while the GUI app runs.",
    )
    parser.add_argument("--icon", default="", help="Optional .ico file path.")
    return parser.parse_args()


def maybe_reexec_in_venv() -> None:
    if os.environ.get(REEXEC_FLAG) == "1":
        return

    if not VENV_PYTHON.is_file():
        return

    current_python = Path(sys.executable).resolve()
    venv_python = VENV_PYTHON.resolve()
    if current_python == venv_python:
        return

    env = os.environ.copy()
    env[REEXEC_FLAG] = "1"
    command = [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]]
    raise SystemExit(subprocess.call(command, cwd=ROOT, env=env))


def require_windows() -> None:
    if os.name != "nt":
        raise SystemExit("build.py currently targets Windows only.")


def require_pyinstaller():
    try:
        import PyInstaller.__main__ as pyinstaller_main
        from PyInstaller.utils.hooks import collect_all
    except ImportError as exc:
        python_exe = Path(sys.executable)
        install_cmd = f'"{python_exe}" -m pip install pyinstaller'
        raise SystemExit(
            "PyInstaller is not installed in the active environment.\n"
            f"Please run: {install_cmd}"
        ) from exc
    return pyinstaller_main, collect_all


def dedupe_pairs(values: list[tuple[str, str]]) -> list[tuple[str, str]]:
    unique: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def dedupe_strings(values: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def build_pyinstaller_args(
    name: str,
    onefile: bool,
    console: bool,
    icon: str,
    collect_all,
) -> list[str]:
    datas: list[tuple[str, str]] = []
    binaries: list[tuple[str, str]] = []
    hiddenimports: list[str] = [
        "serial.tools.list_ports",
        "openpyxl",
    ]

    for module_name in ("snap7.type", "snap7.types"):
        if importlib.util.find_spec(module_name) is not None:
            hiddenimports.append(module_name)

    for package_name, required in (
        ("snap7", True),
        ("pyqtgraph", True),
        ("Pinyin2Hanzi", False),
        ("serial", False),
    ):
        if importlib.util.find_spec(package_name) is None:
            if required:
                raise SystemExit(f"Required package not found for build: {package_name}")
            continue

        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package_name)
        datas.extend(pkg_datas)
        binaries.extend(pkg_binaries)
        hiddenimports.extend(pkg_hiddenimports)

    args = [
        str(MAIN_SCRIPT),
        "--noconfirm",
        "--clean",
        "--name",
        name,
        "--paths",
        str(ROOT),
        "--windowed" if not console else "--console",
        "--onefile" if onefile else "--onedir",
    ]

    if icon:
        args.extend(["--icon", str((ROOT / icon).resolve() if not Path(icon).is_absolute() else Path(icon))])

    for src, dest in dedupe_pairs(datas):
        args.append(f"--add-data={src}{os.pathsep}{dest}")

    for src, dest in dedupe_pairs(binaries):
        args.append(f"--add-binary={src}{os.pathsep}{dest}")

    for module_name in dedupe_strings(hiddenimports):
        args.extend(["--hidden-import", module_name])

    return args


def build_runtime_root(name: str, onefile: bool) -> Path:
    dist_dir = ROOT / "dist"
    return dist_dir if onefile else dist_dir / name


def seed_runtime_files(runtime_root: Path) -> None:
    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / "data").mkdir(parents=True, exist_ok=True)
    (runtime_root / "data" / "image").mkdir(parents=True, exist_ok=True)
    (runtime_root / "log").mkdir(parents=True, exist_ok=True)

    source_settings = ROOT / "data" / "local_settings.json"
    if source_settings.is_file():
        shutil.copy2(source_settings, runtime_root / "data" / "local_settings.json")

    source_db = ROOT / "gas_records.db"
    if source_db.is_file():
        shutil.copy2(source_db, runtime_root / "gas_records.db")


def main() -> None:
    require_windows()
    maybe_reexec_in_venv()
    args = parse_args()
    pyinstaller_main, collect_all = require_pyinstaller()
    onefile = not args.onedir

    pyinstaller_args = build_pyinstaller_args(
        name=args.name,
        onefile=onefile,
        console=args.console,
        icon=args.icon,
        collect_all=collect_all,
    )

    print(f"[build] Python: {sys.executable}")
    print(f"[build] Mode: {'onefile' if onefile else 'onedir'}")
    print(f"[build] Name: {args.name}")
    pyinstaller_main.run(pyinstaller_args)

    runtime_root = build_runtime_root(args.name, onefile)
    seed_runtime_files(runtime_root)

    exe_path = runtime_root / f"{args.name}.exe"
    print(f"[build] Output: {exe_path}")
    print(f"[build] Runtime data dir: {runtime_root / 'data'}")


if __name__ == "__main__":
    main()
