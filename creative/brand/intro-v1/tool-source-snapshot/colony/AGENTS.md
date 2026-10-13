# Colony internal tool

This folder is the separate Ambient Colony final-video assembler, not the main
Speedy SlideShow product. Keep its release behaviour and build separate.

## Opening default (2026-10-13)

The user requested the thumbnail typography and orbital logo for all future
video intros, followed by the public title and the exact final line
`Stay a while and listen:`. The GUI defaults to enabled with a blank title.
`intro.py` owns native graphics and timing. Fonts and OFL licence are bundled
under assets/fonts and must remain included in Colony.spec.

Dark scene through the channel credit; brighten from main title at 10 seconds
to normal at 20. Optional opening audio holds silence to 5 then rises to normal
by 20. Do not stack this with a baked opening fade; expose the keep-supplied-fade
option. Preserve later SFX schedules and music joins. Preview opening must also
work without music: the user is improving the reusable treatment, not required
to have a new soundtrack ready.

Apply once during final assembly, outside clean repeating masters. Encode only
complete opening units and keep subsequent units copied. Preserve YUV/colour
tags and loop phase. Preview and export share the same path and full-playlist
SFX/overlay schedule. API defaults remain compatible with historical scripts;
new production scripts opt in with IntroSettings(public_title).

Tests: `python -m pytest tests/test_colony.py tests/test_colony_sfx.py tests/test_colony_intro.py -q`.
Build: `python -m PyInstaller --noconfirm --clean --distpath dist --workpath build/colony colony/Colony.spec`.
Preserve the prior executable, and never close a user's running export.

Production workflow/reference evidence lives in `C:/Colony/creative/brand/intro-v1/`
and its ANIMATION_WORKFLOW/MUSIC_WORKFLOW/PRODUCTION_PIPELINE documents. V1 is
implemented and technically checked; user visual/listening approval remains
pending. No whole-video rerenders follow automatically from an intro change.
