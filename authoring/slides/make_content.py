"""Validate and format the canonical slides.json without replacing its authored content.

slides.json is the single source of truth. This helper is deliberately lossless for
all unknown keys so that a direct JSON edit survives future runs.
"""
import json
from pathlib import Path

SOURCE = Path(__file__).with_name('slides.json')

def main():
    spec = json.loads(SOURCE.read_text(encoding='utf-8'))
    slides = spec['slides']
    assert 56 <= len(slides) <= 68, f'Nombre de diapositives inattendu : {len(slides)}'
    for number, slide in enumerate(slides, 1):
        assert slide.get('title'), f'Titre absent : {number}'
        assert slide.get('section') in 'ABCDE', f'Repère A–E absent : {number}'
        assert slide.get('layout'), f'Mise en page absente : {number}'
        if slide['layout'] == 'capture':
            for field in ('asset', 'caption', 'provenance', 'items', 'pixelSize'):
                assert slide.get(field), f'Capture {number} : champ {field} absent'
            assert len(slide['pixelSize']) == 2 and all(n > 0 for n in slide['pixelSize'])
    charts = [s for s in slides if s['layout'] == 'chart']
    assert [c['values'] for c in charts] == [[22.5, 18, 36, 22.5], [27, 18, 48, 22.5]]
    assert [sum(c['values']) for c in charts] == [99, 115.5]
    SOURCE.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(slides)} diapositives validées ; contenu JSON conservé.')

if __name__ == '__main__':
    main()
