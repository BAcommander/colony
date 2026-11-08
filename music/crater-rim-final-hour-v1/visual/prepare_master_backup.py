"""Split the verified600s master into bounded, byte-exact LFS transport chunks."""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=HERE/'master-backup'
LIMIT=1_000_000_000

def main():
    checked=json.loads((HERE/'master-validation.json').read_text(encoding='utf-8'))
    assert checked['status']=='passed'
    master=Path(checked['output']);assert master.stat().st_size==checked['bytes']
    OUT.mkdir(exist_ok=True)
    assert not any(OUT.iterdir()),'Preserve existing master backup; verify instead of overwriting'
    digest=hashlib.sha256();rows=[]
    with master.open('rb') as source:
        for index in range((checked['bytes']+LIMIT-1)//LIMIT):
            target=OUT/f'Crater-Rim-Survey-clean-600s-4K.mp4.part{index+1:03d}'
            size=0;part=hashlib.sha256()
            with target.open('xb') as output:
                while size<LIMIT:
                    block=source.read(min(8*1024*1024,LIMIT-size))
                    if not block:break
                    output.write(block);part.update(block);digest.update(block);size+=len(block)
            rows.append({'index':index,'path':target.relative_to(ROOT).as_posix(),'bytes':size,'sha256':part.hexdigest()})
            print(f'Prepared exact master chunk {index+1}: {size:,} bytes',flush=True)
        assert not source.read(1)
    assert digest.hexdigest()==checked['sha256'] and sum(r['bytes'] for r in rows)==checked['bytes']
    # Re-read the stored chunks to prove the written ordered stream, not just inputs.
    restored=hashlib.sha256()
    for row in rows:
        part=hashlib.sha256()
        with (ROOT/row['path']).open('rb') as source:
            for block in iter(lambda:source.read(8*1024*1024),b''):part.update(block);restored.update(block)
        assert part.hexdigest()==row['sha256']
    assert restored.hexdigest()==checked['sha256']
    report={'status':'passed','method':'Raw ordered transport chunks; concatenation restores exact original MP4, no remux or transcode','master':{'path':master.relative_to(ROOT).as_posix(),'bytes':checked['bytes'],'sha256':checked['sha256'],'seconds':600,'dimensions':[3840,2160],'fps':30},'maximum_chunk_bytes':LIMIT,'chunks':rows,'all_written_chunks_reread':True,'ordered_written_stream_matches_master':True,'original_master_preserved':True}
    (HERE/'master-chunks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('All chunk bytes re-read; exact master reconstruction verified.',flush=True)

if __name__=='__main__':main()
