"""SmartDialer Server Launcher: Auto-detects free port, opens browser, and runs Uvicorn."""

import os
import sys
import socket
import webbrowser
import threading
import time
from pathlib import Path


def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a TCP port is open and bindable."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(preferred_ports=(8001, 8000, 8080, 5000)) -> int:
    """Find the first available port among preferred ports (defaulting to 8001)."""
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            p = int(env_port)
            if is_port_free(p):
                return p
        except ValueError:
            pass

    for p in preferred_ports:
        if is_port_free(p):
            return p

    # Fallback: let OS assign an ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def open_browser_delayed(url: str, delay: float = 1.2):
    """Open browser after a brief delay so server has time to bind."""
    time.sleep(delay)
    print(f"\n[SmartDialer] Opening live dashboard in your default browser: {url}\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # Ensure paths are added to sys.path and PYTHONPATH for uvicorn reloader subprocess
    project_dir = Path(__file__).resolve().parent
    inner_dir = project_dir / "smart_dialer"

    search_dirs = []
    if (inner_dir / "smart_dialer").is_dir():
        search_dirs.append(str(inner_dir))
    if (project_dir / "smart_dialer").is_dir():
        search_dirs.append(str(project_dir))
    search_dirs.append(str(project_dir))

    for d in search_dirs:
        if d not in sys.path:
            sys.path.insert(0, d)

    cur_pypath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = os.pathsep.join(search_dirs + ([cur_pypath] if cur_pypath else []))

    port = find_available_port([8001, 8000, 8080, 5000])
    host = "127.0.0.1"
    url = f"http://{host}:{port}/"

    print("=" * 65)
    print(" SmartDialer Telephony Operations Engine")
    print(f" Live Dashboard:           {url}")
    print(f" Interactive Swagger UI:   {url}docs")
    print(f" Live Health Probe:        {url}health")
    print(f" Live Telephony Metrics:   {url}metrics")
    print("=" * 65)

    # Launch browser in a background thread
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    # Run Uvicorn
    import uvicorn
    uvicorn.run("smart_dialer.api.app:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
