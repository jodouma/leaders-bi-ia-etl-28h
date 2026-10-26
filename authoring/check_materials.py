"""Check sources, printed runnable examples, links and the public package.

Requires the authoring dependencies, never needed to follow the course.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BOOKS = [('start.json', '01_demarrer_windows.pdf'),
         ('course.json', '02_cours_atlas.pdf'),
         ('reference.json', '03_reperes_et_depannage.pdf'),
         ('solutions.json', '04_indices_et_corriges.pdf')]


def canonical(text):
    return '\n'.join(line.rstrip() for line in
                     unicodedata.normalize('NFC', text).splitlines()).strip()


def find_printed(code, pages):
    """Recover the printed lines, preserving indentation and characters.

    PDF extractors omit visually blank lines. These examples do not use blank
    lines inside string literals, so ignoring blank separators is harmless.
    """
    wanted=[line.rstrip() for line in canonical(code).splitlines() if line.strip()]
    for text in pages:
        lines=[line.rstrip() for line in canonical(text).splitlines() if line.strip()]
        for start in range(len(lines)-len(wanted)+1):
            actual=lines[start:start+len(wanted)]
            if actual==wanted:
                return '\n'.join(actual)+'\n'
    return None


def main():
    errors=[]
    checks=[]
    seen=set()
    for source,pdf in BOOKS:
        data=json.loads((HERE/source).read_text(encoding='utf-8'))
        reader=PdfReader(ROOT/'pdf'/pdf)
        pages=[page.extract_text() or '' for page in reader.pages]
        extracted='\n'.join(pages)
        if '\ufffd' in extracted or '\u25a0' in extracted:
            errors.append(f'{pdf}: possible missing glyph')
        checks.append({'pdf':pdf,'pages':len(reader.pages)})
        for page in data['pages']:
            for block in page['blocks']:
                if block['type']!='code' or not block.get('source'):
                    continue
                path=ROOT/block['source']
                code=block['text']
                if not path.is_file():
                    errors.append(f'Missing example: {path.relative_to(ROOT)}')
                    continue
                if canonical(path.read_text(encoding='utf-8'))!=canonical(code):
                    errors.append(f'Source differs from book: {block["source"]}')
                printed_code=find_printed(code,pages)
                if printed_code is None:
                    errors.append(f'Printed code differs: {pdf}: {block["source"]}')
                    continue
                if path in seen:
                    continue
                seen.add(path)
                with tempfile.TemporaryDirectory(prefix='atlas-example-') as folder:
                    printed=Path(folder)/path.name
                    printed.write_text(printed_code,encoding='utf-8')
                    result=subprocess.run([sys.executable,str(printed)],cwd=folder,
                                          text=True,capture_output=True,timeout=30)
                checks.append({'example':block['source'],'exit':result.returncode,
                               'stdout':result.stdout.strip()})
                if result.returncode:
                    errors.append(f'Example failed: {block["source"]}: {result.stderr}')
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',readme):
        if target.startswith(('https://','http://','#')):
            continue
        if not (ROOT/target).is_file():
            errors.append('Broken README link: '+target)
    forbidden=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts:
            continue
        lower=path.name.lower()
        if any(word in lower for word in ['private_guide','critic-receipt','student-rankings','deliberation','formateur']):
            forbidden.append(str(path.relative_to(ROOT)))
    if forbidden:
        errors.append('Private files in student repository: '+', '.join(forbidden))
    print(json.dumps({'checks':checks,'errors':errors},ensure_ascii=False,indent=2))
    if errors:
        raise SystemExit(1)


if __name__=='__main__':
    main()
