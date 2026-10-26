"""Create the student ZIP from an explicit public root, excluding runtime files.

Run from any folder. The private sibling formateur/ is never traversed.
"""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT.parent / 'livraison' / 'Atlas_ETL_28h_etudiants.zip'
EXCLUDED = {'.git', '__pycache__', '.DS_Store', '.venv', 'node_modules',
            'outputs', 'renders', 'pdf_layout_report.json'}


def main():
    files = sorted(p for p in ROOT.rglob('*') if p.is_file()
                   and not any(part in EXCLUDED for part in p.relative_to(ROOT).parts)
                   and p.suffix != '.pyc')
    private_markers = ['private_guide', 'guide_formateur', 'student-rankings',
                       'critic-receipt', 'deliberation']
    assert not any(any(marker in p.name.lower() for marker in private_markers)
                   for p in files), 'Private file inside student export'
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(DEST, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path('atlas-etl') / path.relative_to(ROOT))
    print(json.dumps({'archive':str(DEST),'files':len(files),
                      'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest()},
                     ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
