"""Gain-only Snowline atmosphere revision; reuse exact wind/air source stems."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg

from build_snowline_radio_session import validate_audio, listening_copy


def encode_flac(source,target,db):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),
        '-af',f'volume={db:.15g}dB','-c:a','flac','-sample_fmt','s32',
        '-bits_per_raw_sample','24','-n',str(target)],capture_output=True,check=True)


def excerpt(source,target,gain_db):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),
        '-ss','54','-t','66','-af',f'volume={gain_db:.15g}dB',
        '-c:a','libmp3lame','-b:a','192k','-n',str(target)],capture_output=True,check=True)


def run(parent,out,wind_db=3.,vent_db=3.):
    if out.exists() and any(out.iterdir()):raise ValueError('Choose a new/empty directory.')
    r=json.loads((parent/'recipe.json').read_text(encoding='utf-8'))
    base=Path(r['parent_mix']['path'])
    wind=parent/'Snowline-exterior-wind-9min-v1.flac'
    vent=parent/'Snowline-ventilation-9min-v1.flac'
    for p in [wind,vent]:
        expected=next(x['sha256'] for x in r['outputs'] if x['file']==p.name)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Source stem changed.')
    if hashlib.sha256(base.read_bytes()).hexdigest()!=r['parent_mix']['sha256']:
        raise ValueError('Music/radio parent changed.')
    out.mkdir(parents=True,exist_ok=True)
    wind_out=out/'Snowline-exterior-wind-9min-v2.flac'
    vent_out=out/'Snowline-ventilation-9min-v2.flac'
    encode_flac(wind,wind_out,wind_db);encode_flac(vent,vent_out,vent_db)
    checks=[validate_audio(wind_out,540),validate_audio(vent_out,540)]
    mix=out/'Snowline-radio-wind-and-ventilation-9min-v2.flac'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(base),'-i',str(wind_out),'-i',str(vent_out),
        '-filter_complex','[0:a][1:a][2:a]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[a]',
        '-map','[a]','-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24','-n',str(mix)],capture_output=True,check=True)
    checks.append(validate_audio(mix,540))
    mp3=out/'Snowline-radio-wind-and-ventilation-9min-v2.mp3'
    metering=listening_copy(mix,mp3,out)
    checks.append(validate_audio(mp3,540))
    preview=out/'Snowline-environment-v2-plateau-check-66s.mp3'
    excerpt(mix,preview,metering['matching_passes'][-1]['gain_db'])
    checks.append(validate_audio(preview,66))
    old=out/'Snowline-environment-v1-plateau-check-66s.mp3'
    excerpt(parent/'Snowline-radio-wind-and-ventilation-9min-v1.flac',old,r['metering']['matching_passes'][-1]['gain_db'])
    checks.append(validate_audio(old,66))
    recipe={'date':'2026-11-02','user_feedback_verbatim':'Added atmosphere is too quiet',
        'change':'Raise both atmosphere stems3dB; preserve their ratio, source waveforms and timing',
        'wind_gain_change_db':wind_db,'ventilation_gain_change_db':vent_db,
        'effective_wind_gain_db':r['wind']['source_gain_db']+wind_db,
        'effective_ventilation_rms_dbfs':r['ventilation']['actual_rms_dbfs']+vent_db,
        'music_radio_parent':r['parent_mix'],'parent_environment_recipe':str((parent/'recipe.json').resolve()),
        'parent_environment_recipe_sha256':hashlib.sha256((parent/'recipe.json').read_bytes()).hexdigest(),
        'source_stems':[{'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [wind,vent]],
        'seconds':540,'sample_rate':48000,'outputs':checks,'metering':metering,
        'previews':{'recording_start_seconds':54,'duration_seconds':66,'new_and_baseline_same_source_window':True,
                    'each_uses_its_full_listening_copy_gain':True,'separately_normalized':False},
        'timing_filter_or_texture_changes':False,'new_generation_or_paid_service':False,
        'source_master_or_prior_version_modified':False,'assistant_listening':False,'user_v2_balance_review':'pending',
        'implementation':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
            [Path(__file__),Path(__file__).with_name('build_snowline_radio_session.py')]]}
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'output':str(out.resolve()),'files_checked':len(checks),'wind_increase_db':wind_db,
        'ventilation_increase_db':vent_db,'full_listening_lufs':metering['listening_copy']['integrated_lufs'],
        'full_listening_true_peak':metering['listening_copy']['true_peak_dbtp']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--wind-db',type=float,default=3);p.add_argument('--vent-db',type=float,default=3)
    a=p.parse_args();run(a.parent,a.out,a.wind_db,a.vent_db)
