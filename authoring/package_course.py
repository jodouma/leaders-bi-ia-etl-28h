"""Crée le ZIP étudiant de l'édition Solen BI 22 h à partir d'une liste explicite de dossiers publics.

Lancer depuis n'importe quel dossier : python authoring/package_course.py
Le dossier privé formateur/ n'est jamais parcouru. Tout fichier dont le nom évoque un guide privé,
une grille, un corrigé ou un lot d'évaluation fait échouer l'archive.
"""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT.parent / 'livraison' / 'Solen_CODEX_BI_22h_etudiants.zip'
PREFIX = 'solen-codex-bi-22h'
PUBLIC = ['README.md', 'AGENTS.md', 'TESTER_LE_COURS.md', 'LICENSE', 'pdf', 'presentation', 'modele-binome',
          'prompts', 'aide-memoire', 'docs', 'authoring']
EXCLUDED_PARTS = {'.git', '.env', '__pycache__', '.DS_Store', '.venv', 'node_modules', 'outputs',
                  'renders', 'pdf_layout_report.json', '.pytest_cache'}
PRIVATE_MARKERS = ['formateur', 'jury', 'grille', 'corrige', 'solution', 'verite', 'lots-prives',
                   'guide_formateur', 'receipt', 'recu_', 'qa_']


def main():
    files = []
    for entry in PUBLIC:
        p = ROOT / entry
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files += [f for f in p.rglob('*') if f.is_file()]
    files = sorted(f for f in files if not any(part in EXCLUDED_PARTS for part in f.relative_to(ROOT).parts)
                   and f.suffix != '.pyc')
    leaks = [str(f.relative_to(ROOT)) for f in files if any(m in str(f.relative_to(ROOT)).lower() for m in PRIVATE_MARKERS)]
    # Les solutions de référence vivent hors du dépôt ; "solution" ne doit apparaître dans aucun chemin public.
    assert not leaks, 'Fichier privé dans l export étudiant : ' + ', '.join(leaks[:5])
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(DEST, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path(PREFIX) / path.relative_to(ROOT))
    print(json.dumps({'archive': str(DEST), 'files': len(files), 'bytes': DEST.stat().st_size,
                      'sha256': hashlib.sha256(DEST.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
