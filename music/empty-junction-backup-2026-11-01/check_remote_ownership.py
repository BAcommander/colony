"""Read-only destination ownership check; credentials are never logged or saved."""
from pathlib import Path
import subprocess,os,json,urllib.request
H=Path(__file__).resolve().parent;R=H.parents[1]
env=dict(os.environ,GCM_INTERACTIVE='Never',GIT_TERMINAL_PROMPT='0')
p=subprocess.run(['git','credential','fill'],cwd=R,input='protocol=https\nhost=github.com\n\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
if p.returncode:raise SystemExit('Existing non-interactive GitHub credential unavailable; no upload attempted.')
credential=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
token=credential.get('password');assert token,'No stored authentication available'
def get(path):
 request=urllib.request.Request('https://api.github.com/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'Ambient-Colony-backup-verification'})
 with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
user=get('user');repo=get('repos/BAcommander/colony')
result={'authenticated_login':user['login'],'repository':repo['full_name'],'owner':repo['owner']['login'],'private':repo['private'],'permissions':repo.get('permissions'),'authenticated_user_is_owner':user['login'].lower()==repo['owner']['login'].lower(),'remote':'https://github.com/BAcommander/colony.git','operation':'Read-only API check; no commit or upload'}
(H/'destination-ownership-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
