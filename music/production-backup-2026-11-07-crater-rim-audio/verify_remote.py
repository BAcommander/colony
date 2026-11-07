"""Verify the pushed audio checkpoint using independent Git/LFS object storage.

Run after the selected checkpoint is committed and pushed on main. Only the
fresh per-run restore scratch and this folder's ignored receipt are written.
No primary-checkout Git operation, media rebuild, render or listening is done.
"""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile

B = Path(__file__).resolve().parent
R = B.parents[1]
PREFIX = "crater-rim-audio-2026-11-07-"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git_environment():
    env = os.environ.copy()
    # Do not let a caller's alternate index/object/worktree override our cwd.
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(name, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def git(args, cwd=R, data=None):
    result = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", *args], cwd=cwd, input=data,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=git_environment())
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace"))
    return result.stdout


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 ** 2), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_path(value):
    require(isinstance(value, str) and value, "Empty/non-string selected path")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and ".." not in parsed.parts
            and "\\" not in value and ":" not in value
            and parsed.as_posix() == value, "Unsafe/noncanonical path: " + value)
    return value


def parse_pointer(data, path):
    lines = data.decode("ascii").splitlines()
    require(lines and lines[0] == "version https://git-lfs.github.com/spec/v1",
            "Not an LFS pointer: " + path)
    oids = [line[11:] for line in lines if line.startswith("oid sha256:")]
    sizes = [line[5:] for line in lines if line.startswith("size ")]
    require(len(oids) == 1 and re.fullmatch(r"[0-9a-f]{64}", oids[0])
            and len(sizes) == 1 and sizes[0].isdigit(),
            "Invalid LFS oid/size: " + path)
    return oids[0], int(sizes[0])


def write_receipt(path, receipt):
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main():
    manifest_file = B / "backup-manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    selection = json.loads((B / "selection.json").read_text(encoding="utf-8"))
    manifest_path = manifest_file.relative_to(R).as_posix()
    paths = [validate_path(path) for path in selection["expected_scope"]]
    files = manifest["files"]
    manifest_paths = [validate_path(row["path"]) for row in files]
    require(len(paths) == len(set(paths)), "Duplicate selection paths")
    require(len(manifest_paths) == len(set(manifest_paths)), "Duplicate manifest paths")
    require(manifest.get("self_excluded") == manifest_path,
            "Unexpected self-excluded manifest path")
    require(set(paths) == set(manifest_paths) | {manifest_path},
            "Selection must exactly equal manifest entries plus self-excluded manifest")
    require(git(["branch", "--show-current"]).strip() == b"main", "Expected main")
    commit = git(["rev-parse", "HEAD"]).decode().strip()
    remote = git(["remote", "get-url", "origin"]).decode().strip()
    head = git(["ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
    require(commit == head, "Local HEAD does not match remote main")

    root = (R / ".local/restore-scratch").resolve()
    require(root.is_relative_to(R.resolve()), "Restore scratch resolves outside repository")
    root.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=PREFIX, dir=root)).resolve()
    require(scratch.parent == root and scratch.name.startswith(PREFIX), "Unsafe scratch path")
    print("Fetching exact remote commit into " + str(scratch), flush=True)
    git(["init", "--bare", "--initial-branch=main", str(scratch)])
    git(["remote", "add", "origin", remote], scratch)
    git(["config", "remote.origin.promisor", "true"], scratch)
    git(["config", "remote.origin.partialclonefilter", "blob:none"], scratch)
    git(["config", "lfs.storage", str(scratch / "private-lfs")], scratch)
    git(["fetch", "--depth=1", "--filter=blob:none", "origin", commit], scratch)
    require(git(["rev-parse", "FETCH_HEAD"], scratch).decode().strip() == commit,
            "Fetched commit mismatch")
    listing = git(["rev-list", "--objects", "--missing=print", commit, "--", *paths], scratch).decode()
    missing = sorted({line[1:].split()[0] for line in listing.splitlines() if line.startswith("?")})
    if missing:
        print(f"Fetching {len(missing)} selected Git blobs", flush=True)
        git(["-c", "fetch.negotiationAlgorithm=noop", "fetch", "--no-tags",
             "--no-write-fetch-head", "--filter=blob:none", "origin", "--stdin"],
            scratch, ("\n".join(missing) + "\n").encode())

    rows, pointers, unique_objects = [], {}, {}
    for entry in files:
        path = entry["path"]
        require(entry["storage"] in ("git", "git-lfs"), "Unexpected storage: " + path)
        data = git(["cat-file", "blob", commit + ":" + path], scratch)
        require(len(data) == entry["git_blob_bytes"]
                and hashlib.sha256(data).hexdigest() == entry["git_blob_sha256"],
                "Remote Git blob mismatch: " + path)
        rows.append({"path": path, "git_blob_verified": True, "storage": entry["storage"]})
        if entry["storage"] == "git-lfs":
            oid, size = parse_pointer(data, path)
            require(oid == entry["sha256"] and size == entry["bytes"],
                    "LFS pointer disagrees with manifest: " + path)
            pointers[path] = data
            obj = unique_objects.setdefault(oid, {"bytes": size, "paths": []})
            require(obj["bytes"] == size, "Conflicting sizes for shared LFS OID")
            obj["paths"].append(path)

    # It cannot hash itself, so check the manifest's complete remote blob separately.
    require(git(["cat-file", "blob", commit + ":" + manifest_path], scratch)
            == manifest_file.read_bytes(), "Self-excluded manifest differs remotely")
    print(f"Verified {len(rows)} Git blobs; downloading {len(unique_objects)} unique LFS objects for {len(pointers)} paths", flush=True)
    env = git_environment()
    env["GIT_LFS_SKIP_SMUDGE"] = "0"
    env.pop("GIT_LFS_SKIP_DOWNLOAD_ERRORS", None)
    for oid, obj in unique_objects.items():
        path = obj["paths"][0]
        print("Downloading only " + path, flush=True)
        transfer = subprocess.run(
            ["git", "-c", "lfs.fetchinclude=" + path, "-c", "lfs.fetchexclude=",
             "lfs", "smudge", path], cwd=scratch, input=pointers[path],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env)
        if transfer.returncode:
            raise RuntimeError(transfer.stderr.decode("utf-8", "replace"))
        restored = scratch / "private-lfs/objects" / oid[:2] / oid[2:4] / oid
        require(restored.is_file() and restored.stat().st_size == obj["bytes"]
                and sha(restored) == oid, "Fresh LFS object mismatch: " + path)

    lfs_rows = [{"path": path, "bytes": obj["bytes"], "sha256": oid,
                 "fresh_remote_download_verified": True}
                for oid, obj in unique_objects.items() for path in obj["paths"]]
    final_head = git(["ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
    require(final_head == commit, "Remote main changed during verification")
    receipt = {
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "passed", "commit": commit, "branch": "main", "remote": remote,
        "remote_head_matches": True, "selected_paths": len(paths),
        "manifest_git_blobs_verified": len(rows), "self_excluded_manifest_verified": True,
        "fresh_lfs_objects_verified": len(unique_objects),
        "fresh_lfs_paths_verified": len(lfs_rows),
        "fresh_lfs_bytes_verified": sum(obj["bytes"] for obj in unique_objects.values()),
        "lfs": lfs_rows, "git_blobs": rows,
        "new_branch_created": False, "full_length_exports_uploaded": False,
        "unrelated_work_preserved": True, "independent_remote_object_restore": True,
        "lfs_download_method": "Exact verified remote pointers; one smudge per unique OID into fresh private storage; no whole-tree scan",
        "full_checkout_restore": False, "full_media_decode_or_listening": False,
        "scratch_path": str(scratch), "scratch_removed": False,
    }
    target = B / "remote-backup-verification.json"
    # Save durable evidence outside scratch before deleting only this successful run.
    write_receipt(target, receipt)
    require(scratch.resolve().parent == root and scratch.name.startswith(PREFIX)
            and scratch != R.resolve() and not scratch.is_symlink(), "Unsafe cleanup target")

    def remove_readonly(function, path, exception):
        require(Path(path).resolve().is_relative_to(scratch), "Cleanup target escaped scratch")
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        function(path)

    shutil.rmtree(scratch, onerror=remove_readonly)
    require(not scratch.exists(), "Verified scratch cleanup incomplete")
    receipt["scratch_removed"] = True
    write_receipt(target, receipt)
    print(json.dumps({"status": "passed", "commit": commit, "git_files": len(paths),
                      "fresh_lfs_files": len(lfs_rows), "fresh_lfs_objects": len(unique_objects),
                      "fresh_lfs_bytes": receipt["fresh_lfs_bytes_verified"],
                      "scratch_removed": True}), flush=True)


if __name__ == "__main__":
    main()
