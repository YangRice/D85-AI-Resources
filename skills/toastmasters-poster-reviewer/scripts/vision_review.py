"""Model-fed visual measurements. No OCR, external model or network calls.

The checker measures selected logo/color/copy features from image observations.
A selected-scope PASS is not whole-brand PASS.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

FORMAT = 'tm-poster-vision-check/v1'
RULES = json.loads(Path(__file__).with_name('brand_rules.json').read_text(encoding='utf-8'))
LOGO_KEYS = {'logo_detection':'detection', 'logo_geometry':'geometry',
             'logo_appearance':'appearance', 'logo_clear_space':'clear_space',
             'logo_effects':'effects', 'logo_size':'size'}
PAGES = {'logo_detection':[8,9,21], 'logo_geometry':[12], 'logo_appearance':[12],
         'logo_clear_space':[8,9,21,28], 'logo_effects':[12], 'logo_size':[8,9,21],
         'design_palette':[14,15,16,17,18,20], 'tagline':[29], 'marketing_phrases':[29]}


def load_module(name):
    spec = importlib.util.spec_from_file_location('tm_'+name, Path(__file__).with_name(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def template():
    return dict(format=FORMAT, rule_set=RULES['rule_set'], candidate_sha256=None,
                producer=dict(method='model-image-observation', model_id=None),
                target_width_px=None, requested_checks=['logo_detection','logo_geometry',
                'logo_appearance','logo_clear_space','design_palette'], logos=[],
                colors=dict(include=[],exclude=[],inventory_complete=False),
                text_runs=[], text_inventory_complete=False)


def inspect(image, spec, root, candidate):
    from PIL import Image
    if spec.get('rule_set') != RULES['rule_set']:
        raise ValueError('Unsupported vision rule set')
    if spec.get('candidate_sha256') != sha(candidate):
        raise ValueError('Vision observations must identify the actual candidate file')
    requested = spec.get('requested_checks')
    if (not isinstance(requested, list) or not requested or len(set(requested)) != len(requested)
            or any(k not in PAGES for k in requested)):
        raise ValueError('Supply a nonempty unique list of supported requested_checks')
    logos = spec.get('logos', [])
    if not isinstance(logos, list) or any(not isinstance(v, dict) for v in logos):
        raise ValueError('logos must be a list of observations')
    identifiers = [l.get('id') for l in logos]
    if any(not isinstance(i,str) or not i for i in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ValueError('Each logo observation needs a unique id')
    findings, details, evidence = [], [], {}
    def add(check, status, reason, **extra):
        if check in requested:
            findings.append(dict(check=check,status=status,reason=reason,
                manual_pages=PAGES[check], evidence_basis='image measurement with supplied model/source regions', **extra))
    for index, logo in enumerate(logos):
        raw = logo.get('references', [logo['reference']] if logo.get('reference') else [])
        if not isinstance(raw, list) or len(raw) > 12:
            raise ValueError('Supply at most 12 reference variants per logo')
        hypotheses = []
        for source in raw:
            # A measurement belongs to its source variant. Never silently reuse
            # one variant's clear-space ratio for another variant's artwork.
            params = dict(logo)
            if isinstance(source, dict):
                if set(source) - {'path', 'wordmark_height_ratio'}:
                    raise ValueError('Unknown reference variant fields')
                source_path = source.get('path')
                params.pop('wordmark_height_ratio', None)
                if 'wordmark_height_ratio' in source:
                    params['wordmark_height_ratio'] = source['wordmark_height_ratio']
            else:
                source_path = source
            if not isinstance(source_path, str) or not source_path:
                raise ValueError('References need a path string or a variant object with path')
            path = root/source_path
            if not path.is_file():
                continue
            evidence[str(path)] = sha(path)
            with Image.open(path) as opened:
                reference = opened.convert('RGBA')
            if 'target_width_px' in spec:
                params['target_width_px'] = spec['target_width_px']
            hypothesis = load_module('logo_vision').inspect_logo(image, reference, params)
            hypothesis['reference'] = str(path)
            hypothesis['reference_name'] = path.name
            hypothesis['reference_sha256'] = evidence[str(path)]
            hypothesis['wordmark_height_ratio'] = params.get('wordmark_height_ratio')
            hypotheses.append(hypothesis)
        # Select visually consistent hypotheses first. Raw mean residuals are
        # not comparable across differently opaque variants: a sparse white
        # outline can ignore most of a colored logo and report a lower mean.
        # Prefer broader validated SIFT support before using residual as a
        # tie-break. Preserve every hypothesis so the choice is inspectable.
        def rank(h):
            detected = h.get('detection',{}).get('status') == 'PASS'
            appearance = h.get('appearance',{}).get('status')
            attempts = h.get('diagnostics',{}).get('attempts',[])
            sift = h.get('detection',{}).get('method') == 'SIFT + RANSAC homography'
            winning = attempts[-1] if sift and attempts else {}
            support = winning.get('inliers',0)*winning.get('reference_hull_fraction',0)
            h['variant_match_support'] = support
            return (detected, appearance == 'PASS', appearance != 'REVISE',
                    support,
                    -h.get('appearance',{}).get('mean_delta_e76',1e6))
        best = max(hypotheses, key=rank) if hypotheses else {}
        details.append(dict(id=logo['id'],selected=best,hypotheses=hypotheses,
                            selection_basis='Detection and appearance status, then distributed SIFT support, then mean Lab residual',
                            source_authenticity='NOT_VERIFIED; use trusted official downloads'))
        for key, component in LOGO_KEYS.items():
            result = best.get(component, {})
            status = result.get('status','BLOCKED')
            # INFO here means effect measurement lacked a suitable backdrop,
            # not that a requested effects check is inapplicable/satisfied.
            if key == 'logo_effects' and status == 'INFO':
                status = 'BLOCKED'
            add(key,status,result.get('reason','No reliable reference/localization evidence'),
                logo=index,logo_id=logo['id'],measurement=result)
    if not logos:
        for key in LOGO_KEYS:
            add(key,'BLOCKED','No logo observation supplied; absence is not established by an empty list')
    color_result = None
    if 'design_palette' in requested:
        observation = spec.get('colors')
        if not isinstance(observation, dict):
            add('design_palette','BLOCKED','Model-selected design mask is missing')
        else:
            color_result = load_module('color_vision').inspect_colors(image, observation, RULES)
            add('design_palette',color_result['status'],color_result['reason'],measurement=color_result)
    runs = spec.get('text_runs', [])
    if not isinstance(runs,list) or any(not isinstance(r,dict) for r in runs):
        raise ValueError('text_runs must be observations')
    if 'tagline' in requested:
        relevant = [r for r in runs if r.get('role') == 'tagline']
        if not relevant:
            add('tagline','INFO' if spec.get('text_inventory_complete') is True else 'BLOCKED',
                'Official tagline is optional; no tagline observed' if spec.get('text_inventory_complete') is True else
                'No complete model transcription establishes tagline applicability')
        for run in relevant:
            clear = run.get('readability') == 'clear' and isinstance(run.get('text'), str)
            status = 'BLOCKED' if not clear else 'PASS' if run['text'] in RULES['taglines'] else 'REVISE'
            add('tagline',status,'Exact tagline comparison on model-read copy',
                text=run.get('text'),evidence_type='model observation; not independently verified transcription')
    if 'marketing_phrases' in requested:
        phrases = [r for r in runs if r.get('role') == 'marketing-phrase']
        clear = all(r.get('readability') == 'clear' and isinstance(r.get('text'),str) for r in phrases)
        invalid = [r.get('text') for r in phrases if r.get('readability')=='clear' and r.get('text') not in RULES['phrases']]
        distinct = {r['text'] for r in phrases if isinstance(r.get('text'),str) and r.get('readability')=='clear'}
        status = 'REVISE' if invalid or len(distinct)>1 else 'PASS' if clear and spec.get('text_inventory_complete') is True else 'BLOCKED'
        add('marketing_phrases',status,'Optional phrase list/count on model-classified copy; partial inventory cannot pass',
            count=len(distinct),invalid=invalid,evidence_type='model observation')
    features = {}
    for key in requested:
        statuses = [f['status'] for f in findings if f['check']==key]
        features[key] = dict(status=next((s for s in ('REVISE','BLOCKED','PASS','INFO') if s in statuses),'BLOCKED'))
    states = [f['status'] for f in features.values()]
    verdict = 'REVISE' if 'REVISE' in states else 'BLOCKED' if 'BLOCKED' in states else 'PASS'
    return dict(format='tm-poster-vision-results/v1',rule_set=RULES['rule_set'],
        candidate_sha256=sha(candidate),dimensions=list(image.size),
        producer=spec.get('producer'),requested_checks=requested,findings=findings,
        feature_results=features,scoped_verdict=verdict,
        logo_measurements=details,color_measurement=color_result,
        reference_file_sha256=evidence,
        scope='Only requested image measurements and model-read copy; not all manual requirements',
        limitations=['Model region/copy semantics are not independently established',
                     'Engineering thresholds are disclosed screening choices, not official brand exemptions',
                     'No external OCR, model call or source-audit prerequisite in this route'])
