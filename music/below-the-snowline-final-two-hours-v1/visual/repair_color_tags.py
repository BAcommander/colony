"""Add absent transfer/primary H.264 VUI tags without changing any decoded picture."""
import json,subprocess,time
import production as p

def data(path):return [l for l in path.read_text().splitlines() if l and not l.startswith('#')]
def main():
    start=time.time();old=p.MASTER;fixed=p.CACHE/'master-color-tagged.mp4';retained=p.CACHE/'master-before-color-tags.mp4'
    for path in [old,fixed,retained]:assert path.resolve().is_relative_to(p.H.resolve())
    assert old.exists() and not fixed.exists() and not retained.exists()
    before=p.sha(old);cmd=[p.FF,'-v','error','-n','-i',str(old),'-map','0:v:0','-c','copy','-bsf:v','h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(fixed)]
    subprocess.run(cmd,check=True)
    hashes=[p.CACHE/'before-color-tags.framemd5',p.CACHE/'master-4K.framemd5']
    processes=[subprocess.Popen([p.FF,'-v','error','-n','-threads','4','-i',str(src),'-map','0:v:0','-an','-f','framemd5',str(dst)]) for src,dst in zip([old,fixed],hashes)]
    assert all(proc.wait()==0 for proc in processes)
    assert data(hashes[0])==data(hashes[1]) and len(data(hashes[0]))==3600
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=color_range,color_space,color_transfer,color_primaries','-of','json',str(fixed)]))['streams'][0]
    assert probe=={'color_range':'tv','color_space':'bt709','color_transfer':'bt709','color_primaries':'bt709'},probe
    old.rename(retained);fixed.rename(old)
    receipt=json.loads((p.H/'encode-receipt.json').read_text());receipt['before_color_tag_sha256']=before;receipt['sha256']=p.sha(old);receipt['bytes']=old.stat().st_size;receipt['metadata_repair']='metadata-repair.json';p.save('encode-receipt.json',receipt)
    p.save('metadata-repair.json',{'status':'passed','output':str(old),'before_sha256':before,'after_sha256':receipt['sha256'],'all_3600_decoded_pictures_and_timestamps_identical':True,'complete_decode_both_before_and_after':True,'color_metadata':probe,'master_framemd5_sha256':p.sha(hashes[1]),'command':cmd,'elapsed_seconds':time.time()-start,'retained_before_file':str(retained)})
    print('PASS: BT709 VUI tags repaired; all3600pictures andtimestamps unchanged',flush=True)

if __name__=='__main__':main()
