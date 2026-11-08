"""Restore the exact approved 600-second visual master from bounded LFS chunks.

Run after fetching the four exact LFS paths in visual/master-chunks.json.
Only a new file below exports/14-crater-rim-survey is created. An existing
correct master is verified; an existing different file is never overwritten.
No audio, final-hour render, source chunk or historical validation is changed.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile

B = Path(__file__).resolve().parent
R = B.parents[1]
MANIFEST_PATH = "music/crater-rim-final-hour-v1/visual/master-chunks.json"
MASTER_PATH = "exports/14-crater-rim-survey/production-v1/Crater-Rim-Survey-clean-600s-4K.mp4"
MASTER_BYTES = 3408440080
MASTER_SHA256 = "3bb88151f697bd2fbb93dde4b70737629d687df8856bef7c9259a23ff1f66ed8"
CHUNK_PREFIX = "music/crater-rim-final-hour-v1/visual/master-backup/"
MAX_CHUNK_BYTES = 1_000_000_000
BLOCK_BYTES = 4 * 1024 ** 2
FRAME_HASH_PATH = "music/crater-rim-final-hour-v1/assembly/evidence/master-frames.sha256"
FRAME_HASH_SHA256 = "e1c29d7779b61f7960b649a8682be566a19ef554b9373fa7860d264688bc71e2"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def safe_relative(value):
    require(isinstance(value, str) and value, "Empty/non-string repository path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and ":" not in value
            and path.as_posix() == value, "Unsafe/noncanonical repository path: " + value)
    return value


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(BLOCK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def validated_manifest(data):
    master = data["master"]
    require(safe_relative(master["path"]) == MASTER_PATH, "Unexpected master destination")
    require(master["bytes"] == MASTER_BYTES and master["sha256"] == MASTER_SHA256,
            "Manifest differs from the approved 600-second master fingerprint")
    chunks = data["chunks"]
    require(isinstance(chunks, list) and len(chunks) == 4, "Expected four bounded chunks")
    require(all(type(row["index"]) is int for row in chunks), "Chunk indices must be integers")
    chunks = sorted(chunks, key=lambda row: row["index"])
    indices = [row["index"] for row in chunks]
    require(indices in ([0, 1, 2, 3], [1, 2, 3, 4]), "Chunk indices must be consecutive")
    seen, offset = set(), 0
    for row in chunks:
        path = safe_relative(row["path"])
        require(path.startswith(CHUNK_PREFIX) and path not in seen,
                "Unexpected or duplicate chunk path: " + path)
        seen.add(path)
        require(type(row["bytes"]) is int and 0 < row["bytes"] <= MAX_CHUNK_BYTES,
                "Invalid/beyond-limit chunk size: " + path)
        require(isinstance(row["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]),
                "Invalid chunk SHA-256: " + path)
        if "offset" in row:
            require(row["offset"] == offset, "Noncontiguous chunk offset: " + path)
        offset += row["bytes"]
    require(offset == MASTER_BYTES, "Chunk sizes do not add up to approved master size")
    return master, chunks


def chunk_sources(chunks):
    root = R.resolve()
    sources = []
    for row in chunks:
        path = (R / row["path"]).resolve()
        require(path.is_relative_to(root), "Chunk path resolves outside repository")
        require(path.is_file() and path.stat().st_size == row["bytes"],
                "Chunk missing/wrong size (fetch the exact Git LFS path first): " + row["path"])
        sources.append((row, path))
    return sources


def stream_chunks(sources, destination=None):
    whole, count, checked = hashlib.sha256(), 0, []
    for row, path in sources:
        digest, size = hashlib.sha256(), 0
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(BLOCK_BYTES), b""):
                digest.update(block)
                whole.update(block)
                size += len(block)
                count += len(block)
                if destination is not None:
                    destination.write(block)
        require(size == row["bytes"] and digest.hexdigest() == row["sha256"],
                "Chunk fingerprint mismatch: " + row["path"])
        checked.append({"path": row["path"], "bytes": size, "sha256": digest.hexdigest()})
    require(count == MASTER_BYTES and whole.hexdigest() == MASTER_SHA256,
            "Concatenated bytes do not match the approved master")
    return checked


def portable_validation(target):
    """Rebase only the portable copy; retain the historical validation verbatim."""
    source = R / "music/crater-rim-final-hour-v1/visual/master-validation.json"
    evidence = (R / FRAME_HASH_PATH).resolve()
    require(evidence.is_relative_to(R.resolve()) and evidence.is_file()
            and sha(evidence) == FRAME_HASH_SHA256, "Saved complete master frame-hash evidence differs")
    source_bytes = source.read_bytes()
    data = json.loads(source_bytes)
    require(data["status"] == "passed" and data["sha256"] == MASTER_SHA256
            and data["bytes"] == MASTER_BYTES and data["seconds"] == 600
            and data["dimensions"] == [3840, 2160] and data["fps"] == 30,
            "Historical master validation contract differs")
    data.update({"file": str(target), "output": str(target),
                 "raw_frame_hashes": str(evidence), "decoded_framehash_file": str(evidence)})
    data["portable_restore_provenance"] = {
        "source_validation": source.relative_to(R).as_posix(),
        "source_validation_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "historical_validation_preserved": True,
        "master_bytes_verified_during_restore": True,
        "frame_hash_evidence": FRAME_HASH_PATH, "frame_hash_evidence_sha256": FRAME_HASH_SHA256,
        "new_decode_performed": False,
        "note": "Only file/output and frame-evidence paths rebased after exact master-byte verification. Original command, timings and other historical evidence retained."
    }
    receipt = target.parent / "restored-master-validation.json"
    encoded = (json.dumps(data, indent=2) + "\n").encode("utf-8")
    if receipt.exists():
        require(receipt.is_file() and receipt.read_bytes() == encoded,
                "Existing portable validation differs; preserved at " + str(receipt))
    else:
        with receipt.open("xb") as stream:
            stream.write(encoded)
    return str(receipt)


def restore(manifest_file, output=None, verify_only=False):
    master, chunks = validated_manifest(json.loads(Path(manifest_file).read_text(encoding="utf-8")))
    sources = chunk_sources(chunks)
    target = Path(output if output is not None else R / master["path"]).resolve()
    allowed = (R / "exports/14-crater-rim-survey").resolve()
    require(allowed.is_relative_to(R.resolve()) and target.is_relative_to(allowed)
            and target != allowed, "Output must remain below repository exports/14-crater-rim-survey")
    existing = target.exists()
    if existing:
        require(target.is_file() and target.stat().st_size == MASTER_BYTES
                and sha(target) == MASTER_SHA256,
                "Existing destination differs; preserve it and choose another --output path")
    if verify_only or existing:
        checked = stream_chunks(sources)
        result = {"status": "passed", "mode": "verify-only" if verify_only else "existing-master-verified",
                "output": str(target), "bytes": MASTER_BYTES, "sha256": MASTER_SHA256,
                "chunks": checked, "existing_master_verified": existing,
                "new_file_created": False, "originals_preserved": True}
        if not verify_only:
            result["portable_master_validation"] = portable_validation(target)
        return result

    target.parent.mkdir(parents=True, exist_ok=True)
    require(shutil.disk_usage(target.parent).free > MASTER_BYTES + 16 * 1024 ** 2,
            "Insufficient space to reconstruct the master")
    # A unique partial is retained on failure, never mistaken for a completed master.
    descriptor, temporary = tempfile.mkstemp(prefix=target.name + ".", suffix=".partial", dir=target.parent)
    partial = Path(temporary)
    with os.fdopen(descriptor, "wb") as destination:
        checked = stream_chunks(sources, destination)
        destination.flush()
        os.fsync(destination.fileno())
    require(partial.stat().st_size == MASTER_BYTES and sha(partial) == MASTER_SHA256,
            "Written partial failed independent complete-file verification; retained at " + str(partial))
    require(not target.exists(), "Destination appeared during restore; verified partial retained at " + str(partial))
    if os.name == "nt":
        # Windows rename fails rather than replacing a destination created by a race.
        os.rename(partial, target)
    else:
        # Hard-link creation supplies the same no-replace guarantee on POSIX.
        os.link(partial, target)
        partial.unlink()
    return {"status": "passed", "mode": "restored", "output": str(target),
            "bytes": MASTER_BYTES, "sha256": MASTER_SHA256, "chunks": checked,
            "existing_master_verified": False, "new_file_created": True, "originals_preserved": True,
            "written_file_independently_rehashed": True,
            "portable_master_validation": portable_validation(target)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=R / MANIFEST_PATH)
    parser.add_argument("--output", type=Path, help="Optional new destination below this repository's Crater Rim exports")
    parser.add_argument("--verify-only", action="store_true", help="Hash all chunks and their concatenation without creating a master")
    args = parser.parse_args()
    print(json.dumps(restore(args.manifest, args.output, args.verify_only), indent=2))


if __name__ == "__main__":
    main()
