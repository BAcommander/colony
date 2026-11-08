"""Guarded current-record update AFTER completed Crater Rim delivery.

Prepare/review with no arguments; write only with --apply. Never runs rendering,
Git, publication or generation. Requires the real final file and independently
bound audit records, preserves exact before-bytes, and changes scene14 only.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCENE = ROOT/'final/14-crater-rim-survey'
ASSEMBLY = PACKAGE/'assembly'
FINAL = ROOT/'exports/14-crater-rim-survey/Crater-Rim-Survey-1-Hour-4K-v1.mp4'
SOURCE_AUDIO = ROOT/'exports/14-crater-rim-survey/audio-1h-v1/Crater-Rim-Survey-1-Hour-music-and-SFX-v1.flac'
APPROVED_AUDIO_SHA = '333c0fe1b94ac899d0fa6a91ed009c693de312c791913a838662bf7433b5c994'
MARKER = 'crater-rim-final-hour-v1-current'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def checked_media(path, size, expected_hash):
    path = Path(path).resolve()
    before = path.stat()
    require(before.st_size == size, 'Media size changed: '+str(path))
    require(sha(path) == expected_hash, 'Media hash mismatch: '+str(path))
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            'Media changed during hashing: '+str(path))
    return {'bytes': after.st_size, 'mtime_ns': after.st_mtime_ns}


def guards():
    paths = {'delivery': ASSEMBLY/'delivery-validation.json',
             'video': ASSEMBLY/'video-validation.json', 'audio': ASSEMBLY/'audio-validation.json',
             'colony': ASSEMBLY/'colony-export.json', 'review': ASSEMBLY/'review-validation.json',
             'master': PACKAGE/'visual/master-validation.json',
             'native': PACKAGE/'audit/native-validation.json',
             'decoded': PACKAGE/'audit/decoded-colour-validation.json',
             'renderer': PACKAGE/'visual/renderer-validation.json',
             'approval': ROOT/'music/crater-rim-production-2026-11-07/user-approval.json'}
    evidence = {key: read_json(path) for key, path in paths.items()}
    for key in ('delivery', 'video', 'audio', 'review', 'master', 'native', 'decoded', 'renderer'):
        require(evidence[key]['status'] == 'passed', 'Required audit is not passed: '+key)
    d, v, a, m = (evidence[key] for key in ('delivery', 'video', 'audio', 'master'))
    require(Path(d['output']).resolve() == FINAL.resolve(), 'Unexpected delivery destination')
    require((d['seconds'], d['frames'], d['fps'], d['dimensions']) == (3600,108000,30,[3840,2160]),
            'Wrong final dimensions/runtime/frame count')
    require(d['native_artwork_dimensions'] == [1672,941], 'Unexpected native source size')
    require(d['source_audio_unchanged'] and d['new_audio_gain_db'] == 0 and not d['extra_sfx'],
            'Audio policy differs from authorized accepted mix')
    require(evidence['approval']['audio_mix_accepted'] and
            evidence['approval']['accepted_full_mix_sha256'] == d['audio_source_sha256'] == APPROVED_AUDIO_SHA,
            'Accepted source-audio identity mismatch')
    require(sha(SOURCE_AUDIO) == APPROVED_AUDIO_SHA, 'Accepted source audio changed')
    stamp = checked_media(FINAL, d['bytes'], d['sha256'])
    require(v['output_stamp'] == a['output_stamp'] == stamp, 'Video/audio audits belong to another output')
    require(v['frames'] == 108000 and all(v[key] for key in (
        'all_original_demuxed_mp4_pts_dts_durations_exact',
        'all_packets_after_first60s_match_600s_master_phase',
        'first_clean_unit_all_decoded_frames_match_master',
        'opening_after22s_all_decoded_frames_match_master', 'intro_present_once')), 'Incomplete final picture/timestamp audit')
    require(a['sample_frames'] == 172800000 and a['source_sha256'] == APPROVED_AUDIO_SHA and
            a['new_gain_db'] == 0 and not a['additional_sfx'] and not a['new_closing_fade'] and
            a['opening_silence_to5_fade_to20_once'], 'Incomplete/wrong full-audio comparison')
    verification = evidence['colony']['verification']
    require(verification['passed'] and verification['full_decode'] and
            all(item['ok'] for item in verification['checks']), 'Actual Colony full decode failed')
    require(m['sha256'] == d['master_sha256'] == evidence['decoded']['master_sha256'], 'Master/audit identity mismatch')
    checked_media(Path(d['master']), m['bytes'], m['sha256'])
    renderer_hash = sha(PACKAGE/'visual/long_scene.py')
    require(m['renderer_sha256'] == evidence['native']['renderer_sha256'] ==
            evidence['decoded']['renderer_sha256'] == renderer_hash, 'Renderer/audit mismatch')
    require(m['independent_native_audit_sha256'] == evidence['decoded']['native_validation_sha256'] == sha(paths['native'])
            and m['independent_encoded_audit_sha256'] == sha(paths['decoded'])
            and evidence['decoded']['all_selected_actual_decoded_frames_pixel_exact_yuv'], 'Independent picture evidence mismatch')
    for relative, expected in evidence['renderer']['fingerprints'].items():
        require(sha(PACKAGE/relative) == expected, 'Native source/dependency changed: '+relative)
    review = evidence['review']
    require(Path(review['source']).resolve() == FINAL.resolve() and review['source_output_stamp'] == stamp and
            review['seconds'] == 135 and review['full_video_audio_decode'], 'Review does not match completed final')
    checked_media(Path(review['path']), review['bytes'], review['sha256'])
    return evidence, {key: {'path': rel(path), 'sha256': sha(path)} for key,path in paths.items()}, stamp


def newline(text):
    return '\r\n' if text.count('\r\n') > text.count('\n')/2 else '\n'


def json_bytes(value, old):
    return ((json.dumps(value, indent=2, ensure_ascii=False)+'\n').replace('\n', newline(old.decode('utf-8-sig')))).encode('utf-8')


def current_block(old, paragraph):
    text = old.decode('utf-8-sig')
    nl = newline(text)
    block = f'<!-- {MARKER}:begin -->{nl}{paragraph}{nl}<!-- {MARKER}:end -->'
    pattern = rf'<!-- {MARKER}:begin -->.*?<!-- {MARKER}:end -->'
    if re.search(pattern, text, flags=re.S):
        require(len(re.findall(pattern,text,flags=re.S)) == 1, 'Repeated current block')
        return re.sub(pattern, lambda _: block, text, count=1, flags=re.S).encode('utf-8')
    match = re.match(r'#[^\r\n]*(?:\r\n|\n)', text)
    require(match is not None, 'Expected document H1')
    return (text[:match.end()]+nl+block+nl+text[match.end():]).encode('utf-8')


def replace_row(old, prefix, value):
    text = old.decode('utf-8-sig')
    pattern = r'^'+re.escape(prefix)+r'[^\r\n]*'
    require(len(re.findall(pattern,text,flags=re.M)) == 1, 'Expected exactly one scene14 row')
    return re.sub(pattern,lambda _:value,text,count=1,flags=re.M).encode('utf-8')


def replace_catalog_entry(old, entry):
    # Replace this object's text only; every byte outside scene14 is retained.
    text = old.decode('utf-8-sig'); decoder = json.JSONDecoder(); pos = text.index('[')+1
    matches = []
    while True:
        while text[pos].isspace() or text[pos] == ',':
            pos += 1
        if text[pos] == ']':
            break
        item, end = decoder.raw_decode(text, pos)
        if item.get('folder') == '14-crater-rim-survey':
            matches.append((pos,end))
        pos = end
    require(len(matches) == 1, 'Catalog must contain exactly one scene14')
    start,end = matches[0]
    replacement = json.dumps(entry,indent=2,ensure_ascii=False).replace('\n','\n  ').replace('\n',newline(text))
    return (text[:start]+replacement+text[end:]).encode('utf-8')


def prepare(evidence, evidence_paths):
    targets = [SCENE/'manifest.json', ROOT/'final/catalog.json', ROOT/'final/README.md',
               ROOT/'PRODUCTION_PIPELINE.md', SCENE/'README.md', SCENE/'motion-brief.md',
               ROOT/'AGENTS.md', PACKAGE/'README.md', PACKAGE/'production-plan.json']
    before = {path:path.read_bytes() for path in targets}; after = dict(before)
    d = evidence['delivery']; day = d['completed_date']
    final_rel = rel(FINAL); package_rel = rel(PACKAGE); delivery_rel = rel(ASSEMBLY/'delivery-validation.json')
    status = 'One-hour 4K final technically verified; V5 visuals with600s attention/60s weather and accepted audio. Full combined user review and upload checks pending.'
    summary = (f'Crater Rim Survey final one-hour 4K delivery ({day}): the user authorized the full version with longer animation timing and accepted audio. '
               f'`{final_rel}` is3600s,3840x2160,30fps/108000frames, upscaled directly from the unchanged1672x941 native V5 source. '
               'The600s attention schedule separates lamp clusters, greenhouse reflections and four rover passages while weather retains its original60s cycle and speeds. '
               'The accepted November7 FLAC is retained at unity with all existing SFX and its20s closing fade; actual Colony v3 appears once, with opening audio silence0-5s/fade5-20s and graphics clear by22s. '
               'Native/source/cache checks, independent encoded controls, full decode, all final timestamps/copied-picture checks and full-source AAC comparison passed. '
               f'Evidence: `{delivery_rel}`. Full combined user review and upload checks remain pending; no continuous playback/listening or publication is claimed. '
               'This production task makes no Git commit/push; previous backup checkpoints remain historical.')
    scene_lead = (f'Current final delivery — {day}: [one-hour4K video](../../{final_rel}) and '
                  f'[verified production package](../../{package_rel}/README.md). Native1672x941 V5 art is upscaled directly to3840x2160/30fps; '
                  'the600s attention schedule runs over unchanged60s weather. Accepted music, wind and room air remain at unity, with the existing closing fade and one actual Colony opening. '
                  'Technical picture/timestamp/decode and complete audio-reference checks passed. Full combined user review and upload checks are pending; continuous playback/listening is not claimed. '
                  'The preparation notes below are historical and do not override this delivery.')
    after[SCENE/'README.md'] = current_block(before[SCENE/'README.md'],scene_lead)
    after[SCENE/'motion-brief.md'] = current_block(before[SCENE/'motion-brief.md'],scene_lead)
    after[ROOT/'AGENTS.md'] = current_block(before[ROOT/'AGENTS.md'],summary)
    package_text = before[PACKAGE/'README.md'].decode('utf-8-sig'); nl = newline(package_text)
    pattern = r'(?<=\n\n)The user authorized the complete one-hour video[^\r\n]*|(?<=\r\n\r\n)The user authorized the complete one-hour video[^\r\n]*'
    lead = (f'The user authorized the complete one-hour video on November8,2026. Completed {day}: '
            f'[`{final_rel}`](../../{final_rel}), exact3600s/3840x2160/30fps, has passed the '
            '[final technical delivery checks](assembly/delivery-validation.json). '
            '[The135-second review](assembly/Crater-Rim-Survey-final-opening-and-scene-135s-720p.mp4) comes from that completed final. '
            'Full combined user review and upload checks remain pending. No continuous playback/listening, publication or new Git backup is inferred.')
    require(len(re.findall(pattern,package_text)) == 1,'Expected package progress lead exactly once')
    after[PACKAGE/'README.md'] = re.sub(pattern,lambda _:lead,package_text,count=1).encode('utf-8')
    after[ROOT/'final/README.md'] = replace_row(before[ROOT/'final/README.md'],'| [14 - Crater Rim Survey]',
        '| [14 - Crater Rim Survey](14-crater-rim-survey/) | [One-hour4K final, technically verified](../music/crater-rim-final-hour-v1/README.md);600s attention/60s weather, accepted audio; full combined review pending | [JPEG](14-crater-rim-survey/thumbnail-v1.jpg) |')
    after[ROOT/'PRODUCTION_PIPELINE.md'] = replace_row(before[ROOT/'PRODUCTION_PIPELINE.md'],'| 14 |',
        '| 14 | [Crater Rim Survey](final/14-crater-rim-survey/README.md) | Native V5 treatment with600s attention over60s weather; [one-hour4K final technically verified](music/crater-rim-final-hour-v1/README.md) | Accepted Nov7 music/wind/room-air hour retained at unity; one Colony opening, original closing fade | Review completed combined video and upload checks; Thu12Nov remains a planning slot |')
    manifest = json.loads(before[SCENE/'manifest.json']); original = copy.deepcopy(manifest)
    production = {'status':status,'completed_date':day,'file':final_rel,'bytes':d['bytes'],'sha256':d['sha256'],
                  'seconds':3600,'dimensions':[3840,2160],'fps':30,'frames':108000,
                  'native_dimensions':[1672,941],'weather_seconds':60,'attention_seconds':600,
                  'production_package':package_rel+'/README.md','validation':delivery_rel,
                  'review':rel(Path(evidence['review']['path'])),'review_sha256':evidence['review']['sha256'],
                  'full_combined_user_review':'pending','continuous_playback_or_listening_claimed':False,
                  'publication':'not inferred','new_git_backup':False,'evidence':evidence_paths}
    manifest.update(status=status,video=copy.deepcopy(production),final_production=copy.deepcopy(production),
                    resolution_note='Native1672x941 artwork rendered at native detail and Lanczos upscaled directly to3840x2160; not native4K art.')
    manifest['audio'] = {'path':rel(SOURCE_AUDIO),'sha256':APPROVED_AUDIO_SHA,'seconds':3600,'user_approved':True,
                         'approval_date':'2026-11-07','new_gain_db':0,'additional_sfx':False,
                         'existing_closing_fade_seconds':20,'opening_audio':'silence0-5s/fade5-20s once',
                         'production_package':'music/crater-rim-production-2026-11-07/README.md'}
    manifest['music_preparation']['status'] = 'Historical prompt preparation and file fingerprints retained below; accepted November7 hour now used in completed final production. Prospective music-writing briefs remain separate.'
    motion = manifest['motion_preparation']; motion['status'] = 'Native V5 visuals retained in verified600s production schedule and one-hour4K delivery; prior minute previews below are historical.'
    motion['brief'].update(sha256=hashlib.sha256(after[SCENE/'motion-brief.md']).hexdigest(),bytes=len(after[SCENE/'motion-brief.md']))
    motion.setdefault('historical_v5_layers',copy.deepcopy(motion['layers']))
    motion['layers'] = [item.replace('two flicker clusters per minute','two flicker clusters per600s').replace('two perspective-scaled utility rover passages','four perspective-scaled utility rover passages per600s') for item in motion['historical_v5_layers']]
    manifest['long_version_preparation'].update(status='Saved600s plan implemented and technically verified in completed one-hour4K production.',
        final_program_seconds=3600,soundtrack_selected=True,implementation=package_rel+'/visual/long_scene.py',final_delivery=delivery_rel)
    for key in ('source','artwork','prompts','thumbnail','youtube_metadata','approval','selection'):
        require(manifest[key] == original[key],'Protected manifest section changed: '+key)
    after[SCENE/'manifest.json'] = json_bytes(manifest,before[SCENE/'manifest.json'])
    catalog = json.loads(before[ROOT/'final/catalog.json']); entry = copy.deepcopy(next(x for x in catalog if x['folder']=='14-crater-rim-survey'))
    entry.update(status=status,duration_seconds=3600,video='../../'+final_rel,dimensions=[3840,2160],fps=30,
                 native_dimensions=[1672,941],final_delivery='../../'+delivery_rel,
                 production_package='../../'+package_rel+'/README.md',full_combined_user_review='pending')
    entry['animation_preview']['user_feedback']='Historical V5 minute received positive feedback; the600s schedule is now implemented in the final production.'
    entry['final_preview']='../../'+rel(Path(evidence['review']['path']))
    after[ROOT/'final/catalog.json'] = replace_catalog_entry(before[ROOT/'final/catalog.json'],entry)
    plan=json.loads(before[PACKAGE/'production-plan.json'])
    plan.update(status='completed_technically_verified',completed_date=day,delivery_validation='assembly/delivery-validation.json',output_bytes=d['bytes'],output_sha256=d['sha256'],user_full_combined_review='pending')
    after[PACKAGE/'production-plan.json']=json_bytes(plan,before[PACKAGE/'production-plan.json'])
    return before,after


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--apply',action='store_true'); args = parser.parse_args()
    evidence, evidence_paths, media_stamp = guards()
    before,after = prepare(evidence,evidence_paths)
    changed = [path for path in before if before[path] != after[path]]
    print(json.dumps({'guards':'passed','write_requested':args.apply,'files':[rel(path) for path in changed]},indent=2))
    if not args.apply or not changed:
        return
    require(all(path.read_bytes()==before[path] for path in before),'A current record changed during preparation')
    st=FINAL.stat(); require({'bytes':st.st_size,'mtime_ns':st.st_mtime_ns}==media_stamp,'Final media changed before records update')
    run = PACKAGE/'records-finalization'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(parents=True,exist_ok=False)
    receipt={'status':'prepared','script_sha256':sha(__file__),'delivery_sha256':evidence_paths['delivery']['sha256'],'files':[]}
    for i,path in enumerate(changed):
        backup=run/'before'/rel(path); backup.parent.mkdir(parents=True,exist_ok=True); backup.write_bytes(before[path])
        (run/f'staged-{i}').write_bytes(after[path])
        receipt['files'].append({'path':rel(path),'before_sha256':hashlib.sha256(before[path]).hexdigest(),
                                 'after_sha256':hashlib.sha256(after[path]).hexdigest(),'backup':rel(backup)})
    applied=[]
    try:
        for i,path in enumerate(changed):
            require(path.read_bytes()==before[path],'Concurrent record edit: '+str(path))
            os.replace(run/f'staged-{i}',path); applied.append(path)
        require(all(path.read_bytes()==after[path] for path in changed),'Written records differ')
        receipt['status']='passed'
    except Exception:
        for path in reversed(applied):
            restore=run/'rollback.tmp'; restore.write_bytes(before[path]); os.replace(restore,path)
        receipt['status']='failed_rolled_back'
        raise
    finally:
        (run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('Current records updated; exact previous bytes retained at '+str(run))


if __name__ == '__main__':
    main()
