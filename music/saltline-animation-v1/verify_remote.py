"""Independent partial clone, exact remote Git-object verification, no media checkout."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
def git(*args,cwd=R):return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.PIPE)
url=git('remote','get-url','origin').decode().strip();expected=git('rev-parse','HEAD').decode().strip()
temp_base=Path(tempfile.gettempdir()).resolve();temp=Path(tempfile.mkdtemp(prefix='saltline-remote-verify-')).resolve()
assert temp.is_relative_to(temp_base) and temp.name.startswith('saltline-remote-verify-')
try:
 subprocess.run(['git','clone','--bare','--depth','1','--filter=blob:none','--single-branch','--branch','main',url,str(temp/'repo.git')],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 repo=temp/'repo.git';head=git('rev-parse','HEAD',cwd=repo).decode().strip();assert head==expected,(head,expected)
 approval=json.loads(git('show','HEAD:music/saltline-animation-v1/approved-v5-preview.json',cwd=repo))
 files={approval['preview_path']:approval['preview_sha256'],'music/saltline-animation-v1/scene-plan-v5.json':approval['config_sha256'],'music/saltline-animation-v1/render_saltline.py':approval['renderer_sha256'],'music/saltline-animation-v1/dust_transport.py':approval['dependencies_sha256']['dust_transport.py'],'final/05-saltline-receiver/artwork-v2-animation.png':approval['source_sha256']}
 files.update({v['snapshot_path']:v['sha256'] for v in approval['exact_dependency_snapshots'].values()})
 for p,sha in files.items():
  restored=git('show','HEAD:'+p,cwd=repo);assert hashlib.sha256(restored).hexdigest()==sha,p
 print(json.dumps({'remote_head':head,'independent_remote_clone':True,'verified_hash_objects':len(files),'accepted_preview_sha256':approval['preview_sha256'],'preview_bytes':len(git('show','HEAD:'+approval['preview_path'],cwd=repo)),'source_config_renderer_dependencies_and_preview_verified':True},indent=2))
finally:
 assert temp.is_relative_to(temp_base) and temp.name.startswith('saltline-remote-verify-')
 shutil.rmtree(temp)
