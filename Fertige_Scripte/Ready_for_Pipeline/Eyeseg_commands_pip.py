from pathlib import Path
import subprocess
import sys

from pathlib import Path
import subprocess
def eyeseg_commands_pip(output_directory):
    p = Path(output_directory).resolve()
    result0 = subprocess.run(
        ['eyeseg', 'check'],
        cwd=p,
        capture_output=False,
        text=True
    )

    result1 = subprocess.run(
        ['eyeseg', 'segment'],
        cwd=p,
        capture_output=False,
        text=True
    )

    src = Path(str(p) + "/processed/.eye")
    dst = Path(str(p) + "/processed/OUTPUT.eye")

    if not src.exists():
        print("Expected output not found:", src)
        sys.exit(1)

    try:
        src.replace(dst)
        print(f"Renamed {src} -> {dst}")
    except OSError as e:
        print("Rename failed:", e)
        sys.exit(1)