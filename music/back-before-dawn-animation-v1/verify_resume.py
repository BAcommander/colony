"""Check frozen native scene states before extending a reviewed workshop build."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    record=json.loads((HERE/'continuation-checkpoint.json').read_text())
    for path,expected in record['input_hashes'].items():assert digest(ROOT/path)==expected,path
    spec=importlib.util.spec_from_file_location('workshop_resume_scene',HERE/'render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for mode,key in [('review120','native_review_controls'),('production600','native_production_controls')]:
        scene=module.Scene(mode)
        for control in record[key]:assert hashlib.sha256(scene.frame(control['absolute_seconds']).tobytes()).hexdigest()==control['native_rgb_sha256'],(mode,control['absolute_seconds'])
    print(json.dumps({'status':'passed','inputs':len(record['input_hashes']),'native_states':len(record['native_review_controls'])+len(record['native_production_controls']),'approval':'pending'}))
if __name__=='__main__':main()
