"""Verify the supplied route and code actually printed in the student PDFs.

--runtime-only uses only the standard library (also used by native CI).
The full check additionally requires authoring/requirements.txt. Reference
execution is automated evidence, never a student pilot or a GUI/account test.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import closing
import copy
import csv
import hashlib
import json
import io
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tokenize

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
BOOKS = [("setup.json", "01_demarrer_windows_ubuntu.pdf"),
         ("course.json", "02_cours_atlas_ia.pdf"),
         ("reference.json", "03_prompts_reperes_depannage.pdf"),
         ("challenge.json", "04_defi_atlas.pdf"),
         ("solutions.json", "05_indices_et_corriges.pdf")]
TABLES = {"dim_product": ("product_key", "product_id", "product_name"),
          "dim_shop": ("shop_key", "shop_id", "shop_name", "commercial_zone", "valid_from", "valid_to"),
          "dim_date": ("date_key", "full_date", "year", "month", "day"),
          "fact_sales": ("sale_id", "date_key", "product_key", "shop_key", "quantity", "unit_price_millimes", "amount_millimes")}
FUNCTION_STAGES = {"normaliser_vente": (1, 2), "lire_increment_sql": (2, 3),
                   "trouver_shop_key": (4, 5)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(arguments, cwd):
    result = subprocess.run(arguments, cwd=cwd, env=PYTHON_ENV, text=True,
                            encoding="utf-8", capture_output=True, timeout=90)
    require(result.returncode == 0,
            f"{arguments} in {cwd}:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def checkpoint(root, destination, number=7):
    run([sys.executable, str(root / "outils/jalon.py"), f"{number:02d}", str(destination)], root)
    require(not list((destination / "outputs").iterdir()), "Checkpoint preloads outputs")
    return destination


def action(atelier, name):
    return json.loads(run([sys.executable, "executer.py", name], atelier))


def database_rows(base):
    with closing(sqlite3.connect(base)) as conn:
        require(conn.execute("PRAGMA foreign_key_check").fetchall() == [], "Broken foreign keys")
        return {table: conn.execute(f"SELECT * FROM {table} ORDER BY {columns[0]}").fetchall()
                for table, columns in TABLES.items()}


def assert_state(base, expected):
    with closing(sqlite3.connect(base)) as conn:
        actual = conn.execute("SELECT COUNT(*), SUM(quantity), SUM(amount_millimes) FROM fact_sales").fetchone()
        require(actual == expected, f"Warehouse totals: {actual} != {expected}")
    return database_rows(base)


def check_delivery(base, directory):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    require(set(manifest["files"]) == {f"{t}.csv" for t in TABLES}, "Manifest must name exactly four tables")
    expected = database_rows(base)
    for table, columns in TABLES.items():
        path = directory / f"{table}.csv"
        raw = path.read_bytes()
        require(raw.startswith(b"\xef\xbb\xbf"), f"Missing UTF-8 BOM: {path.name}")
        info = manifest["files"][path.name]
        require(hashlib.sha256(raw).hexdigest() == info["sha256"], f"Export hash: {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream)
            require(next(reader) == list(columns), f"Export columns: {path.name}")
            rows = list(reader)
        require(rows == [["" if value is None else str(value) for value in row]
                         for row in expected[table]], f"Export values/order: {path.name}")
        require(info["rows"] == len(rows), f"Manifest count: {path.name}")
    return {"export": "four CSV round-trip", "rows": {t: len(v) for t, v in expected.items()}}


def check_runtime(root):
    checks = []
    with tempfile.TemporaryDirectory(prefix="atlas-route-") as folder:
        temporary = Path(folder)
        for number in range(1, 8):
            atelier = checkpoint(root, temporary / f"jalon {number:02d}", number)
            output = run([sys.executable, "verifier.py", f"{number:02d}"], atelier)
            require(not list((atelier / "outputs").iterdir()), "Verifier changed learner outputs")
            checks.append({"checkpoint": f"{number:02d}", "stdout": output})
        atelier = checkpoint(root, temporary / "reference complete")
        initial = action(atelier, "initial")
        base = atelier / "outputs/atlas.sqlite"
        require(tuple(initial[k] for k in ("raw", "accepted", "rejected", "duplicate")) == (16, 12, 3, 1), "Initial quality receipt")
        assert_state(base, (12, 32, 99000))
        increment = action(atelier, "increment")
        require(tuple(increment[k] for k in ("inserted", "existing", "new_shop_versions")) == (2, 1, 1), "Increment receipt")
        before = assert_state(base, (14, 35, 115500))
        replay = action(atelier, "increment")
        require(tuple(replay[k] for k in ("inserted", "existing", "new_shop_versions")) == (0, 3, 0), "Replay receipt")
        require(database_rows(base) == before, "Replay changed keys or values")
        report = action(atelier, "rapport")
        require(report["zone_amounts_millimes"] == {"Cap Bon": 43500, "Grand Tunis": 72000}, "Historical zones")
        delivery = Path(action(atelier, "export")["delivery"])
        checks.extend([{"reference_sequence": ["initial", "increment", "increment", "rapport", "export"],
                        "initial": initial, "increment": increment, "replay": replay},
                       check_delivery(base, delivery)])
        checks.append({"all_checkpoints": run([sys.executable, "verifier.py", "tout"], atelier)})
    return checks


def canonical(text):
    # Keep leading spaces, punctuation and Unicode code points unchanged.
    return "\n".join(line.rstrip() for line in text.splitlines()).strip("\n")


def find_printed(code, pages):
    """Match actual extracted glyphs and indentation, ignoring blank separators.

    The renderer omits empty textLine glyphs. Blank lines inside multiline string
    literals are rejected, since they cannot safely be reconstructed this way.
    """
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            if token.type == tokenize.STRING:
                require(not re.search(r"\n[ \t]*\n", token.string),
                        "A multiline string contains a blank line PDF extraction cannot recover")
    except (tokenize.TokenError, IndentationError):
        pass  # Non-Python panels still receive the exact glyph comparison.
    wanted = [line.rstrip() for line in code.splitlines() if line.strip()]
    for text in pages:
        lines = [line.rstrip() for line in text.splitlines() if line.strip()]
        for start in range(len(lines) - len(wanted) + 1):
            actual = lines[start:start + len(wanted)]
            if actual == wanted:
                return "\n".join(actual) + "\n"
    raise ValueError("Printed panel differs in characters or indentation: " + code[:80])


def function_ast(node):
    node = copy.deepcopy(node)
    if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
        node.body.pop(0)
    return ast.dump(node, include_attributes=False)


def source_matches(printed, complete):
    try:
        nodes = ast.parse(printed).body
    except SyntaxError:
        return canonical(printed) in canonical(complete)
    functions = [n for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not functions:
        return canonical(printed) in canonical(complete)
    originals = {n.name: n for n in ast.parse(complete).body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return all(n.name in originals and function_ast(n) == function_ast(originals[n.name])
               for n in functions)


def execute_function(root, printed, source, temporary):
    nodes = ast.parse(printed).body
    require(len(nodes) == 1 and isinstance(nodes[0], ast.FunctionDef),
            f"Expected one complete printed function: {source}")
    function = nodes[0]
    require(function.name in FUNCTION_STAGES,
            f"Function panel needs an explicit execution case: {source}:{function.name}")
    stage, verifier = FUNCTION_STAGES[function.name]
    atelier = checkpoint(root, temporary / "function", stage)
    target = atelier / Path(source).name
    starter = target.read_text(encoding="utf-8")
    lines = starter.splitlines(keepends=True)
    original = next(n for n in ast.parse(starter).body
                    if isinstance(n, ast.FunctionDef) and n.name == function.name)
    # Replace only the exact printed function. Imports, helpers and constants
    # come from the real starter, never a preloaded solution module.
    lines[original.lineno - 1:original.end_lineno] = [printed + "\n"]
    target.write_text("".join(lines), encoding="utf-8")
    return run([sys.executable, "verifier.py", f"{verifier:02d}"], atelier)


def prepared_reference(root, temporary, state="final"):
    atelier = checkpoint(root, temporary / "atelier")
    action(atelier, "initial")
    if state == "final":
        action(atelier, "increment")
    else:
        require(state == "initial", "Unknown snippet state: " + state)
    return atelier


def execute_python(root, block, printed, temporary):
    source = block.get("source", "")
    if source.startswith("solutions/atlas/"):
        return execute_function(root, printed, source, temporary)
    atelier = prepared_reference(root, temporary, block.get("state", "initial"))
    if block.get("fixture") == "source_connection":
        # This context is explicitly declared in the book, using the genuine
        # supplied connection helper and SQL constant, not substitute objects.
        prefix = ("from lecture import connexion_source, SQL_VENTES, DATA\n"
                  "conn = connexion_source(DATA / 'source_operationnelle.sqlite')\n"
                  "batch_id = '2026-01-08'\ntry:\n")
        script = prefix + "\n".join("    " + line for line in printed.splitlines()) + "\nfinally:\n    conn.close()\n"
    else:
        script = "\n".join(block.get("prerequisites", [])) + "\n" + printed
    if source.startswith("docs/exemples/"):
        target = temporary / source
        target.parent.mkdir(parents=True, exist_ok=True)
        # Legacy example paths explicitly use projet/ relative to docs/.
        shutil.copytree(atelier, temporary / "projet")
    else:
        target = atelier / "exemple_imprime.py"
    target.write_text(script, encoding="utf-8")
    output = run([sys.executable, str(target)], atelier)
    if "expected_stdout" in block:
        require(output == block["expected_stdout"].strip(), "Python output differs: " + output)
    return output


def execute_sql(root, block, printed, temporary):
    atelier = prepared_reference(root, temporary, block.get("state", "initial"))
    base = (atelier / "data/source_operationnelle.sqlite" if block.get("sql_database") == "source"
            else atelier / "outputs/atlas.sqlite")
    with closing(sqlite3.connect(base.as_uri() + "?mode=ro", uri=True)) as conn:
        before = conn.total_changes
        rows = conn.execute(printed, block.get("params", [])).fetchall()
        require(conn.total_changes == before, "SQL example wrote data")
    if "expected_rows" in block:
        require([list(r) for r in rows] == block["expected_rows"], f"SQL rows differ: {rows}")
    return rows


def execute_shell(root, block, printed, temporary):
    label = block.get("label", "")
    if "explorer.exe" in printed:
        return {"coverage": "Windows/WSL GUI transfer; requires manual execution"}
    # Installers, account login and edited path templates are checked as
    # printed text only; the receipt must not claim they ran on this host.
    lines = [line for line in printed.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    portable = all(re.match(r"^(python3\b|pwd$|cd\s|ls\b)", line) for line in lines)
    if not portable:
        return {"coverage": "setup/platform instruction; not executed", "label": label}
    if os.name == "nt":
        return {"coverage": "Linux shell; executed in Ubuntu PDF job"}
    snapshot = temporary / "cours"
    shutil.copytree(root, snapshot, ignore=shutil.ignore_patterns(".git", "outputs", "__pycache__"))
    if "outils/jalon.py" in printed:
        cwd = snapshot
    else:
        cwd = checkpoint(snapshot, temporary / "atelier")
        action(cwd, "initial")
        if block.get("state", "initial") == "final":
            action(cwd, "increment")
    # Use the literal python3 commands from the panel, bound to this verifier's
    # interpreter through PATH, so no globally installed Python is assumed.
    bin_dir = temporary / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    result = subprocess.run(["/bin/sh", "-eu", "-c", printed], cwd=cwd,
                            env={**PYTHON_ENV, "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", "")},
                            text=True, encoding="utf-8", capture_output=True, timeout=90)
    require(result.returncode == 0, f"Printed shell failed: {printed}\n{result.stdout}\n{result.stderr}")
    return {"coverage": "isolated completed reference context", "stdout": result.stdout.strip()}


def check_books(root):
    from pypdf import PdfReader
    checks, panels = [], 0
    for source, pdf in BOOKS:
        data = json.loads((root / "authoring/content" / source).read_text(encoding="utf-8"))
        reader = PdfReader(root / "pdf" / pdf)
        pages = [p.extract_text() or "" for p in reader.pages]
        require(not any("\ufffd" in t or "\u25a0" in t for t in pages), f"Missing glyph: {pdf}")
        checks.append({"pdf": pdf, "pages": len(pages)})
        for page in data["pages"]:
            for block in page["blocks"]:
                if block["type"] != "code":
                    continue
                panels += 1
                printed = find_printed(block["text"], pages)
                source_path = block.get("source")
                if source_path:
                    complete = (root / source_path).read_text(encoding="utf-8")
                    require(source_matches(printed, complete), "Source differs: " + source_path)
                label = block.get("label", "")
                language = block.get("language", "").lower()
                if not language:
                    if label.startswith("Python") or (source_path and source_path.endswith(".py")):
                        language = "python"
                    elif label.startswith("SQL") or (source_path and source_path.endswith(".sql")):
                        language = "sql"
                    elif label.startswith("Terminal"):
                        language = "shell"
                with tempfile.TemporaryDirectory(prefix="atlas-printed-") as folder:
                    temporary = Path(folder)
                    if language == "python":
                        result = execute_python(root, block, printed, temporary)
                    elif language == "sql":
                        result = execute_sql(root, block, printed, temporary)
                    elif language in ("shell", "bash"):
                        result = execute_shell(root, block, printed, temporary)
                    else:
                        result = {"coverage": "printed reference text", "language": language or "text"}
                checks.append({"panel": panels, "pdf": pdf, "section": page["title"], "result": result})
        for page in reader.pages:
            for ref in page.get("/Annots", []):
                uri = str(ref.get_object().get("/A", {}).get("/URI", ""))
                require(not uri.endswith((".html.", ".pdf.")), "Trailing punctuation in PDF URI: " + uri)
    return panels, checks


def check_package(root):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            require((path.parent / target.split("#")[0]).exists(),
                    f"Broken Markdown link: {path.relative_to(root)} -> {target}")
    forbidden = [str(p.relative_to(root)) for p in root.rglob("*")
                 if p.is_file() and ".git" not in p.parts
                 and any(word in p.name.lower() for word in
                         ("private_guide", "critic-receipt", "student-rankings", "deliberation", "formateur"))]
    require(not forbidden, "Private files in student repository: " + ", ".join(forbidden))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--runtime-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    checks, errors, panels = [], [], 0
    try:
        checks.extend(check_runtime(root))
        if not args.runtime_only:
            panels, book_checks = check_books(root)
            checks.extend(book_checks)
            check_package(root)
    except (ValueError, OSError, SyntaxError, KeyError, sqlite3.Error, subprocess.SubprocessError) as error:
        errors.append(str(error))
    print(json.dumps({"printed_panels": panels, "checks": checks, "errors": errors,
                      "limits": ["Automated reference execution only", "No Codex Free account, WSL GUI or Power BI Desktop interaction tested"]},
                     ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
