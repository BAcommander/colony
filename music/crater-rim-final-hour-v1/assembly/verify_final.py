"""Independent timestamp, copied-picture, opening and complete AAC checks."""
from assemble import *
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor
import math
import numpy as np
from PIL import Image, ImageDraw

E = H / "evidence"


def settings():
    return json.loads((H / "assembly-settings.json").read_text(encoding="utf-8"))


def stable_output():
    stat = OUTPUT.stat()
    return {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def stamp_matches(stamp):
    require(stable_output() == stamp, "Final file changed during/after verification")


def decode_hash_chunk(path, start, seconds):
    command = [FF, "-v", "error", "-nostdin", "-xerror", "-err_detect", "explode", "-threads", "2"]
    if start:
        command += ["-ss", str(start)]
    command += ["-i", str(path), "-t", str(seconds), "-map", "0:v:0", "-an", "-fps_mode", "passthrough",
                "-threads:v", "2", "-f", "framehash", "-hash", "sha256", "pipe:1"]
    result = run(command)
    require(not result.stderr, "Frame decode errors at source second " + str(start))
    text = result.stdout.decode()
    require("#hash: SHA256" in text, "Unexpected decoded-picture hash algorithm")
    headers, rows, timebase = [], [], None
    for line in text.splitlines():
        if line.startswith("#"):
            headers.append(line)
            if line.startswith("#tb 0:"):
                timebase = Fraction(line.split(":", 1)[1].strip())
        elif line.strip():
            fields = [field.strip() for field in line.split(",")]
            require(timebase is not None and len(fields) == 6 and fields[0] == "0", "Unexpected decoded framehash structure")
            require(int(fields[1]) * timebase == int(fields[2]) * timebase == Fraction(len(rows), FPS),
                    "Decoded chunk frame time mismatch at source second " + str(start))
            require(int(fields[3]) * timebase == Fraction(1, FPS), "Decoded chunk duration mismatch")
            require(len(fields[5]) == 64 and all(char in "0123456789abcdef" for char in fields[5]), "Malformed decoded SHA256 digest")
            rows.append(fields)
    require(len(rows) == round(seconds * FPS), "Decoded chunk has missing/extra frames")
    return headers, rows, timebase


def frame_digests(path, start, seconds, label):
    # All production boundaries are closed GOPs at two-second intervals. Keep
    # 600s checks parallel without skipping a single decoded source picture.
    spans = [(start + offset, 120) for offset in range(0, 600, 120)] if seconds == 600 else [(start, seconds)]
    if len(spans) > 1:
        require(start % 2 == 0, "Parallel decode must start on a closed-GOP boundary")
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(decode_hash_chunk, path, position, length) for position, length in spans]
            # Submission order retains exact temporal order despite asynchronous completion.
            results = [future.result() for future in futures]
    else:
        results = [decode_hash_chunk(path, start, seconds)]
    headers, _, timebase = results[0]
    lines, digests = list(headers), []
    for _, rows, chunk_timebase in results:
        require(chunk_timebase == timebase, "Decoded chunk time bases differ")
        for fields in rows:
            stamp = Fraction(len(digests), FPS) / timebase
            require(stamp.denominator == 1, "Cannot exactly express combined decoded timestamp")
            fields[1] = fields[2] = str(stamp.numerator)
            lines.append(", ".join(fields))
            digests.append(fields[5])
    require(len(digests) == round(seconds * FPS), "Combined decoded picture count mismatch")
    E.mkdir(parents=True, exist_ok=True)
    (E / (label + "-frames.sha256")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return digests


def master_frames(master, evidence):
    cached = evidence.get("raw_frame_hashes")
    if cached and evidence.get("full_4K_decode"):
        path = Path(cached)
        if not path.is_absolute():
            path = Path(settings()["master_validation"]).parent / path
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            require("#hash: SHA256" in text, "Cached master picture hashes must be SHA256")
            rows = [line.rsplit(",", 1)[-1].strip() for line in text.splitlines() if line and not line.startswith("#")]
            require(len(rows) == UNIT_FRAMES, "Master decoded-hash count mismatch")
            require(all(len(row) == 64 and all(char in "0123456789abcdef" for char in row) for row in rows),
                    "Malformed cached SHA256 picture digest")
            E.mkdir(parents=True, exist_ok=True)
            (E / "master-frames.sha256").write_text(text, encoding="utf-8")
            save("master-verification-reuse.json", {"master_sha256": evidence["sha256"], "framehash_source": str(path),
                                                    "framehash_sha256": digest(path), "decoded_frames_reused": len(rows),
                                                    "decoded_picture_hash_algorithm": "SHA256"})
            return rows
    return frame_digests(master, 0, UNIT, "master")


def probe_packet_hashes(path, label):
    """One demux pass yields original MP4 timings and exact packet SHA256s."""
    result = subprocess.run([PROBE, "-v", "error", "-select_streams", "v:0", "-show_packets",
                             "-show_data_hash", "sha256", "-show_entries", "packet=pts,dts,duration,data_hash",
                             "-of", "json", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    E.mkdir(parents=True, exist_ok=True)
    (E / (label + "-error.log")).write_bytes(result.stderr)
    require(result.returncode == 0 and not result.stderr, "FFprobe packet/hash read failed: " + str(path))
    (E / (label + ".json")).write_bytes(result.stdout)
    packets = json.loads(result.stdout)["packets"]
    hashes = []
    for packet in packets:
        require({"pts", "dts", "duration", "data_hash"} <= packet.keys(), "Missing original packet timing/hash")
        algorithm, separator, value = packet["data_hash"].partition(":")
        require(separator and algorithm.upper() == "SHA256" and len(value) == 64
                and all(char in "0123456789abcdef" for char in value), "Malformed FFprobe packet SHA256")
        hashes.append(value)
    return packets, hashes


def verify_packet_hash_equivalence():
    sample = CACHE / "clean-000-060.mp4"
    before = sample.stat()
    sample_stamp = {"bytes": before.st_size, "mtime_ns": before.st_mtime_ns}
    receipt_path = H / "packet-hash-equivalence.json"
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text(encoding="utf-8"))
        if previous.get("status") == "passed" and previous.get("sample_stamp") == sample_stamp:
            return previous
    packets, probe_hashes = probe_packet_hashes(sample, "hash-equivalence-ffprobe-packets")
    ffmpeg_hashes = packet_rows(sample)
    require(len(packets) == len(probe_hashes) == len(ffmpeg_hashes) == 1800, "Hash-equivalence sample frame count changed")
    require(probe_hashes == ffmpeg_hashes, "FFprobe data_hash does not match FFmpeg copied-packet hashes")
    after = sample.stat()
    require(before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns, "Equivalence sample changed")
    receipt = {"status": "passed", "sample": str(sample), "sample_stamp": sample_stamp,
               "packets": len(packets), "algorithm": "SHA256", "all_ffprobe_and_ffmpeg_payload_hashes_equal": True,
               "comparison": "FFprobe -show_data_hash sha256 vs FFmpeg -c:v copy -f framehash -hash sha256"}
    save("packet-hash-equivalence.json", receipt)
    return receipt


def verify_video():
    stamp = stable_output()
    job = settings()
    master = Path(job["master"])
    require(digest(master) == job["master_sha256"], "Master changed")
    source_packets = packet_rows(master)
    require(len(source_packets) == UNIT_FRAMES, "Wrong source packet count")
    equivalence = verify_packet_hash_equivalence()
    data = probe(OUTPUT)
    stream = check_video_stream(data, SECONDS)
    timebase = Fraction(stream["time_base"])
    count, mismatches = 0, 0
    E.mkdir(parents=True, exist_ok=True)
    print("Reading original final-video packet timings and SHA256 payloads in one FFprobe pass", flush=True)
    packets, final_hashes = probe_packet_hashes(OUTPUT, "all-video-packets")
    require(len(packets) == len(final_hashes) == FRAMES, "Final packet count mismatch")
    for packet, payload in zip(packets, final_hashes):
        expected = Fraction(count, FPS)
        require(int(packet["pts"]) * timebase == int(packet["dts"]) * timebase == expected,
                "Noncontiguous original MP4 PTS/DTS at frame " + str(count))
        require(int(packet["duration"]) * timebase == Fraction(1, FPS), "Wrong original packet duration")
        if count >= 60 * FPS:
            require(payload == source_packets[count % UNIT_FRAMES], "Clean picture payload changed at frame " + str(count))
        elif payload != source_packets[count]:
            mismatches += 1
        count += 1
        if count % 18000 == 0:
            print(f"All packet payloads/timestamps checked: {count // 1800}/60 minutes", flush=True)
    require(count == FRAMES and mismatches > 0, "Wrong frame count or missing opening")
    evidence = json.loads(Path(job["master_validation"]).read_text(encoding="utf-8"))
    require(evidence["status"] == "passed" and evidence["sha256"] == job["master_sha256"], "Master evidence mismatch")
    original = master_frames(master, evidence)
    print("Decoding the first60s opening and one complete clean600s unit", flush=True)
    branded = frame_digests(OUTPUT, 0, 60, "opening")
    clean = frame_digests(OUTPUT, UNIT, UNIT, "first-clean")
    require(len(original) == len(clean) == UNIT_FRAMES and len(branded) == 60 * FPS, "Decoded picture count mismatch")
    require(clean == original, "First complete clean unit differs from master")
    require(branded[22 * FPS:] == original[22 * FPS:60 * FPS], "Pictures changed after title clearance")
    require(any(a != b for a, b in zip(branded[:22 * FPS], original[:22 * FPS])), "Opening graphics absent")
    require(abs(float(data["format"]["duration"]) - SECONDS) < 0.04, "Wrong container duration")
    audio = [stream for stream in data["streams"] if stream["codec_type"] == "audio"]
    require(len(audio) == 1 and audio[0]["codec_name"] == "aac" and audio[0]["sample_rate"] == "48000" and audio[0]["channels"] == 2,
            "Wrong final audio properties")
    stamp_matches(stamp)
    save("video-validation.json", {"status": "passed", "output_stamp": stamp, "frames": count,
                                   "all_pts_dts_exact_30fps": True, "all_packet_durations_exact": True,
                                   "all_original_demuxed_mp4_pts_dts_durations_exact": True,
                                   "packet_read_method": "One FFprobe JSON demux pass for original timings and SHA256 payloads",
                                   "packet_hash_equivalence": "packet-hash-equivalence.json",
                                   "all_packets_after_first60s_match_600s_master_phase": True,
                                   "complete_clean_600s_copies": 5, "first_cycle_untouched_tail_seconds": 540,
                                   "first_clean_unit_all_decoded_frames_match_master": True,
                                   "opening_after22s_all_decoded_frames_match_master": True,
                                   "intro_present_once": True, "dimensions": [3840, 2160], "fps": FPS, "probe": data})


def read_exact(stream, length):
    chunks, count = [], 0
    while count < length:
        piece = stream.read(length - count)
        if not piece:
            break
        chunks.append(piece)
        count += len(piece)
    return b"".join(chunks)


def verify_audio():
    stamp = stable_output()
    require(digest(AUDIO) == AUDIO_SHA256, "Approved audio changed")
    # Independent reference omits Colony's inactive safety limiter. This checks
    # the approved FLAC plus ONLY the once-only opening envelope, at unity.
    graph = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,afade=t=in:st=5:d=15:curve=hsin"
    count = 0
    peak = first = sxx = syy = sxy = error = 0.0
    windows, minute_rows = [], []
    minute_xx = minute_yy = minute_xy = 0.0
    E.mkdir(parents=True, exist_ok=True)
    expected_log, actual_log = E / "expected-audio.log", E / "actual-audio.log"
    with expected_log.open("wb") as e1, actual_log.open("wb") as e2:
        p = subprocess.Popen([FF, "-v", "error", "-i", str(AUDIO), "-af", graph, "-t", str(SECONDS),
                              "-ac", "2", "-ar", "48000", "-f", "f32le", "pipe:1"], stdout=subprocess.PIPE, stderr=e1)
        q = subprocess.Popen([FF, "-v", "error", "-i", str(OUTPUT), "-vn", "-t", str(SECONDS),
                              "-ac", "2", "-ar", "48000", "-f", "f32le", "pipe:1"], stdout=subprocess.PIPE, stderr=e2)
        try:
            for sec in range(SECONDS):
                ar, br = read_exact(p.stdout, 48000 * 2 * 4), read_exact(q.stdout, 48000 * 2 * 4)
                require(len(ar) == len(br) == 48000 * 2 * 4, "Audio ends early at " + str(sec))
                a = np.frombuffer(ar, "<f4").astype(np.float64)
                b = np.frombuffer(br, "<f4").astype(np.float64)
                require(np.isfinite(a).all() and np.isfinite(b).all(), "Nonfinite audio")
                peak = max(peak, float(np.max(np.abs(b))))
                require(peak < 1, "Clipped final AAC")
                if sec < 4:
                    first = max(first, float(np.max(np.abs(b))))
                ax, by, xy = float(np.sum(a * a)), float(np.sum(b * b)), float(np.sum(a * b))
                sxx += ax
                syy += by
                sxy += xy
                error += float(np.sum((a - b) ** 2))
                minute_xx += ax
                minute_yy += by
                minute_xy += xy
                count += 48000
                if sec in (4, 5, 10, 15, 19, 20, 45, 90, 270, 300, 526, 600, 1800, 3579, 3580, 3590, 3599):
                    gain = 10 * math.log10(max(by, 1e-30) / max(ax, 1e-30)) if ax > 0 else None
                    corr = xy / math.sqrt(max(ax * by, 1e-30)) if ax > 0 else None
                    if sec >= 5:
                        require(abs(gain) < .35 and corr > .98, "Wrong gain/fade at " + str(sec))
                    windows.append({"second": sec, "expected_rms": math.sqrt(ax / len(a)), "aac_rms": math.sqrt(by / len(b)),
                                    "correlation": corr, "gain_difference_db": gain, "reference_silent": ax == 0})
                if sec % 60 == 59:
                    gain = 10 * math.log10(minute_yy / minute_xx)
                    corr = minute_xy / math.sqrt(minute_xx * minute_yy)
                    require(abs(gain) < .2 and corr > .99, "Minute gain/correlation failed: " + str(sec // 60))
                    minute_rows.append({"minute": sec // 60, "gain_difference_db": gain, "correlation": corr})
                    minute_xx = minute_yy = minute_xy = 0.0
                if sec % 600 == 599:
                    print(f"Complete AAC comparison: {(sec + 1) // 60}/60 minutes", flush=True)
            require(not p.stdout.read(1) and not q.stdout.read(1), "Extra decoded audio beyond expected duration")
            require(p.wait() == q.wait() == 0 and count == 172800000, "Full audio decode failed")
        finally:
            for process in (p, q):
                if process.poll() is None:
                    process.kill()
                    process.wait()
    require(expected_log.stat().st_size == actual_log.stat().st_size == 0, "Audio decode errors")
    corr, gain, snr = sxy / math.sqrt(sxx * syy), 10 * math.log10(syy / sxx), 10 * math.log10(sxx / error)
    require(first < 1e-6 and corr > .995 and abs(gain) < .15 and snr > 25, "Complete AAC/reference comparison failed")
    stamp_matches(stamp)
    save("audio-validation.json", {"status": "passed", "output_stamp": stamp, "seconds": SECONDS,
                                   "sample_frames": count, "all_samples_finite": True, "unclipped": True,
                                   "peak_dbfs": 20 * math.log10(peak), "source_audio": str(AUDIO), "source_sha256": AUDIO_SHA256,
                                   "expected_graph": graph, "actual_colony_graph_input0": expected_audio_graph(),
                                   "new_gain_db": 0, "additional_sfx": False, "new_closing_fade": False,
                                   "existing_source_closing_fade_seconds": 20, "opening_silence_to5_fade_to20_once": True,
                                   "first_four_seconds_peak": first, "full_track_correlation": corr,
                                   "gain_difference_db": gain, "aac_snr_db": snr,
                                   "diagnostic_windows": windows, "all_minute_checks": minute_rows,
                                   "note": "Compared to approved source plus opening envelope only; no continuous listening claimed"})


def stills():
    times = [1, 6, 13, 16, 19, 23, 59, 60, 87, 197, 397, 599, 600, 601, 1199, 3599]
    sheet = Image.new("RGB", (1280, 8 * 390), "#11151b")
    draw = ImageDraw.Draw(sheet)
    for index, sec in enumerate(times):
        target = H / "stills" / f"final-{sec:04}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            run([FF, "-v", "error", "-n", "-ss", str(sec), "-i", str(OUTPUT), "-frames:v", "1",
                 "-vf", "scale=1280:720:flags=lanczos", str(target)])
        with Image.open(target) as image:
            reduced = image.convert("RGB").resize((640, 360), Image.Resampling.LANCZOS)
        x, y = (index % 2) * 640, (index // 2) * 390
        sheet.paste(reduced, (x, y))
        draw.text((x + 10, y + 365), f"{sec}s", fill="#F3EBDD")
    sheet.save(H / "final-contact-sheet.jpg", quality=94)
    save("visual-review-preparation.json", {"stills": "final-contact-sheet.jpg", "times_seconds": times,
                                            "status": "Prepared for actual visual inspection; continuous playback not inferred"})


def container_hash():
    stamp = stable_output()
    value = digest(OUTPUT)
    stamp_matches(stamp)
    save("container-hash.json", {"path": str(OUTPUT), **stamp, "sha256": value, "stable_during_read": True})


def review():
    stamp = stable_output()
    target = H / "Crater-Rim-Survey-final-opening-and-scene-135s-720p.mp4"
    require(not target.exists(), "Review already exists; preserve it and use its validation record")
    run([FF, "-v", "error", "-nostdin", "-n", "-i", str(OUTPUT), "-t", "135", "-map", "0:v:0", "-map", "0:a:0",
         "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-bf", "0",
         "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(target)])
    data = probe(target)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    require((video["width"], video["height"], video["r_frame_rate"], int(video["nb_frames"])) == (1280, 720, "30/1", 4050), "Wrong review format")
    require(abs(float(data["format"]["duration"]) - 135) < .04, "Wrong review duration")
    decoded = run([FF, "-v", "error", "-xerror", "-err_detect", "explode", "-i", str(target), "-f", "null", "-"])
    require(not decoded.stderr, "Review decode errors")
    totals = [0.0, 0.0, 0.0, 0.0]
    E.mkdir(parents=True, exist_ok=True)
    with (E / "review-source-audio.log").open("wb") as e1, (E / "review-audio.log").open("wb") as e2:
        processes = [subprocess.Popen([FF, "-v", "error", "-i", str(path), "-t", "135", "-vn", "-ac", "2", "-ar", "48000",
                                       "-f", "f32le", "pipe:1"], stdout=subprocess.PIPE, stderr=err)
                     for path, err in ((OUTPUT, e1), (target, e2))]
        try:
            for sec in range(135):
                chunks = [read_exact(process.stdout, 48000 * 2 * 4) for process in processes]
                require(all(len(chunk) == 48000 * 2 * 4 for chunk in chunks), "Review audio length mismatch")
                a, b = [np.frombuffer(chunk, "<f4").astype(np.float64) for chunk in chunks]
                require(np.isfinite(a).all() and np.isfinite(b).all(), "Nonfinite review audio")
                totals[0] += float(np.sum(a * a))
                totals[1] += float(np.sum(b * b))
                totals[2] += float(np.sum(a * b))
                totals[3] += float(np.sum((a - b) ** 2))
            require(all(not process.stdout.read(1) for process in processes), "Extra review samples")
            require(all(process.wait() == 0 for process in processes), "Review audio decode failure")
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait()
    require((E / "review-source-audio.log").stat().st_size == (E / "review-audio.log").stat().st_size == 0,
            "Review audio decode errors")
    xx, yy, xy, ee = totals
    corr, gain, snr = xy / math.sqrt(xx * yy), 10 * math.log10(yy / xx), 10 * math.log10(xx / ee)
    require(corr > .995 and abs(gain) < .15 and snr > 25, "Review audio differs from actual final excerpt")
    stamp_matches(stamp)
    save("review-validation.json", {"status": "passed", "path": str(target), "bytes": target.stat().st_size, "sha256": digest(target),
                                    "source": str(OUTPUT), "source_output_stamp": stamp, "source_seconds": [0, 135],
                                    "seconds": 135, "frames": 4050, "dimensions": [1280, 720], "fps": 30,
                                    "full_video_audio_decode": True, "sample_frames": 6480000,
                                    "audio_correlation_with_actual_final": corr, "audio_gain_difference_db": gain, "audio_snr_db": snr,
                                    "opening_and_sound": "Actual completed final's first135s; no new fade or graphics added"})


def finish():
    job = settings()
    video = json.loads((H / "video-validation.json").read_text())
    audio = json.loads((H / "audio-validation.json").read_text())
    colony = json.loads((H / "colony-export.json").read_text())
    hashed = json.loads((H / "container-hash.json").read_text())
    master = json.loads(Path(job["master_validation"]).read_text())
    require(video["status"] == audio["status"] == master["status"] == "passed", "A required verification failed")
    require(colony["verification"]["full_decode"] and colony["verification"]["passed"], "Actual Colony full decode did not pass")
    require(all(check["ok"] for check in colony["verification"]["checks"]), "Incomplete Colony verification")
    for stamp in (video["output_stamp"], audio["output_stamp"], {key: hashed[key] for key in ("bytes", "mtime_ns")}):
        stamp_matches(stamp)
    require(digest(AUDIO) == AUDIO_SHA256 and digest(Path(job["master"])) == master["sha256"] == job["master_sha256"], "Inputs changed")
    verify_engine()
    save("delivery-validation.json", {"status": "passed", "completed_date": time.strftime("%Y-%m-%d"),
                                      "output": str(OUTPUT), "bytes": hashed["bytes"], "sha256": hashed["sha256"],
                                      "seconds": SECONDS, "frames": FRAMES, "dimensions": [3840, 2160], "fps": FPS,
                                      "native_artwork_dimensions": [1672, 941], "master": job["master"], "master_sha256": master["sha256"],
                                      "audio_source_sha256": AUDIO_SHA256, "source_audio_unchanged": True,
                                      "colony_full_video_audio_decode": True,
                                      "video_validation": "video-validation.json", "audio_validation": "audio-validation.json",
                                      "opening": "Actual frozen Colony v3 once within hour; graphics clear22s, silence0-5 and fade5-20",
                                      "closing_audio": "Existing approved20s fade retained; none added",
                                      "new_audio_gain_db": 0, "extra_sfx": False,
                                      "clean_600s_repeats_after_opening_cycle": 5,
                                      "full_combined_user_review": "pending", "assistant_listening": "not performed",
                                      "publication": "not inferred", "remote_backup": False})
    print("Final one-hour4K Crater Rim technical delivery verified", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("video", "audio", "stills", "hash", "review", "finish"):
        parser.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    if args.video:
        verify_video()
    if args.audio:
        verify_audio()
    if args.stills:
        stills()
    if args.hash:
        container_hash()
    if args.review:
        review()
    if args.finish:
        finish()
