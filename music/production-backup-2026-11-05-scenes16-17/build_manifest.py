"""Inventory the exact staged checkpoint plus existing source/music dependencies."""
from pathlib import Path
import hashlib
import json
import subprocess

B = Path(__file__).resolve().parent
R = B.parents[1]


def git(args):
    return subprocess.check_output(['git', *args], cwd=R)


def main():
    staged = git(['diff', '--cached', '--name-only', '-z']).decode('utf-8').strip('\0').split('\0')
    assert staged and git(['branch', '--show-current']).strip() == b'main'
    dependencies = ['final/16-cyberpunk-apartment/artwork-v3.png','creative/brainstorm/2026-10-27-three-worlds/e1-gate-camp/concept-v1.png']
    dependencies += ['EXPORTS.md', 'creative/ANIMATION_WORKFLOW.md', 'creative/NEXT_SCENE_RUNBOOK.md', 'creative/MUSIC_WORKFLOW.md']
    selection_path = (B/'selection.json').relative_to(R).as_posix()
    manifest_path = (B/'backup-manifest.json').relative_to(R).as_posix()
    paths = sorted(set(staged+dependencies+[selection_path, manifest_path]))
    assert all(paths) and all((R/p).is_file() for p in dependencies)
    selection = {'date': '2026-11-05', 'authority': 'User requests committing and pushing all scene16/17 drafts, assets and learnings.',
                 'branch': 'main', 'expected_scope': paths, 'source_dependencies_already_in_git': dependencies,
                 'policy': 'selection-policy.json', 'long_schedule_status': 'proposed, not implemented',
                 'full_length_media_included': False}
    (B/'selection.json').write_bytes((json.dumps(selection, indent=2)+'\n').encode('utf-8'))
    git(['add', '--', selection_path])
    rows = []
    for path in paths:
        if path == manifest_path:
            continue
        blob = git(['show', ':'+path])
        local = (R/path).read_bytes()
        lfs = blob.startswith(b'version https://git-lfs.github.com/spec/v1\n')
        row = {'path': path, 'bytes': len(local), 'sha256': hashlib.sha256(local).hexdigest(),
               'git_blob_bytes': len(blob), 'git_blob_sha256': hashlib.sha256(blob).hexdigest(),
               'storage': 'git-lfs' if lfs else 'ordinary-git', 'local_bytes_equal_git_blob': local == blob}
        if lfs:
            assert ('oid sha256:'+row['sha256']).encode() in blob and ('size '+str(len(local))).encode() in blob
        # Every native renderer/config/plan byte must survive a fresh checkout exactly.
        if path.startswith(('music/cyberpunk-apartment-animation-v4/','music/gate-camp-animation-v3/','music/scene-animation-core/','music/scene16-17-first-draft-assets/')) and not lfs:
            assert row['local_bytes_equal_git_blob'], path
        rows.append(row)
    output = {'date': '2026-11-05', 'branch': 'main', 'selection': selection_path,
              'manifest_self_excluded': True, 'files': rows,
              'lfs_media_bytes': sum(f['bytes'] for f in rows if f['storage'] == 'git-lfs'),
              'ordinary_git_bytes': sum(f['git_blob_bytes'] for f in rows if f['storage'] == 'ordinary-git')}
    (B/'backup-manifest.json').write_bytes((json.dumps(output, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'files': len(rows), 'lfs_bytes': output['lfs_media_bytes'],
                      'ordinary_git_bytes': output['ordinary_git_bytes']}), flush=True)


if __name__ == '__main__':
    main()
