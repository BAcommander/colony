"""Archive our measurement charts/timelines in Git without external recordings."""
import json
from pathlib import Path

from analyze_ambient_audio import render

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'exports/reference-analysis/comparison-2026-10-30'
ARCHIVE = ROOT / 'creative/music/reference-analysis/comparison-2026-10-30'


def archive():
    comparison = json.loads((LOCAL / 'comparison.json').read_text(encoding='utf-8'))
    page = (LOCAL / 'comparison.html').read_text(encoding='utf-8')
    for track in comparison['tracks']:
        source_json = Path(track['analysis_file'])
        report = json.loads(source_json.read_text(encoding='utf-8'))
        folder = ARCHIVE / 'reports' / track['id']
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'analysis.json').write_bytes(source_json.read_bytes())
        render(report, folder / 'report.html', Path(report['source']['path']))
        import os
        old_link = Path(os.path.relpath(source_json.parent / 'report.html', LOCAL)).as_posix()
        page = page.replace('href="' + old_link + '"', 'href="reports/' + track['id'] + '/report.html"')
    trials = '../../../../exports/reference-analysis/comparison-2026-10-30/listening-trials/trials.html'
    page = page.replace('href="listening-trials/trials.html"', 'href="' + trials + '"')
    page = page.replace('<h1>', '<p>Archived measurement reports and timelines. Audio and listening-trial clips remain in the local ignored exports folder.</p><h1>', 1)
    (ARCHIVE / 'comparison.html').write_text(page, encoding='utf-8', newline='\n')
    print('Archived six reports/full timelines and comparison page; no recordings copied.')


if __name__ == '__main__':
    archive()
