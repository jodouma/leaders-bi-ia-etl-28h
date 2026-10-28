"""Validate slides.json for the Solen BI 22 h deck (V7). Read-only: it never rewrites content.

Run from anywhere:  python3 authoring/slides/make_content.py
Exit code 0 = valid. Each failure names the slide id.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = HERE / "slides.json"
LAYOUTS = {"cover", "divider", "closing", "picture", "capture", "cards", "process", "table", "kpis", "mail",
           "statement", "compare", "code", "grid", "effort", "grain", "loads", "chart", "session", "sources"}
NEEDS_NOTE_DATE = {"D", "I"}  # Codex Free and sources: every note carries the verification date


def fail(msg):
    print("ÉCHEC —", msg)
    sys.exit(1)


def main():
    spec = json.loads(SOURCE.read_text(encoding="utf-8"))
    slides = spec["slides"]
    if spec.get("edition") != "V7-Solen-22h":
        fail("edition attendue : V7-Solen-22h")
    if not 70 <= len(slides) <= 90:
        fail(f"{len(slides)} diapositives (attendu 70 à 90)")
    for logo in ("authoring/assets/leaders-logo.jpeg", "authoring/assets/solen-digital-horizontal.png"):
        if not (ROOT / logo).exists():
            fail("logo absent : " + logo)
    if not (HERE / "assets/solen-digital-horizontal-1200.png").exists():
        fail("copie réduite du logo Solen absente (authoring/slides/assets/)")

    manifest = json.loads((ROOT / "authoring/visuals/manifest.json").read_text(encoding="utf-8"))
    diagrams = {a["png"] for a in manifest["assets"]}
    registre = json.loads((ROOT / "docs/images/captures/REGISTRE.json").read_text(encoding="utf-8"))
    captures = {"docs/images/captures/" + c["fichier"] for c in registre["captures"]}

    ids, sections = set(), []
    for s in slides:
        sid = s.get("id", "?")
        if sid in ids:
            fail("id en double : " + sid)
        ids.add(sid)
        if s.get("layout") not in LAYOUTS:
            fail(f"{sid} : mise en page inconnue {s.get('layout')}")
        if not s.get("title"):
            fail(f"{sid} : titre manquant")
        if not s.get("notes") or len(s["notes"]) < 40:
            fail(f"{sid} : notes du présentateur manquantes ou trop courtes")
        if s.get("section") not in "ABCDEFGHI":
            fail(f"{sid} : section inconnue")
        if s["section"] in NEEDS_NOTE_DATE and s["layout"] != "closing" and "28/10/2026" not in s["notes"] and "2026-10-28" not in s["notes"]:
            fail(f"{sid} : la note doit dater le fait (28/10/2026)")
        sections.append(s["section"])
        img = s.get("image")
        if img:
            if not (ROOT / img).exists():
                fail(f"{sid} : image absente {img}")
            if s["layout"] == "picture" and img not in diagrams:
                fail(f"{sid} : schéma hors manifeste {img}")
            if s["layout"] == "capture":
                if img not in captures:
                    fail(f"{sid} : capture absente du registre {img}")
                if not s.get("caption", "").startswith("Capture réelle, macOS"):
                    fail(f"{sid} : légende « Capture réelle, macOS » obligatoire")
        if s["layout"] == "session":
            total = sum(seg[1] for seg in s["segments"])
            pauses = [seg for seg in s["segments"] if seg[2] == "z"]
            if total != 240 or len(pauses) != 2 or any(p[1] != 10 for p in pauses):
                fail(f"{sid} : séance ≠ 240 min avec 2 pauses de 10 min")
    if sections != sorted(sections):
        fail("sections hors ordre A → I")
    if set(sections) != set("ABCDEFGHI"):
        fail("il manque une section A → I")

    sessions = [s for s in slides if s["layout"] == "session"]
    if len(sessions) != 5:
        fail("5 diapositives de séance attendues")

    charts = [s for s in slides if s["layout"] == "chart"]
    if len(charts) != 1:
        fail("un seul graphique natif attendu")
    ref = json.loads((ROOT / "modele-binome/tronc-commun/reference/attendu_lot2.json").read_text(encoding="utf-8"))
    zones = ref["agregats"]["par_zone"]
    c = charts[0]
    expected = [zones[z]["ventes_nettes_millimes"] for z in c["labels"]]
    if sorted(c["labels"]) != sorted(zones) or c["millimes"] != expected:
        fail("graphique : valeurs ≠ attendu_lot2.json agregats.par_zone")
    if sum(c["millimes"]) != ref["indicateurs"]["ventes_nettes_millimes"]:
        fail("graphique : la somme des zones ≠ ventes nettes après lot 2")

    print(f"OK — {len(slides)} diapositives, sections A → I, 5 séances de 240 min, "
          f"graphique = attendu_lot2.json ({sum(c['millimes']) / 1000:.3f} TND), images présentes.")


if __name__ == "__main__":
    main()
