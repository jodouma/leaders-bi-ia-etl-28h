"""Validate the V6 teaching contract without replacing authored slide content."""
import json
from pathlib import Path
SOURCE=Path(__file__).with_name("slides.json")
def main():
    spec=json.loads(SOURCE.read_text(encoding="utf-8"))
    slides=spec["slides"]
    assert spec["edition"] == "V6-15h"
    assert len(slides) >= 60
    ids=[]
    for n,s in enumerate(slides,1):
        assert s.get("title") and s.get("layout") and s.get("section") in "ABCDE",n
        ids.append(s["id"])
        if s["layout"] == "capture":
            assert all(s.get(k) for k in ["asset","caption","provenance","items","pixelSize"]),n
        if s["layout"] == "diagram":
            assert s["asset"].startswith("docs/images/diagrams/v6-"),n
    assert len(ids)==len(set(ids)), "Duplicate slide id"
    assert len([s for s in slides if s["layout"]=="schedule"])==5
    assert len([s for s in slides if s["layout"]=="pause"])==5
    chart=[s for s in slides if s["layout"]=="chart"]
    assert [(s["labels"],s["values"]) for s in chart]==[(["Cap Bon","Grand Tunis"],[43.5,72])]
    assert sum(chart[0]["values"])==115.5
    SOURCE.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{len(slides)} slides validated; 5 sessions, 5 pauses, historical zone total 115.500 TND.")
if __name__=="__main__":main()
