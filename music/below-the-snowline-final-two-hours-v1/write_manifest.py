"""Fingerprint final production records without archiving large media or caches."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
OMIT={'cache','verification-cache','masters','__pycache__'}
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
    return h.hexdigest()
def main():
    d=json.loads((H/'delivery-validation.json').read_text(encoding='utf-8'))
    assert d['status']=='passed' and (H/'record-update.json').exists()
    rows=[]
    for p in sorted(H.rglob('*')):
        rel=p.relative_to(H)
        if not p.is_file() or any(x in OMIT for x in rel.parts) or p.name=='production-manifest.json':continue
        rows.append({'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
    result={'status':'local production inventory','completed_date':d['completed_date'],'files':rows,'file_count':len(rows),'total_bytes':sum(x['bytes'] for x in rows),'final_delivery':{k:d[k] for k in ['output','bytes','sha256','seconds','frames']},'excluded_directories':sorted(OMIT),'media_and_sources':'Large final video, prepared audio and silent visual master are identified by their validation records. Original audio and approved scene remain at their existing locations.','remote_backup':False}
    (H/'production-manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'Local production inventory: {len(rows)} files, {result["total_bytes"]:,} bytes; no remote backup performed.')
if __name__=='__main__':main()
