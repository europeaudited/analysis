"""Cached raw data with checksums. Data files are *.csv; SOURCES.md is documentation and is not hashed.

Every piece keeps its raw files in <piece>/data/raw/ and a manifest at
<piece>/data/MANIFEST.sha256 in the format of `sha256sum`, paths relative to <piece>/data/.
Check from the shell with:  cd <piece>/data && sha256sum -c MANIFEST.sha256
"""
import hashlib
from pathlib import Path

import pandas as pd

MANIFEST = "MANIFEST.sha256"


class ChecksumError(RuntimeError):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_manifest(data_dir):
    """(Re)write the manifest for every file under <data_dir>/raw/."""
    data_dir = Path(data_dir)
    lines = []
    for p in sorted((data_dir / "raw").rglob("*.csv")):
        if p.is_file():
            lines.append(f"{sha256_file(p)}  {p.relative_to(data_dir).as_posix()}")
    (data_dir / MANIFEST).write_text("\n".join(lines) + "\n")
    return lines


def read_manifest(data_dir):
    out = {}
    mf = Path(data_dir) / MANIFEST
    if not mf.exists():
        raise ChecksumError(f"No manifest at {mf}")
    for line in mf.read_text().splitlines():
        if line.strip():
            digest, rel = line.split("  ", 1)
            out[rel.strip()] = digest.strip()
    return out


def verify(data_dir):
    """Raise ChecksumError if any listed file is missing or changed, or any raw file is unlisted."""
    data_dir = Path(data_dir)
    listed = read_manifest(data_dir)
    for rel, digest in listed.items():
        p = data_dir / rel
        if not p.exists():
            raise ChecksumError(f"Missing file listed in manifest: {rel}")
        if sha256_file(p) != digest:
            raise ChecksumError(f"Checksum mismatch: {rel}")
    on_disk = {p.relative_to(data_dir).as_posix() for p in (data_dir / "raw").rglob("*.csv") if p.is_file()}
    extra = on_disk - set(listed)
    if extra:
        raise ChecksumError(f"Files not in manifest: {sorted(extra)}")
    return True


def verified_path(path):
    """Verify the whole data folder that holds `path` (<data>/raw/<file>), return the path."""
    path = Path(path)
    verify(path.parent.parent)
    return path


def load_csv(path, **kwargs):
    """Verify checksums, then read a cached CSV."""
    return pd.read_csv(verified_path(path), **kwargs)
