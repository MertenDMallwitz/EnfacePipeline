from pathlib import Path
import subprocess
import sys

from pathlib import Path
import subprocess

output_directory = r"C:\Users\50126825\Desktop\octa\Drusen_algorithmus\TEST_XML_4"
p = Path(output_directory).resolve()

result0 = subprocess.run(
    ['eyeseg', 'check'],
    cwd=r'C:\Users\50126825\Desktop\octa\Drusen_algorithmus\Neuer_Ordner',
    capture_output=False,
    text=True
)

result1 = subprocess.run(
    ['eyeseg', 'segment'],
    cwd=r'C:\Users\50126825\Desktop\octa\Drusen_algorithmus\Neuer_Ordner',
    capture_output=False,
    text=True
)

src = Path(str(p) + ".eye")
dst = Path(str(p) + ".OUTPUT.eye")

if not src.exists():
    print("Expected output not found:", src)
    sys.exit(1)

try:
    src.replace(dst)
    print(f"Renamed {src} -> {dst}")
except OSError as e:
    print("Rename failed:", e)
    sys.exit(1)

