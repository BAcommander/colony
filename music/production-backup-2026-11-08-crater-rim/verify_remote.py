"""Verify the pushed Crater Rim checkpoint using fresh Git and LFS storage.

Run only after the checkpoint is committed and pushed on main. Verify all
selected Git blobs, existing restore dependencies and exact bounded master
chunks from remote objects. The complete master is hashed as a stream, without
writing another master or full-hour video. A durable local receipt precedes
cleanup of this run's unique successful restore scratch.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile

import restore_master

B = Path(__file__).resolve().parent
R = B.parents[1]
PREFIX = "crater-rim-final-2026-11-08-"
require = restore_master.require
validate_path = restore_master.safe_relative
sha = restore_master.sha


def git_environment():
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(name, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def git(args, cwd=R, data=None):
    result = subprocess.run(["git", "-c", "core.fsmonitor=false", *args], cwd=cwd, input=data,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=git_environment())
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace"))
    return result.stdout


def parse_pointer(data, path):
    lines = data.decode("ascii").splitlines()
    require(lines and lines[0] == "version https://git-lfs.github.com/spec/v1", "Not an LFS pointer: " + path)
    oids = [line[11:] for line in lines if line.startswith("oid sha256:")]
    sizes = [line[5:] for line in lines if line.startswith("size ")]
    require(len(oids) == 1 and re.fullmatch(r"[0-9a-f]{64}", oids[0])
            and len(sizes) == 1 and sizes[0].isdigit(), "Invalid LFS oid/size: " + path)
    return oids[0], int(sizes[0])


def remote_head():
    rows = git(["ls-remote", "origin", "refs/heads/main"]).decode().splitlines()
    require(len(rows) == 1 and len(rows[0].split()) == 2, "Expected exactly one remote main head")
    return rows[0].split()[0]


def write_receipt(path, receipt):
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main():
    manifest_file = B / "backup-manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    selection = json.loads((B / "selection.json").read_text(encoding="utf-8"))
    manifest_path = manifest_file.relative_to(R).as_posix()
    scope = [validate_path(path) for path in selection["expected_scope"]]
    dependencies = [validate_path(path) for path in selection.get("existing_restore_dependencies", [])]
    require(len(scope) == len(set(scope)) and len(dependencies) == len(set(dependencies)), "Duplicate selected paths")
    paths = sorted(set(scope) | set(dependencies))
    files = manifest["files"]
    manifest_paths = [validate_path(row["path"]) for row in files]
    require(len(manifest_paths) == len(set(manifest_paths)), "Duplicate manifest paths")
    require(manifest.get("self_excluded") == manifest_path, "Unexpected self-excluded manifest path")
    require(set(paths) == set(manifest_paths) | {manifest_path},
            "Scope plus restore dependencies must exactly equal manifest rows plus self-excluded manifest")
    require(restore_master.MANIFEST_PATH in paths, "Chunk manifest is outside verified scope")
    require(git(["branch", "--show-current"]).strip() == b"main", "Expected main")
    commit = git(["rev-parse", "HEAD"]).decode().strip()
    remote = git(["remote", "get-url", "origin"]).decode().strip()
    require(commit == remote_head(), "Local HEAD does not match remote main")

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
    require(git(["rev-parse", "FETCH_HEAD"], scratch).decode().strip() == commit, "Fetched commit mismatch")
    listing = git(["rev-list", "--objects", "--missing=print", commit, "--", *paths], scratch).decode()
    missing = sorted({line[1:].split()[0] for line in listing.splitlines() if line.startswith("?")})
    if missing:
        print(f"Fetching {len(missing)} selected Git blobs", flush=True)
        git(["-c", "fetch.negotiationAlgorithm=noop", "fetch", "--no-tags", "--no-write-fetch-head",
             "--filter=blob:none", "origin", "--stdin"], scratch, ("\n".join(missing) + "\n").encode())

    rows, pointers, objects, path_objects, chunk_data = [], {}, {}, {}, None
    for entry in files:
        path = entry["path"]
        require(entry["storage"] in ("git", "git-lfs"), "Unexpected storage: " + path)
        data = git(["cat-file", "blob", commit + ":" + path], scratch)
        require(len(data) == entry["git_blob_bytes"] and hashlib.sha256(data).hexdigest() == entry["git_blob_sha256"],
                "Remote Git blob mismatch: " + path)
        rows.append({"path": path, "git_blob_verified": True, "storage": entry["storage"],
                     "existing_restore_dependency": path in dependencies})
        if path == restore_master.MANIFEST_PATH:
            require(entry["storage"] == "git", "Chunk manifest must be a normal Git blob")
            chunk_data = json.loads(data)
        if entry["storage"] == "git-lfs":
            oid, size = parse_pointer(data, path)
            require(oid == entry["sha256"] and size == entry["bytes"], "LFS pointer disagrees with manifest: " + path)
            pointers[path] = data
            path_objects[path] = oid
            obj = objects.setdefault(oid, {"bytes": size, "paths": []})
            require(obj["bytes"] == size, "Conflicting sizes for shared LFS OID")
            obj["paths"].append(path)
    require(git(["cat-file", "blob", commit + ":" + manifest_path], scratch) == manifest_file.read_bytes(),
            "Self-excluded manifest differs remotely")
    master, chunks = restore_master.validated_manifest(chunk_data)
    for chunk in chunks:
        require(path_objects.get(chunk["path"]) == chunk["sha256"]
                and objects[chunk["sha256"]]["bytes"] == chunk["bytes"],
                "Master chunk is absent from verified LFS scope or differs: " + chunk["path"])

    print(f"Verified {len(rows)} Git blobs; downloading {len(objects)} unique LFS objects", flush=True)
    env = git_environment()
    env["GIT_LFS_SKIP_SMUDGE"] = "0"
    env.pop("GIT_LFS_SKIP_DOWNLOAD_ERRORS", None)
    for oid, obj in objects.items():
        path = obj["paths"][0]
        print("Downloading only " + path, flush=True)
        transfer = subprocess.run(["git", "-c", "lfs.fetchinclude=" + path, "-c", "lfs.fetchexclude=",
                                   "lfs", "smudge", path], cwd=scratch, input=pointers[path],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env)
        if transfer.returncode:
            raise RuntimeError(transfer.stderr.decode("utf-8", "replace"))
        restored = scratch / "private-lfs/objects" / oid[:2] / oid[2:4] / oid
        require(restored.is_file() and restored.stat().st_size == obj["bytes"] and sha(restored) == oid,
                "Fresh LFS object mismatch: " + path)
    # Every byte comes from independent remote LFS downloads, never the checkout's cache.
    sources = [(chunk, scratch / "private-lfs/objects" / chunk["sha256"][:2]
                / chunk["sha256"][2:4] / chunk["sha256"]) for chunk in chunks]
    checked_chunks = restore_master.stream_chunks(sources)
    lfs_rows = [{"path": path, "bytes": obj["bytes"], "sha256": oid, "fresh_remote_download_verified": True}
                for oid, obj in objects.items() for path in obj["paths"]]
    require(remote_head() == commit, "Remote main changed during verification")
    receipt = {
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "passed", "commit": commit, "branch": "main", "remote": remote,
        "remote_head_matches": True, "selected_paths": len(paths), "expected_scope_paths": len(scope),
        "existing_restore_dependency_paths": len(dependencies), "manifest_git_blobs_verified": len(rows),
        "self_excluded_manifest_verified": True, "fresh_lfs_objects_verified": len(objects),
        "fresh_lfs_paths_verified": len(lfs_rows),
        "fresh_lfs_bytes_verified": sum(obj["bytes"] for obj in objects.values()),
        "lfs": lfs_rows, "git_blobs": rows,
        "clean_master": {"path": master["path"], "bytes": restore_master.MASTER_BYTES,
                         "sha256": restore_master.MASTER_SHA256, "ordered_chunks": checked_chunks,
                         "fresh_remote_chunk_concatenation_verified": True, "complete_file_written": False},
        "new_branch_created": False, "full_length_exports_uploaded": False,
        "exact_600_second_master_archived_in_bounded_chunks": True,
        "unrelated_work_preserved": True, "independent_remote_object_restore": True,
        "lfs_download_method": "Exact verified remote pointers; one smudge per unique OID into fresh private storage; no whole-tree scan",
        "full_checkout_restore": False, "full_media_decode_or_listening": False,
        "scratch_path": str(scratch), "scratch_removed": False,
    }
    target = B / "remote-backup-verification.json"
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
                      "fresh_lfs_paths": len(lfs_rows), "fresh_lfs_objects": len(objects),
                      "fresh_lfs_bytes": receipt["fresh_lfs_bytes_verified"],
                      "clean_master_exact_sha256_verified": True, "scratch_removed": True}), flush=True)


if __name__ == "__main__":
    main()
