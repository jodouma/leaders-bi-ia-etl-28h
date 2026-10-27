"""Check sources, printed runnable examples, links and the public package.

Requires the authoring dependencies, never needed to follow the course.
"""
from __future__ import annotations

import ast
import copy
from contextlib import redirect_stdout
import io
import json
import shutil
import sqlite3
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BOOKS = [('setup.json', '01_demarrer_windows_ubuntu.pdf'),
         ('course.json', '02_cours_atlas_ia.pdf'),
         ('reference.json', '03_prompts_reperes_depannage.pdf'),
         ('challenge.json', '04_defi_campus_box.pdf'),
         ('solutions.json', '05_indices_et_corriges.pdf')]


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


def equivalent_function(snippet, complete):
    wanted = ast.parse(snippet).body[0]
    actual = next(node for node in ast.parse(complete).body
                  if isinstance(node, ast.FunctionDef) and node.name == wanted.name)
    actual = copy.deepcopy(actual)
    if actual.body and isinstance(actual.body[0], ast.Expr) and isinstance(actual.body[0].value, ast.Constant) and isinstance(actual.body[0].value.value, str):
        actual.body = actual.body[1:]
    return ast.dump(wanted, include_attributes=False) == ast.dump(actual, include_attributes=False)


def run_reference_examples(examples, sql, snippets):
    results=[]
    with tempfile.TemporaryDirectory(prefix='atlas-pdf-reference-') as folder:
        temporary=Path(folder)
        # Explicit reference run: construct the legitimate stage-05 artifacts
        # in order. This is not the independent first learner attempt.
        shutil.copytree(ROOT/'solutions'/'atlas',temporary/'projet',ignore=shutil.ignore_patterns('outputs','__pycache__'))
        shutil.copytree(ROOT/'projet'/'data',temporary/'projet'/'data')
        for module in ['calcul.py','lecture.py','nettoyage.py','modele.py','chargement.py']:
            result=subprocess.run([sys.executable,str(temporary/'projet'/module)],cwd=temporary,text=True,capture_output=True,timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)
        for relative, printed in examples.items():
            target=temporary/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(printed,encoding='utf-8')
            result=subprocess.run([sys.executable,str(target)],cwd=folder,text=True,capture_output=True,timeout=30)
            if result.returncode:
                raise RuntimeError(f'{relative}: {result.stderr}')
            results.append({'example':relative,'exit':0,'stdout':result.stdout.strip()})
        base=temporary/'projet'/'outputs'/'atlas.sqlite'
        with sqlite3.connect(base) as connection:
            for relative, printed in sql.items():
                rows=connection.execute(printed).fetchall()
                if relative.endswith('controle_global.sql'):
                    assert rows == [(12,32,99000)]
                results.append({'query':relative,'state':'after_05','rows':rows})
        for label, printed in snippets:
            namespace={'__name__':'pdf_example'}
            captured=io.StringIO()
            with redirect_stdout(captured):
                exec(compile(printed,'<printed PDF>','exec'),namespace)
            if 'calculer_total' in namespace:
                function=namespace['calculer_total']
                assert function([{'quantity':2,'unit_price_millimes':4500},{'quantity':3,'unit_price_millimes':1500}])==13500
                assert function([{'quantity':3,'unit_price_millimes':4500},{'quantity':3,'unit_price_millimes':1500}])==18000
            results.append({'snippet':label,'executed':True,'stdout':captured.getvalue().strip()})
        for module in ['incremental.py','rapport.py']:
            result=subprocess.run([sys.executable,str(temporary/'projet'/module)],cwd=folder,text=True,capture_output=True,timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)
        target=temporary/'docs/exemples/08_sql.py'
        result=subprocess.run([sys.executable,str(target)],cwd=folder,text=True,capture_output=True,timeout=30)
        assert result.returncode==0 and '(14, 35, 115500)' in result.stdout
        results.append({'example':'docs/exemples/08_sql.py','state':'after_06','stdout':result.stdout.strip()})
    return results


def main():
    errors=[]
    checks=[]
    examples={}
    queries={}
    snippets=[]
    panels=0
    for source,pdf in BOOKS:
        data=json.loads((HERE/'content'/source).read_text(encoding='utf-8'))
        reader=PdfReader(ROOT/'pdf'/pdf)
        pages=[page.extract_text() or '' for page in reader.pages]
        extracted='\n'.join(pages)
        if '\ufffd' in extracted or '\u25a0' in extracted:
            errors.append(f'{pdf}: possible missing glyph')
        checks.append({'pdf':pdf,'pages':len(reader.pages)})
        for page in data['pages']:
            for block in page['blocks']:
                if block['type']!='code':
                    continue
                panels+=1
                printed=find_printed(block['text'],pages)
                if printed is None:
                    errors.append(f'Printed panel differs: {pdf}: {page["title"]}')
                    continue
                relative=block.get('source')
                if relative:
                    path=ROOT/relative
                    if not path.is_file():
                        errors.append('Missing source: '+relative)
                        continue
                    complete=path.read_text(encoding='utf-8')
                    if relative=='solutions/atlas/lecture.py':
                        if not equivalent_function(block['text'],complete):
                            errors.append('Printed function differs semantically: '+relative)
                        # Excerpt declares imports already provided; exercise it.
                        namespace={}
                        exec('import csv\nfrom pathlib import Path\n'+printed,namespace)
                        with tempfile.TemporaryDirectory() as folder:
                            sample=Path(folder)/'sample.csv'
                            sample.write_text('a,b\n1,002\n',encoding='utf-8')
                            assert namespace['lire_csv'](sample)==[{'a':'1','b':'002'}]
                    elif canonical(block['text']) not in canonical(complete):
                        errors.append('Source differs: '+relative)
                    if relative.startswith('docs/exemples/'):
                        examples[relative]=printed
                    if relative.endswith('.sql'):
                        queries[relative]=printed
                elif block.get('label','').startswith('Python'):
                    snippets.append((block['label'],printed))
        for page in reader.pages:
            for ref in page.get('/Annots',[]):
                action=ref.get_object().get('/A',{})
                uri=str(action.get('/URI',''))
                if uri.endswith(('.html.','.pdf.')):
                    errors.append('Trailing punctuation in PDF link: '+uri)
    if not errors:
        checks.extend(run_reference_examples(examples,queries,snippets))
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if target.startswith(('https://','http://','#')):
                continue
            if not (path.parent/target.split('#')[0]).exists():
                errors.append(f'Broken Markdown link: {path.relative_to(ROOT)} -> {target}')
    forbidden=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts:
            continue
        if any(word in path.name.lower() for word in ['private_guide','critic-receipt','student-rankings','deliberation','formateur']):
            forbidden.append(str(path.relative_to(ROOT)))
    if forbidden:
        errors.append('Private files in student repository: '+', '.join(forbidden))
    print(json.dumps({'printed_panels':panels,'checks':checks,'errors':errors},ensure_ascii=False,indent=2))
    if errors:
        raise SystemExit(1)


if __name__=='__main__':
    main()
