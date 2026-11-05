"""Freeze the current rendered review and native continuation controls."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('workshop_checkpoint_scene',HERE/'render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    scene=module.Scene();validation=json.loads((HERE/'delivery-validation.json').read_text())
    assert validation['status']=='technical_checks_passed_user_visual_review_pending'
    controls=[]
    for t in [0,16,27.55,60,80,94.35,119.9666666667]:controls.append({'absolute_seconds':t,'native_rgb_sha256':hashlib.sha256(scene.frame(t).tobytes()).hexdigest()})
    production=module.Scene('production600');production_controls=[]
    for t in [0,143.55,214,227,382,436.35,500,599.9666666667]:production_controls.append({'absolute_seconds':t,'native_rgb_sha256':hashlib.sha256(production.frame(t).tobytes()).hexdigest()})
    pkg={'date':'2026-11-05','user_artistic_review':'pending','source_dimensions':[1672,941],'review_mode':'review120','review_seconds':120,'environment_period_seconds':60,'production_attention_mode':'production600','production_attention_seconds':600,'production_status':'Implemented and native-audited; no full600s playback, production4K or long-session approval inferred.','input_hashes':scene.input_hashes(),'review_media':{'path':validation['path'],'sha256':validation['sha256'],'bytes':validation['bytes']},'native_review_controls':controls,'native_production_controls':production_controls,'schedule':scene.cfg['schedules'],'phase_rule':'Carry absolute attention time across chunks; only physical environmental fields wrap at60. Do not scale physical velocities by requested output duration.','opening_rule':'Keep this clean visual master free of opening/title/audio. Apply current Colony intro once at final assembly.','storage_rule':'Keep source assets/current short review/recipe; long upload and regenerable repeats/caches stay local under EXPORTS.md.'}
    (HERE/'continuation-checkpoint.json').write_text(json.dumps(pkg,indent=2)+'\n')
    print('Saved review and production-native continuation fingerprints')
if __name__=='__main__':main()
