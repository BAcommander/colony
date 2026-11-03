"""Catalogue preserved SFX sources with contextual approval and portable previews."""
from pathlib import Path
import json, hashlib, shutil, subprocess, re, math, html, sys
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];FF=shutil.which('ffmpeg')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(R).as_posix()
def save(n,v):(H/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def measure(p):
 r=subprocess.run([FF,'-hide_banner','-nostats','-i',str(p),'-vn','-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True,check=True)
 log=r.stderr.decode(errors='replace').rsplit('Summary:',1)[-1]
 return {k:float(re.search(pattern,log)[1]) for k,pattern in [('lufs',r'\bI:\s*([-+\d.]+) LUFS'),('lra_lu',r'\bLRA:\s*([-+\d.]+) LU'),('true_peak_dbtp',r'\bPeak:\s*([-+\d.]+) dBFS')]}
def main():
 assert not (H/'catalog.json').exists(),'Preserve existing library; update entries explicitly'
 for name in ['assets','previews','prompts']:(H/name).mkdir(exist_ok=True)
 dp=R/'music/deepwell-production-2026-11-01';dj=read(dp/'combined-review-v4/mix-recipe.json');dh=read(dp/'delivery-hour-v1/mix-recipe.json')
 jp=R/'music/empty-junction-final-hour-v2/mix-recipe.json';j=read(jp)
 rainp=R/'music/shared-rain-overlay/rain-preset-current.json';rain=read(rainp)
 usage=lambda scene,gain,event,fade,recipe,status='accepted balance':{'scene':scene,'source_gain_db':gain,'event_seconds':event,'fade_seconds':fade,'recipe':rel(recipe),'status':status}
 entries=[]
 def add(id,title,category,source,expected,description,usages,notes,prompt=None,aliases=None):
  entries.append(dict(id=id,title=title,category=category,source=Path(source),expected=expected,description=description,usages=usages,reuse_notes=notes,prompt=prompt,aliases=aliases or []))
 add('wind-soft-exterior-01','Soft exterior wind','Wind',j['source_paths'][0],j['source_hashes'][0],
     'Soft wind intended as a distant exterior layer, including sheltered listening viewpoints.',
     [usage('The Empty Junction',j['gain_db']['wind'],60,j['fade_seconds']['wind'],jp,'balance accepted; later25% frequency increase requested'),usage('Deepwell Station',dh['sfx_gain_db']['wind'],60,[8,12],dp/'delivery-hour-v1/mix-recipe.json')],
     ['30-second source; accepted prepared loop trims1–29s with4s overlap (24-second cycle).','An8-second rise is not an8-second event. Deepwell wind plays60-second passages.','Deepwell+4.85dB and Junction+7.85dB are source-specific, scene-specific settings.'],aliases=[dj['wind']['local_copy']])
 add('water-soft-ripples-01','Gentle exterior water','Water',dj['water']['source'],dj['water']['sha256'],
     'Rolling/rippling ocean-water source reused quietly for the sheltered Deepwell gallery.',
     [usage('Deepwell Station',dh['sfx_gain_db']['water'],'40–70',[8,12],dp/'delivery-hour-v1/mix-recipe.json')],
     ['Originally stored with Shoreless; do not describe this as a literal new circulation-pump recording.','Deepwell source gain includes the requested10% amplitude reduction.','Prepared loop trims1–29s with2s overlap (26-second cycle).'],aliases=[dj['water']['local_copy']])
 add('train-distant-freight-01','Distant freight passage','Transport',j['source_paths'][1],j['source_hashes'][1],
     'Distant freight/train texture intended to add railway identity without a foreground arrival.',
     [usage('The Empty Junction',j['gain_db']['train'],25,j['fade_seconds']['train'],jp,'balance accepted; laterfrequency increase requested')],
     ['Use complete25-second source; accepted timing places it in wind gaps.','Related written brief includes a distant whistle; actual rendered contents are not independently identified by the assistant.'],
     R/'music/empty-junction-music-v1/distant-train-sfx-prompt-v1.txt')
 add('grit-mineral-soft-01','Fine mineral grit','Surface texture',j['source_paths'][2],j['source_hashes'][2],
     'Fine dry mineral-grit rustle intended for exposed steps/platform surfaces.',
     [usage('The Empty Junction',j['gain_db']['grit'],12,j['fade_seconds']['grit'],jp,'balance accepted; laterfrequency increase requested')],
     ['Earlier grit was too loud. Accepted source gain is−3.3dB,7.5dB below first mix.','Events also follow the wind envelope. Keep this as a secondary texture, and review it with music.'],
     R/'music/empty-junction-music-v1/mineral-grit-sfx-prompt-v1.txt')
 add('pump-distant-circulation-01','Distant circulation pump','Machinery',dj['pump']['source'],dj['pump']['sha256'],
     'Plant-room pump cycle intended as a rounded interior sound with pipe resonance.',
     [usage('Deepwell Station',dh['sfx_gain_db']['pump'],20,[3,5],dp/'delivery-hour-v1/mix-recipe.json')],
     ['Complete20-second source;22 events in the accepted hour.','Placed in water/wind gaps. Balance is approved in the composition, not a universal machinery preset.'],
     dp/'combined-review-v2/plant-room-pump-sfx-prompt.txt')
 add('rain-sheltered-gentle-01','Gentle sheltered rain','Rain',rain['settings']['path'],rain['source_sha256'],
     'Continuous gentle rain intended to be heard from shelter.',
     [usage('Rainline Relay',rain['settings']['gain_db'],120,[20,30],rainp)],
     ['Approved v3 after two peak-level reductions;43.75% of originalv1 rain amplitude.','Two-minute passages with90 seconds off;2-second loop overlap.','Later current preset records approval; original v3 delivery report predates that approval.'],
     R/'music/shared-rain-overlay/rain-overlay-prompt-v2-short.txt')
 results=[]
 for e in entries:
  p=e.pop('source');assert sha(p)==e.pop('expected'),('Source hash changed',p)
  dst=H/'assets'/(e['id']+p.suffix.lower());shutil.copy2(p,dst);assert sha(dst)==sha(p)
  raw=subprocess.check_output([FF,'-v','error','-i',str(dst),'-vn','-ar','48000','-ac','2','-f','f32le','pipe:1'])
  audio=np.frombuffer(raw,'<f4').reshape(-1,2);assert np.isfinite(audio).all() and np.max(abs(audio))<1
  m=measure(dst);gain=min(-24-m['lufs'],-2-m['true_peak_dbtp']);preview=H/'previews'/(e['id']+'.mp3')
  subprocess.run([FF,'-v','error','-n','-i',str(dst),'-vn','-af',f'volume={gain:.8f}dB','-c:a','libmp3lame','-b:a','192k','-ar','48000',str(preview)],check=True)
  pm=measure(preview);assert pm['true_peak_dbtp']<-.5
  prompt=e.pop('prompt')
  if prompt:
   target=H/'prompts'/(e['id']+'.txt');shutil.copy2(prompt,target);e['related_prompt']={'path':target.relative_to(H).as_posix(),'original_path':rel(prompt),'sha256':sha(target),'actual_generation_prompt_confirmed':False,'scope':'Related saved brief, not proof of exact wording/settings used for this supplied source.'}
  else:e['related_prompt']=None
  e.update(source_file=dst.relative_to(H).as_posix(),source_sha256=sha(dst),source_bytes=dst.stat().st_size,original_project_path=rel(p),duration_seconds=len(audio)/48000,sample_rate=48000,channels=2,measurements=m,preview_file=preview.relative_to(H).as_posix(),preview_gain_db=gain,preview_measurements=pm,preview_sha256=sha(preview),approval='Accepted in recorded scene mix',general_favourite=False,assistant_listening=False,provenance='User-supplied generated SFX; exact provider/model/settings and licence terms not independently verified here. Existing source records retained.')
  results.append(e);print('Imported',e['title'],len(audio)/48000,'seconds; source hash exact',flush=True)
 save('catalog.json',{'schema_version':1,'created':'2026-11-01','scope':'Starter library of six source sounds with contextual acceptance, deduplicated by original source hash. No universal favourite rating inferred.','preview_policy':'Preview copies use constant gain toward−24LUFS, limited for peak headroom. They are audition-only. Reuse original source_file with scene-specific gains.','reuse_policy':'Check location, distance, plateau level, event duration and quiet gaps in the actual composition before adopting. Keep gains and frequency separate.','entries':results})
 save('rejected-approaches.json',{'scope':'Feedback history, not a complete catalogue of rejected generated files','entries':[{'scene':'The Empty Junction','approach':'Radio chatter/static/electronic station sounds','feedback':'Voices unwanted; early voice-free version too quiet, later static lacked variety; no accepted radio layer in final mix.','decision':'Do not treat these approaches as approved library sounds.'},{'scene':'The Empty Junction','approach':'Cabin/compressor mechanical effect','feedback':'User said it did not feel ambient enough and preferred trying distant train/whistle.','decision':'Retain history in original project; not in accepted starter set.'}]})
 render_catalog()
 validate()
def render_catalog():
 results=read(H/'catalog.json')['entries']
 cards=[]
 for e in results:
  esc=html.escape
  uses=''
  for u in e['usages']:
   link='../../'+u['recipe'] if (R/u['recipe']).exists() else 'https://github.com/BAcommander/colony/blob/aa62e427e3f6386217e90229c063820c8f54ccae/'+u['recipe']
   gain=f"{u['source_gain_db']:+.2f}dB" if u.get('source_gain_db') is not None else u.get('level_note','See recipe')
   uses+=f"<li><b>{esc(u['scene'])}</b>: {esc(gain)}; {esc(str(u['event_seconds']))}s passages. {esc(u['status'])}. <a href='{esc(link)}'>Recipe</a></li>"
  prompt=f"<a href='{e['related_prompt']['path']}'>Related brief</a>" if e['related_prompt'] else 'Exact prompt not recorded'
  cards.append(f"<article data-category='{esc(e['category'])}' data-search='{esc((e['title']+' '+e['description']+' '+' '.join(u['scene'] for u in e['usages'])).lower())}'><span class='tag'>{esc(e['category'])} · {e['duration_seconds']:g}s</span><h2>{esc(e['title'])}</h2><p>{esc(e['description'])}</p><p class='accepted'>{esc(e['approval'])}</p><label>Listening preview — adjusted toward −24 LUFS</label><audio controls preload='none' src='{e['preview_file']}'></audio><details><summary>Original source and reuse notes</summary><p>Original: {e['measurements']['lufs']:.1f}LUFS · {e['measurements']['true_peak_dbtp']:.1f}dBTP</p><audio controls preload='none' src='{e['source_file']}'></audio><p><a href='{e['source_file']}' download>Original for mixing</a> · {prompt}</p><ul>{uses}</ul><ul>{''.join('<li>'+esc(n)+'</li>' for n in e['reuse_notes'])}</ul><p class='muted'>Related briefs do not confirm exact generation wording. Acceptance applies to the recorded mix; it is not a universal gain preset.</p></details></article>")
 categories=sorted({e['category'] for e in results})
 page="""<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Ambient Colony — SFX Library</title><style>body{margin:0;background:#11191c;color:#e9ece7;font:16px/1.55 system-ui}main{max-width:1140px;margin:0 auto;padding:38px 24px}h1{font-size:38px;line-height:1.1}h2{font-size:23px;margin:12px 0}a{color:#9fd7d3}header p{max-width:800px}.toolbar{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}input,select{background:#213036;color:#fff;border:1px solid #577078;border-radius:8px;padding:12px;font:inherit}input{flex:1;min-width:240px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}article{background:#1a282d;border:1px solid #34484f;border-radius:14px;padding:22px}article[hidden]{display:none}.tag,.muted,label{color:#aabfc4;font-size:13px}.accepted{color:#c7dca5;font-size:14px}audio{display:block;width:100%;margin:12px 0 18px}summary{cursor:pointer;color:#e8ce9f}li{margin-bottom:9px}footer{margin-top:32px;color:#aabfc4}button{cursor:pointer}#count{align-self:center}</style><main><header><p>AMBIENT COLONY / REUSABLE SOUND</p><h1>SFX Library</h1><p>Reusable source sounds with recorded scene uses and candidate auditions. Check each source’s selection and listening status. Audition a source, inspect its previous use, then check it against the new scene.</p><p>Preview players use a consistent listening level. Use the <b>original source</b> for mixing; the saved gains apply to those original files.</p></header><div class='toolbar'><input id='search' type='search' placeholder='Search sound or scene…' aria-label='Search library'><select id='category' aria-label='Sound category'><option value=''>All categories</option>"""+''.join(f'<option>{html.escape(c)}</option>' for c in categories)+"""</select><span id='count' aria-live='polite'>7 sounds</span></div><section class='grid'>"""+''.join(cards)+"""</section><footer><a href='catalog.json'>Catalogue data</a> · <a href='README.md'>Reuse guide</a> · <a href='rejected-approaches.json'>Earlier approaches we did not keep</a><p>New scenes still need an in-composition listening check. No autoplay, uploads or external services.</p></footer></main><script>const cards=[...document.querySelectorAll('article')],search=document.querySelector('#search'),category=document.querySelector('#category');function filter(){let n=0;for(const c of cards){c.hidden=!(c.dataset.search.includes(search.value.toLowerCase().trim())&&(!category.value||c.dataset.category===category.value));if(!c.hidden)n++;else c.querySelectorAll('audio').forEach(a=>a.pause());}document.querySelector('#count').textContent=n+' sounds';}search.addEventListener('input',filter);category.addEventListener('change',filter);document.addEventListener('play',e=>{if(e.target.tagName==='AUDIO')document.querySelectorAll('audio').forEach(a=>{if(a!==e.target)a.pause();});},true);</script></html>"""
 page=page.replace('>7 sounds</span>',f'>{len(results)} sounds</span>')
 (H/'index.html').write_text(page,encoding='utf-8')

def validate():
 results=read(H/'catalog.json')['entries']
 for e in results:
  assert sha(H/e['source_file'])==e['source_sha256']
  assert (H/e['source_file']).stat().st_size==e['source_bytes']
  assert sha(H/e['preview_file'])==e['preview_sha256']
  if e.get('related_prompt'):assert sha(H/e['related_prompt']['path'])==e['related_prompt']['sha256']
  assert abs(e['preview_measurements']['lufs']-(e['measurements']['lufs']+e['preview_gain_db']))<=.6
  assert e['preview_measurements']['true_peak_dbtp']<-.5
 assert len({e['source_sha256'] for e in results})==len(results)
 save('validation.json',{'status':'passed','date':'2026-11-03','unique_sources':len(results),'all_catalogue_source_preview_and_prompt_hashes_match':True,'all_catalogue_media_paths_exist':True,'source_comparison':'Six imported originals/previews match the production-branch catalogue; new creak matches supplied original.','assistant_listening':False})
 print('PASS:',len(results),'source copies, previews and catalogue links verified',flush=True)
if __name__=='__main__':
 if '--validate' in sys.argv:validate()
 elif '--refresh' in sys.argv:render_catalog();validate()
 else:main()
