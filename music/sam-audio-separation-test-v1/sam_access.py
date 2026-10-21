"""Browser sign-in and gated-model access check. No model or audio transfer."""
from pathlib import Path
import argparse,os,sys,json

ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parent/'.local'/'sam-audio-separation'
os.environ['HF_HOME']=str(CACHE/'hf-cache')
os.environ['HF_TOKEN_PATH']=str(CACHE/'hf-cache'/'token')
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['login','status','offline-check'])
    args=parser.parse_args()
    from huggingface_hub import login,get_token,get_hf_file_metadata,hf_hub_url
    if args.action=='offline-check':
        print('Hugging Face helper imports work.')
        print('Saved local sign-in present:',bool(get_token()))
        print('No token, account information, model or audio was transmitted.')
        return
    CACHE.mkdir(parents=True,exist_ok=True)
    if args.action=='login':
        print('Choose Log in with your browser. Complete the official Hugging Face page.')
        print('No password or access token needs to be shared in chat.')
        login(add_to_git_credential=False,skip_if_logged_in=True)
    if not get_token():
        print('No Hugging Face sign-in is saved for this test. Run sign-in.cmd first.')
        return 2
    results={}
    for repo in ['facebook/sam-audio-small','facebook/sam-audio-large']:
        try:
            meta=get_hf_file_metadata(hf_hub_url(repo,'config.json'),token=True)
            results[repo]={'access':'granted','config_commit':meta.commit_hash}
            print(repo+': access granted.')
        except Exception as exc:
            status=getattr(getattr(exc,'response',None),'status_code',None)
            results[repo]={'access':'not confirmed','error_type':type(exc).__name__,
                           'http_status':status}
            print(repo+': access not confirmed ('+type(exc).__name__+').')
            if status in (401,403):
                print('Open https://huggingface.co/'+repo+' in your browser and complete the access request.')
    record={'signed_in':True,'models':results,'model_downloaded':False,'audio_uploaded':False,
            'next_step':'Run a short, text-directed SAM Audio test after model access is confirmed.'}
    (ROOT/'access-status.json').write_text(json.dumps(record,indent=2))
    print('Status saved. Credentials remain in the ignored local cache, not in this report.')
    return 0 if results['facebook/sam-audio-small']['access']=='granted' else 3

if __name__=='__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nSign-in cancelled.')
        sys.exit(130)
    except Exception as exc:
        # Avoid dumping exception internals or authentication state to the UI.
        print('Could not complete sign-in/check ('+type(exc).__name__+').')
        print('No audio was uploaded. Retry sign-in.cmd after checking your connection.')
        sys.exit(1)
