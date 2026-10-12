"""Verify and reproduce the original published analysis without network access.

Usage: python run_reproduction.py
Requires Python 3.12 and the NumPy version in requirements.txt.
"""
from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA256 = "bf93862bd93b17bc5fdea74e1dae84024b96e0dfa33010e057e678afbf8a5ed2"
archive = HERE / "source_data.zip"
if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
    raise SystemExit("The original source archive has changed; verification stopped.")

copies = {
    "original_analysis.py": "analysis.py",
    "original_reproduce.py": "reproduce.py",
    "specification.json": "specification.json",
    "results.csv": "results.csv",
    "source_manifest.csv": "source_manifest.csv",
    "sources.csv": "sources.csv",
    "ORIGINAL_METHODS.txt": "README.txt",
    "flag_icons_LICENSE.txt": "flag_icons_LICENSE.txt",
}
with zipfile.ZipFile(archive) as z:
    for local_name, archived_name in copies.items():
        if (HERE / local_name).read_bytes() != z.read(archived_name):
            raise SystemExit(f"Readable copy differs from the original archive: {local_name}")
    with tempfile.TemporaryDirectory(prefix="reddit_activity_reproduction_") as work:
        root = Path(work).resolve()
        for member in z.infolist():
            target = (root / member.filename).resolve()
            if not target.is_relative_to(root):
                raise SystemExit("Archive contains an unsafe path.")
        z.extractall(root)
        completed = subprocess.run([sys.executable, str(root / "reproduce.py")], cwd=root)
        raise SystemExit(completed.returncode)
