"""Render source-bound animation backlogs as repository briefs and a local proposal map."""
from pathlib import Path
import html
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(number, slug):
    return json.loads((HERE/f'{number}-{slug}-backlog.json').read_text(encoding='utf-8'))


def write(path, text):
    path.write_bytes(text.encode('utf-8'))


def current_note(number=None):
    """Keep this historical proposal generator from hiding a later delivery."""
    path=HERE/'first-draft-status.json'
    if not path.exists():return ''
    data=json.loads(path.read_text())
    if number is None:
        return '> Current: both full-minute first visual drafts are delivered for review. [Play both drafts and detail clips](review.html). The original planning checkpoint follows; the ten-minute production schedule and audio remain pending.\n\n'
    item=next(s for s in data['scenes'] if s['catalog_number']==number)
    return f"> Current: [{item['version']} full-minute visual draft](../../{item['folder']}/README.md) is delivered at720p/{item['fps']}fps, with all twelve candidates represented in the first pass. [Paired visual review](../../creative/animation-development/2026-11-05-16-17/review.html). Technical checks passed; user artistic review, the ten-minute event schedule, audio and4K remain pending. The historical planning checkpoint follows.\n\n"


def brief(scene):
    n = scene['catalog_number']
    city = n == 16
    title = scene['title']
    direction = ('A warm, still apartment above a rainy city that carries on living outside the glass.' if city else
                 'A sheltered expedition camp beside a steady open portal, with the alien landscape and fabric responding to the same wind.')
    observed = ('The existing V3 already has road traffic, three travelling signs, three animated panels, window modulation, rain, sliding bead marks, gap mist, water/floor reflections and cup steam. Plants are deliberately static. Four hovering vehicles were repaired out; preserve those repairs and the no-aircraft direction. The current loop is ten seconds at sixty fps.' if city else
                'V1 and V2 are eight-second portal tests. V2 adds broad pearl-blue highlights and three small landing-light areas. Clouds, basin, canopy, foreground practicals, computer, radio and cup remain static. The portal tests are continuous auditions, not completed periodic loops.')
    rows = ['| ID | Candidate | Existing or new | Priority | Visible action |', '|---|---|---|---|---|']
    for effect in scene['candidates']:
        label = {1: 'Core', 2: 'Support', 3: 'Experiment'}[effect['priority']]
        rows.append(f"| {effect['id']} | {effect['title']} | {effect['state'].replace('_', ' ')} | {label} | {effect['action']} |")
    stages = ('''1. Preserve V3 and audit its source/encoded colour path. Replace the machine-specific ShareX FFmpeg path in a new renderer with the portable bundled binary. Keep native1672×941 coordinates through the effect pass; upscale once at delivery.
2. Prove A04/A05 together: two independent sign signals with matching haze/river/floor response. Also prove A02 on one road with exact body/occluder registration before expanding traffic.
3. Add A01 coherent city cloud transport and A06 true glass optics. Review these principal actions at720p/60fps at actual speed before supporting effects.
4. Build a genuine sixty-second unique scene. V3 uses normalized10s time for almost every layer and forces each traffic identity through its entire route in that period. Simply changing DURATION to60 slows all traffic/rain/steam by six. Separate physical speeds, particle lifetimes, sign programmes and held window events from the master period.
5. Add rooftop vapour, cup steam, selected occupancy states and one practical-light cue with their own remapped receivers. Then audition the rarer commuter shuttle.
6. Only include leaves or the ferry after their isolated geometry/contact tests work. Use a separate proposed600s attention schedule for rare transit, lamp and occupation events, preserving the approved appearance while avoiding a short repeated show.
7. Review the complete new loop and timing at normal size; then make the accepted native-to4K/60fps master, with explicit colour conversion/tags and the Colony intro applied once during final assembly.''' if city else
'''1. Prepare a confined mug repair: the still visibly has a handle on both sides. Inspect the gate approach, rail joins and canopy rigging at native size too. Save the exact patch and prove all unrelated source pixels unchanged before freezing a new production plate.
2. Prove G01/G02 as one hero system: broad contained water motion with matching light on real stone, rail and ring surfaces. Keep the gate already open and the camera locked. Preserve warm foreground counterlight.
3. Test G05 on the broad cloth folds with fixed supports, then connect the same gust to G04 basin/ground air. Source-isolated moving free edges are a separate asset problem; do not smear the background to manufacture cloth motion.
4. Add source-safe G03 cloud layers around the fixed world and spires. Do not let transported samples contain pieces of the world, ring, canopy or rock. Clouds that truly cross the world need an independently prepared cloud-only element and new occlusion design.
5. Add laptop/radio indicators, corrected-mug steam and restrained warm practical behaviour. Feed the same portal field into local cool receiver masks, with different material/facing/falloff responses.
6. Build and validate the real sixty-second periodic scene at720p/30fps. The existing V1 drift grows linearly over time, and V2 highlight periods5.4/7.3s do not close on60s. See the provisional periodic-surface design; do not merely extend the eight-second settings.
7. Add a separate proposed600s attention clock and wind/SFX cue sheet. Optional strap/scrub motion or a rover follows acceptance of the base scene. Native-to4K/30fps production and audio assembly remain later steps.''')
    safeguards = ('Retain the source warm/cool balance, the repaired absence of hovering cars, locked furnishings and exact window-frame/building/shoreline geometry. Readability comes from useful shape, contrast and timing; no synchronized skyline pulse. True droplet refraction may affect architecture only locally through the bead, with source-valid sampling. The sampled1080p file reports a BT.709 matrix but unspecified primaries/transfer; audit the old RGB-to-YUV conversion and set the full colour chain explicitly in new work without silently grading the still.' if city else
                  'Keep the planet/moon, gate ring, stairs, poles, cases and chair structurally fixed. A path lamp is a warm practical, not an excuse for a whole path of flashing lights. Keep the gate in its steady open state; a repeated activation burst or human crossing is outside the initial build. Source repair and new rover/leaf/strap assets require their own proof before inclusion.')
    sound = ('Start with indoor room air and rain heard through closed glass. Add distant city/road movement only if the room perspective supports it. Couple significant sign changes to reflections, and weather changes to the rain bed. A rare bus/ferry cue is an optional later audition, with filtered distance and no sharp horn or advertising voice. Existing music prompts remain drafts; no new sound or generation is made in this plan.' if city else
             'Start with open-air wind and an original low resonant gate bed, then selected cloth rustle tied to the same gust as the canopy/ground air. Radio receive sound is optional and sparse, informed by the Snowline chatter feedback, with no automatically reused gains. Cup, laptop and lamps do not each need a sound. Balance isolated effects and then the same music with/without ambience at matched level.')
    extra = []
    for effect in scene['candidates']:
        extra += [f"### {effect['id']} — {effect['title']}", '', effect['method'], '',
                  f"**Proof:** {effect['acceptance']}", '', f"**Asset/preparation:** {effect['asset_requirement']}", '']
    return current_note(n)+f'''# {n} — {title}: animation development plan

Prepared2026-11-05. Status: source/legacy-code audit and proposed build backlog. No new animation or repaired artwork is delivered by this plan. Current source and prior masters remain unchanged.

Proposed new build folder: `{'music/cyberpunk-apartment-animation-v4/' if city else 'music/gate-camp-animation-v3/'}`. Preserve the current version while developing these candidates.

{direction}

[Interactive source map](../../creative/animation-development/2026-11-05-16-17/index.html#scene-{n}) · [Machine-readable backlog](../../creative/animation-development/2026-11-05-16-17/{n}-{scene['slug']}-backlog.json) · [Fresh baseline audit](../../creative/animation-development/2026-11-05-16-17/baseline-audit.json)

## What exists

{observed}

Source: `{scene['source']['path']}`, native1672×941, SHA-256 `{scene['source']['sha256']}`. The existing preview was decoded completely in this task: {'600frames/10s/60fps' if city else '240frames/8s/30fps'}, silent with sequential timestamps. Source and decoded stills were inspected; no new continuous playback or user approval is inferred. Map pins are approximate planning locations, not finished masks.

## Candidate list

{chr(10).join(rows)}

## Build order

{stages}

## Source and motion guards

{safeguards}

Implementation starting point: [{'legacy timing and route audit' if city else 'provisional periodic water design'}](../../creative/animation-development/2026-11-05-16-17/{'16-retiming-design.json' if city else '17-periodic-surface-design.json'}). These are design records, not executable effect settings or proof that a new loop works.

[Existing native-coordinate geometry seeds](../../creative/animation-development/2026-11-05-16-17/geometry-seeds.json) preserve the current glass, roads, occluders, sign boxes and portal aperture. Refine them against the source before treating any new receiver or emitter box as a final mask.

Use eight-to-twelve-second full-composition proofs first, with isolated principal layers and unamplified source-size crops. Check both source taps and output coverage, complete emitter/aperture masks, material-linked spill, solid occlusion, and true local/long-cycle joins. No difference score or endpoint identity establishes natural-looking motion. Preserve named unchanged layers with exact controls while adding effects.

Proposed first complete review:60s at1280×720/{scene['proposed_preview']['fps']}fps. Environmental motion and physical speeds need independent time controls; the later attention schedule is600s, not a default restart every minute. The native1672×941 plate will be upscaled for4K only after look/timing acceptance. Save source/config/code/asset/runtime hashes and exact feedback; apply the current opening once at later assembly.

## Sound and cue relationships

{sound}

## Method and acceptance notes per candidate

{chr(10).join(extra)}
## Lessons carried forward

Crater Rim V5 supplies emitter contrast, useful holds, full-size A/B review, coupled lamp spill and grounded vehicle compositing. Snowline supplies strict source/output exclusions and full-context structure tracing. Baal supplies depth and shared weather/audio cues. Rainline supplies inward glass masks, and Shoreless supplies the warning against a prominent decorative waveform. These methods require new masks and viewing tests; their old scene-specific values or approvals do not transfer.

The broader gate/city proposal, first proofs, optional assets, music, final runtime,4K master and long-form assembly are unbuilt. No paid service, image generation, commit or push is included in this planning task.
'''


def board(scenes):
    articles = []
    for scene in scenes:
        n = scene['catalog_number']
        pins, cards = [], []
        for index, effect in enumerate(scene['candidates'], 1):
            x, y = effect['planning_anchor_native']
            state = {1: 'Core', 2: 'Support', 3: 'Experiment'}[effect['priority']]
            pins.append(f'<a class="pin p{effect["priority"]}" href="#{effect["id"]}" style="left:{100*x/1672:.3f}%;top:{100*y/941:.3f}%" aria-label="{html.escape(effect["title"])}">{index}</a>')
            cards.append(f'''<details id="{effect['id']}"><summary><span class="key">{index:02}</span> {html.escape(effect['title'])}<span class="priority">{state}</span></summary><p>{html.escape(effect['action'])}</p><p><strong>Method:</strong> {html.escape(effect['method'])}</p><p><strong>Pass when:</strong> {html.escape(effect['acceptance'])}</p><p class="asset"><strong>Preparation:</strong> {html.escape(effect['asset_requirement'])}</p></details>''')
        articles.append(f'''<article id="scene-{n}"><header><p class="eyebrow">SCENE {n} · PROPOSED DEVELOPMENT</p><h2>{html.escape(scene['title'])}</h2><p class="intro">{'Refine the existing city systems, then add a few longer stories.' if n==16 else 'Make the open gate light a living expedition camp.'}</p></header><div class="photo"><img src="../../../{scene['source']['path']}" alt="{html.escape(scene['title'])}, unchanged clean source artwork"><div class="pins">{''.join(pins)}</div></div><p class="note">Numbers mark candidate locations. Core = first visible build; support = second pass; experiment = separate asset/geometry proof.</p><div class="effects">{''.join(cards)}</div></article>''')
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Scenes16 and17 — animation development</title>
<style>
:root{color-scheme:dark;--bg:#111519;--panel:#1a2026;--line:#38424b;--text:#eeeae1;--muted:#b4b9bd;--amber:#e7b873;--cyan:#8ecfe3}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:5rem}body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;font-size:16px;line-height:1.6}main{max-width:1280px;margin:auto;padding:2rem 1.5rem 4rem}h1,h2,p{margin:0}h1{font-size:2.2rem;font-weight:600;line-height:1.2}h2{font-size:1.7rem;font-weight:600}a{color:var(--cyan)}.lede{max-width:72ch;color:var(--muted);margin-top:1rem}.nav{display:flex;gap:1.5rem;position:sticky;top:0;background:#111519f2;border-bottom:1px solid var(--line);padding:1rem 0;z-index:9;backdrop-filter:blur(8px)}.nav a{color:var(--text);text-decoration:none}.nav a:hover{text-decoration:underline}article{margin-top:3rem}header{margin-bottom:1.25rem}.eyebrow{color:var(--amber);font-size:.78rem;letter-spacing:.11em}.intro,.note{color:var(--muted)}.photo{position:relative;aspect-ratio:1672/941;overflow:hidden;border:1px solid var(--line)}.photo img{display:block;width:100%;height:100%}.pin{position:absolute;transform:translate(-50%,-50%);display:flex;align-items:center;justify-content:center;width:1.8rem;height:1.8rem;border-radius:50%;background:#12181de8;border:2px solid var(--amber);color:white;font-size:.75rem;font-weight:600;text-decoration:none;box-shadow:0 1px 8px #000b}.pin.p2{border-color:var(--cyan)}.pin.p3{border-color:#b6b9c4;border-style:dashed}.pin:hover,.pin:focus{background:var(--amber);color:#111;outline:2px solid white;z-index:2}.note{margin:.75rem 0 1rem;font-size:.9rem}.effects{display:grid;grid-template-columns:1fr 1fr;align-items:start;gap:.75rem}details{background:var(--panel);border:1px solid var(--line);scroll-margin-top:5rem}details:target{border-color:var(--amber)}summary{cursor:pointer;padding:.85rem 1rem;list-style:none;font-weight:500;display:flex;gap:.7rem;align-items:baseline}summary:before{content:'+';color:var(--muted)}details[open] summary:before{content:'−'}.key{color:var(--amber);font-variant-numeric:tabular-nums}.priority{font-size:.75rem;margin-left:auto;color:var(--muted)}details p{padding:0 1rem .8rem;color:#d2d5d6}details p.asset{color:var(--muted);font-size:.9rem}.footer{border-top:1px solid var(--line);margin-top:3rem;padding-top:1rem;color:var(--muted);max-width:85ch}@media(max-width:750px){main{padding:1.5rem 1rem 3rem}.effects{grid-template-columns:1fr}.pins{display:none}h1{font-size:1.6rem}.nav{gap:1rem;font-size:.9rem}.priority{white-space:nowrap}}
</style></head><body><main><h1>Two scenes. Two different kinds of life.</h1><p class="lede">Source-bound animation proposals using the Crater Rim, Snowline, Baal and Rainline lessons. The clean artwork below is unchanged. This map shows ideas and build priorities; it is not a new animation preview.</p><nav class="nav"><a href="#scene-16">16 · Cyberpunk Apartment</a><a href="#scene-17">17 · Gate Camp</a><a href="README.md">Build brief</a></nav>
'''+''.join(articles)+'''
<p class="footer">Existing baselines: scene16 has a10-second/60fps V3 city loop; scene17 has an8-second/30fps V2 water/light test. Planned complete reviews are60seconds, with a separate longer attention clock. Source and decoded stills were inspected; candidate additions, new source repairs and longer animations remain unbuilt.</p></main></body></html>
'''


def main():
    scenes = [load(16, 'cyberpunk-apartment'), load(17, 'gate-camp')]
    for scene in scenes:
        destination = ROOT/f"final/{scene['catalog_number']}-{scene['slug']}/ANIMATION_DEVELOPMENT.md"
        write(destination, brief(scene))
    page=board(scenes)
    if (HERE/'first-draft-status.json').exists():page=page.replace('<nav class="nav">','<p class="lede"><strong>Current full-minute drafts:</strong> <a href="review.html">Play both animations, detail crops and loop joins</a>. The source map below is the original proposal.</p><nav class="nav">')
    write(HERE/'index.html', page)
    write(HERE/'README.md', current_note()+'''# Scenes16 and17 — animation development pack

Prepared2026-11-05 from the exact existing artwork, renderer source and freshly decoded legacy previews. The user requests a scene-specific list of potential animations and stronger development using the accumulated lessons. This is a planning/build-preparation package, not newly rendered motion.

[Open the source map](index.html) · [Scene16 build plan](../../../final/16-cyberpunk-apartment/ANIMATION_DEVELOPMENT.md) · [Scene17 build plan](../../../final/17-gate-camp/ANIMATION_DEVELOPMENT.md) · [Baseline audit](baseline-audit.json) · [Shared cue/production rules](shared-production-rules.json)

The source map works from the clean artwork already in Git. To play the existing city baseline after an on-demand pull, fetch only `git lfs pull --include="final/16-cyberpunk-apartment/animation-v3/Cyberpunk-Apartment-V3-1080p.mp4" --exclude=""`. The gateV2 preview is already a compact ordinary Git file. No new long or4K render needs downloading for this planning review.

There are twelve candidates per scene, separated into core, support and experiments. Every candidate records its approximate native anchor, current/new status, visible action, method, asset prerequisites and a concrete viewing gate. Pins locate ideas; none is a finished effect mask. Existing sources/masters are unchanged. No new animation, paid generation, source repair, music,4K production, commit or push is implied.

For16, first prove source-linked sign/reflection behaviour and grounded irregular traffic, then coherent clouds and refractive glass rain. Its V3 already contains many effects; extending the10s normalized clock alone would slow its motion. The proposed upgrade retains60fps and introduces independent physical timing.

For17, first prove the contained water/interactive-light system and canopy folds, then depth in cloud/ground air. Its current8s portal test is not periodic. The source mug has handles on both sides and needs a confined repair before a new production plate is frozen. The proposed initial loop is60s at30fps.

Both scenes use a separate proposed600s attention clock for rare events, source-safe sampling/solid occlusion, material-linked light responses, unamplified normal-size proofs and independent artistic acceptance. [Crater Rim continuation method](../../../music/crater-rim-animation-v5/LONG_VERSION.md) remains a proposal rather than implemented long-animation evidence. The [city retiming design](16-retiming-design.json) preserves the legacy road routes/rates as a reference; the [gate periodic-surface design](17-periodic-surface-design.json) records candidate cycle changes and source-sampling risks.
''')
    print('Built local source map and both scene development briefs', flush=True)


if __name__ == '__main__':
    main()
