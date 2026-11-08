# Independent production audit

`audit_long_scene.py` loads the original backed-up V5 separately from the new production snapshot. It derives the ten-minute schedule from the original continuation plan and compares the actual frozen event methods with the production renderer.

Run from the repository root using `.local/crater-final-runtime/Scripts/python.exe -B music/crater-rim-final-hour-v1/audit/audit_long_scene.py native`. The native stage checks every one of the 18,000 event-clock ticks, all event starts/peaks/ends, minute joins, quiet legacy event times, original source/mask hashes, safe cloud sampling, protected pixels, retained weather, immutable cache inputs and the 600-second regional seam. It writes `native-validation.json`.

After the clean master exists, run the same command with `decoded` instead of `native`. Optional `--master` selects an explicit master path. This independently renders native reference controls and uses the production FFmpeg Lanczos/BT.709/TV conversion. Actual decoded YUV controls must match byte for byte. It writes `decoded-colour-validation.json` and a contact sheet from actual decoded pictures.

The reference preserves the original NumPy scalar types as well as the formulas. A Python `float` substituted for the original glint's NumPy `float64` changed one channel by one code at 480 seconds under NumPy 2, despite an identical scalar value. Keeping the original type restored exact pixels; no production change or tolerance relaxation was required.

The native check alone does not validate an encoded file. Creating a contact sheet does not establish that someone inspected it. Full final frame/timestamp, stream-copy, opening and AAC checks belong to the separate assembly validator. No numerical check implies uninterrupted playback, listening, publication or user artistic approval.
