#!/usr/bin/env python3
"""usage: python3 make.py "<phrase>" [out_dir] [--sound]

Renders the 3.0 s newspaper highlight animation in 4K at 60 fps, reel and
YouTube orientations in parallel, then checks both files. --sound adds the
projector rattle. Works on macOS, Windows and Linux with Python 3.12+.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent


def ensure_python_312():
    """Re-run under a newer Python if this one is too old (macOS's built-in python3 is 3.9)."""
    if sys.version_info >= (3, 12):
        return
    for cmd in (["python3.14"], ["python3.13"], ["python3.12"], ["py", "-3.14"], ["py", "-3.13"], ["py", "-3.12"]):
        if shutil.which(cmd[0]):
            ok = subprocess.run(cmd + ["-c", "import sys; sys.exit(sys.version_info < (3, 12))"], capture_output=True)
            if ok.returncode == 0:
                sys.exit(subprocess.run(cmd + [str(Path(__file__).resolve())] + sys.argv[1:]).returncode)
    sys.exit("error: needs Python 3.12 or newer, from https://www.python.org/downloads/ (or `brew install python`)")


def env_python():
    """One shared environment per pinned dependency set, outside the skill folder so plugin
    updates don't wipe it."""
    req = HERE / "requirements.txt"
    base = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    env_dir = base / "newspaper-highlight-animation" / ("venv-" + hashlib.sha1(req.read_bytes()).hexdigest()[:8])
    py = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not py.exists():
        print(f"first run: installing dependencies into {env_dir} (about 250 MB, once)", file=sys.stderr)
        venv.create(env_dir, with_pip=True)
        if subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", str(req)]).returncode:
            shutil.rmtree(env_dir, ignore_errors=True)
            sys.exit("error: installing dependencies failed")
    return str(py)


def total_ram_gb():
    try:
        if os.name == "nt":
            import ctypes

            class MemoryStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + \
                           [(n, ctypes.c_ulonglong) for n in ("total", "avail", "pagetotal", "pageavail", "vtotal", "vavail", "extavail")]
            m = MemoryStatus(dwLength=ctypes.sizeof(MemoryStatus))
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.total / 2 ** 30
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2 ** 30
    except (AttributeError, OSError, ValueError):
        return 0.0


def check_imports(py):
    """Linux desktops ship the GL libraries Skia links against; minimal installs and containers may not."""
    r = subprocess.run([py, "-c", "import skia"], capture_output=True, text=True)
    if r.returncode:
        hint = ""
        if "libEGL" in r.stderr or "libGL" in r.stderr:
            hint = ("\nInstall the system graphics libraries, then run again:\n"
                    "  Debian/Ubuntu:  sudo apt install libegl1 libgl1\n"
                    "  Fedora:         sudo dnf install mesa-libEGL mesa-libGL\n"
                    "  Arch:           sudo pacman -S libglvnd")
        sys.exit("error: " + r.stderr.strip().splitlines()[-1] + hint)


def main():
    ensure_python_312()
    sound = "--sound" in sys.argv[1:]
    args = [a for a in sys.argv[1:] if a != "--sound"]
    if not args or not args[0].strip():
        sys.exit(__doc__)
    phrase = args[0]
    out = Path(args[1]).expanduser() if len(args) > 1 else Path.home() / "Downloads" / "newspaper-highlight-animation"
    py = env_python()
    check_imports(py)

    slug = re.sub(r"[^a-z0-9]+", "-", phrase.lower()).strip("-") or "phrase"
    out.mkdir(parents=True, exist_ok=True)
    jobs = [("reel", 2160, 3840), ("youtube", 3840, 2160)]
    files = {name: out / f"{slug}_{name}_{w}x{h}_60fps.mp4" for name, w, h in jobs}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")  # keep the skill folder clean
    cmds = [[py, str(HERE / "render.py"), phrase, str(w), str(h), "60", str(files[name])] + (["--sound"] if sound else [])
            for name, w, h in jobs]
    # Each 4K render peaks around 2 GB, so render both at once only when there is room for it.
    if total_ram_gb() >= 8:
        procs = [subprocess.Popen(c, env=env, stdout=subprocess.DEVNULL) for c in cmds]
        failed = any([p.wait() for p in procs])
    else:
        failed = any(subprocess.run(c, env=env, stdout=subprocess.DEVNULL).returncode for c in cmds)
    if failed:
        sys.exit("error: rendering failed")

    # Self-check: size, fps, frame count, duration, sound, plus a contact sheet per video to look at.
    sheets = Path(tempfile.gettempdir()) / "newspaper-highlight-animation"
    sheets.mkdir(exist_ok=True)
    for name, _, _ in jobs:
        subprocess.run([py, str(HERE / "check_video.py"), str(files[name]), str(sheets / f"{slug}_{name}_cards.png")],
                       env=env, check=True)
    for f in files.values():
        print(f"{f}  ({f.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
