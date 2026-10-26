#!/usr/bin/env python3
"""Offline poster brand measurements against the August 2026 manual."""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

RULE_SET = 'tm-poster-brand-2026-08-v1'
PALETTE = ('004165', '772432', 'A9B2B1', 'F2DF74')
GRADIENTS = (('004165', '006094'), ('3B0104', '781327'), ('A9B2B1', 'F5F5F5'))


def extended_module():
    path = Path(__file__).with_name('brand_extended.py')
    module_spec = importlib.util.spec_from_file_location('tm_brand_extended', path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def compare_logo(original, observed, background, offset=(0, 0), jpeg_settings=None):
    path = Path(__file__).with_name('logo_compare.py')
    spec = importlib.util.spec_from_file_location('tm_logo_compare', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compare(original, observed, background, offset,jpeg_settings)


def corroborate_text(image, run, root, evidence_bundle=None,jpeg_settings=None):
    path = Path(__file__).with_name('text_evidence.py')
    spec = importlib.util.spec_from_file_location('tm_text_evidence', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.corroborate(image,run,root,rect,digest,evidence_bundle,jpeg_settings)


def feature_results(findings):
    """Aggregate actual observations separately from declarative checks.

    A known defect remains visible even when another required check abstains.
    This is the benchmark-facing decision; global BLOCKED cannot hide misses.
    """
    groups = {}
    for finding in findings:
        groups.setdefault(finding['check'],[]).append(finding)
    results = {}
    for check,items in groups.items():
        states = [item.get('observed_status',item['status']) for item in items]
        status = next((s for s in ('REVISE','BLOCKED','PASS','INFO') if s in states),'BLOCKED')
        results[check] = dict(status=status,
            evidence_basis=sorted({item.get('evidence_basis','computed from supplied evidence') for item in items}),
            findings=len(items),unverified_declarations=sum(item.get('evidence_basis')=='unverified declaration' for item in items))
    return results


def template():
    return dict(format='tm-poster-brand-check/v2', rule_set=RULE_SET,
                candidate_sha256=None, context=None, document_kind='poster',
                target_width_px=None, print_width_in=None, inventory_complete=False,
                color_formulations=[], color_regions=[], exclusions=[],
                logos=[], layers=[], faces=[], text_runs=[], contrast_pairs=[],
                identity=dict(custom_logo=None, custom_theme=None, custom_tagline=None))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def rgb(value):
    value = value.removeprefix('#')
    if len(value) != 6:
        raise ValueError('Colors must be six-digit RGB hex')
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def pixels(image):
    method = getattr(image, 'get_flattened_data', None)
    return method() if method else image.getdata()


def rect(value, size):
    if (not isinstance(value, list) or len(value) != 4 or
        any(type(x) is not int for x in value)):
        raise ValueError('Bounds must be integer [x, y, width, height]')
    x, y, w, h = value
    if min(x, y) < 0 or min(w, h) <= 0 or x+w > size[0] or y+h > size[1]:
        raise ValueError('Bounds outside image')
    return x, y, x+w, y+h


def gradient_distance(pixel, start, end):
    vector = [b-a for a, b in zip(start, end)]
    t = max(0, min(1, sum((p-a)*v for p, a, v in zip(pixel, start, vector)) /
                       sum(v*v for v in vector)))
    return max(abs(p-(a+t*v)) for p, a, v in zip(pixel, start, vector))


def inspect(candidate, spec, root):
    from PIL import Image
    if not isinstance(spec, dict) or spec.get('format') not in ('tm-poster-brand-check/v1', 'tm-poster-brand-check/v2', 'tm-poster-vision-check/v1'):
        raise ValueError('Expected a supported brand-check or vision-check specification')
    if spec.get('rule_set') != RULE_SET:
        raise ValueError('Unsupported rule_set')
    with Image.open(candidate) as opened:
        original_format = opened.format
        jpeg_settings = None
        if original_format=='JPEG':
            from PIL import JpegImagePlugin
            jpeg_settings=dict(qtables=getattr(opened,'quantization',None),subsampling=JpegImagePlugin.get_sampling(opened))
        if original_format not in ('PNG', 'JPEG'):
            raise ValueError('Only PNG and JPEG exports are supported')
        rgba = opened.convert('RGBA')
    if rgba.getextrema()[3] != (255, 255):
        raise ValueError('Final candidate must be opaque; flatten against intended background first')
    image = rgba.convert('RGB')
    if spec['format'] == 'tm-poster-vision-check/v1':
        path = Path(__file__).with_name('vision_review.py')
        loaded = importlib.util.spec_from_file_location('tm_vision_review', path)
        module = importlib.util.module_from_spec(loaded)
        loaded.loader.exec_module(module)
        return module.inspect(image, spec, root, candidate)
    if spec['format'] == 'tm-poster-brand-check/v2':
        module = extended_module()
        scoped_spec = dict(spec, _candidate=candidate)
        findings, manual = module.inspect(image, scoped_spec, root, dict(rgb=rgb, rect=rect, digest=digest, pixels=pixels,
            compare_logo=lambda original,observed,background,offset:compare_logo(original,observed,background,offset,jpeg_settings),
            corroborate_text=lambda image,run,root:corroborate_text(image,run,root,scoped_spec.get('_evidence_bundle'),jpeg_settings)))
        if original_format == 'JPEG':
            for finding in findings:
                if finding['check'] in ('palette','gradient') and finding['status'] == 'REVISE' and 'out_of_tolerance_pixels' in finding:
                    finding.update(status='BLOCKED', observed_status='BLOCKED',reason='JPEG pixel drift: verify lossless source before declaring an exact-color violation')
        states = [f.get('observed_status',f['status']) for f in findings]
        return dict(format='tm-poster-brand-results/v2', rule_set=RULE_SET,
                    manual=module.RULES['manual'], candidate_sha256=digest(candidate),
                    input_format=original_format, dimensions=list(image.size), findings=findings,
                    feature_results=feature_results(findings),
                    scoped_verdict='BLOCKED' if 'BLOCKED' in states else 'REVISE' if 'REVISE' in states else 'PASS',
                    full_brand_verdict='NOT_ASSESSED', manual_review=manual,
                    limitation='Computed results are conditional on supplied source evidence and complete accurate inventories. No TI approval or release authorization.')
    findings = []

    def add(check, status, **details):
        findings.append(dict(check=check, status=status, **details))

    regions = spec.get('color_regions', [])
    logos = spec.get('logos', [])
    if not isinstance(regions, list) or not isinstance(logos, list):
        raise ValueError('color_regions and logos must be lists')
    if not regions:
        add('B05/B06', 'BLOCKED', reason='No designated non-photo color regions')
    for index, region in enumerate(regions):
        bounds = rect(region['bounds'], image.size)
        tolerance = region.get('tolerance', 0)
        if type(tolerance) is not int or not 0 <= tolerance <= 3:
            raise ValueError('Color tolerance must be 0–3 RGB levels; default 0')
        mode = region.get('mode', 'solid')
        if mode == 'solid':
            color = rgb(region['color'])
            if color not in tuple(map(rgb, PALETTE)):
                add('B05', 'REVISE', region=index, reason='Declared solid color outside brand palette')
                continue
            distance = lambda p: max(abs(a-b) for a, b in zip(p, color))
        elif mode == 'gradient':
            colors = tuple(map(rgb, region['colors']))
            if len(colors) != 2 or not any(colors == tuple(map(rgb, pair)) or colors == tuple(map(rgb, pair))[::-1] for pair in GRADIENTS):
                add('B06', 'REVISE', region=index, reason='Undocumented gradient endpoints')
                continue
            distance = lambda p: gradient_distance(p, *colors)
        else:
            raise ValueError('Color mode must be solid or gradient')
        crop = image.crop(bounds)
        bad = sum(distance(p) > tolerance for p in pixels(crop))
        add('B05' if mode == 'solid' else 'B06', 'REVISE' if bad else 'PASS',
            region=index, bounds=region['bounds'], checked_pixels=crop.width*crop.height,
            out_of_tolerance_pixels=bad, tolerance=tolerance,
            scope='Pixel colors only; gradient geometry, dominance and region selection require review')
    if not logos:
        add('B02/B03', 'BLOCKED', reason='No logo checks supplied; applicability requires review')
    for index, logo in enumerate(logos):
        bounds = rect(logo['bounds'], image.size)
        source = root / logo['source']
        actual_hash = digest(source)
        if logo.get('source_sha256') != actual_hash:
            add('B02', 'BLOCKED', logo=index, reason='Official source checksum missing or mismatched')
            continue
        with Image.open(source) as opened:
            original = opened.convert('RGBA')
        width, height = bounds[2]-bounds[0], bounds[3]-bounds[1]
        # Allow at most one pixel of rounding when deriving the other dimension.
        error = abs(height-width*original.height/original.width)
        add('B02 proportions', 'PASS' if error <= 1 else 'REVISE', logo=index,
            expected_height=width*original.height/original.width, actual_height=height)
        kind = logo.get('kind')
        if kind not in ('ti', 'pathways'):
            raise ValueError('Logo kind must be ti or pathways; other assets require manual rules')
        target_width = spec.get('target_width_px')
        print_width = spec.get('print_width_in')
        if target_width is None and print_width is None:
            add('B03 minimum size', 'BLOCKED', logo=index, reason='Intended output size missing')
        for unit, target, minimum in (('px', target_width, 72), ('in', print_width, 1 if kind == 'pathways' else .75)):
            if target is not None:
                if type(target) not in (int, float) or not math.isfinite(target) or target <= 0:
                    raise ValueError('Output size must be positive and finite')
                measured = width*target/image.width
                add('B03 minimum size', 'PASS' if measured >= minimum else 'REVISE',
                    logo=index, width=measured, minimum=minimum, unit=unit)
        # Compare visual appearance across plausible resize/JPEG pipelines.
        background = rgb(logo['background'])
        comparison = compare_logo(original, image.crop(bounds), background, bounds[:2],jpeg_settings)
        add('B02 source rendering', comparison.pop('status'), logo=index,
            source_sha256=actual_hash, **comparison)
        # This is a uniform-background clear-space test, using a measured
        # wordmark height from the trusted official source/manual diagram.
        source_clear = logo.get('source_wordmark_height_px')
        if type(source_clear) not in (int, float) or not math.isfinite(source_clear) or source_clear <= 0 or source_clear > original.height:
            add('B03 clear space', 'BLOCKED', logo=index, reason='Verified source wordmark height required')
        else:
            margin = math.ceil(source_clear*width/original.width)
            x, y, right, bottom = bounds
            if x < margin or y < margin or right+margin > image.width or bottom+margin > image.height:
                add('B03 clear space', 'REVISE', logo=index, required_margin_px=margin, reason='Clear space crosses canvas edge')
            else:
                strips = ((x-margin,y-margin,right+margin,y), (x-margin,bottom,right+margin,bottom+margin),
                          (x-margin,y,x,bottom), (right,y,right+margin,bottom))
                occupied = sum(p != background for strip in strips for p in pixels(image.crop(strip)))
                add('B03 clear space', 'PASS' if not occupied else 'BLOCKED', logo=index,
                    required_margin_px=margin, nonbackground_pixels=occupied,
                    reason='Uniform clear space verified' if not occupied else 'Nonuniform background: inspect clear space manually')
    states = [item['status'] for item in findings]
    if original_format == 'JPEG':
        for finding in findings:
            if 'out_of_tolerance_pixels' in finding and finding['status'] == 'REVISE':
                finding.update(status='BLOCKED', reason='JPEG pixel drift: verify lossless source before declaring an exact-color violation')
        states = [item['status'] for item in findings]
    return dict(format='tm-poster-brand-results/v1', rule_set=RULE_SET,
                candidate_sha256=digest(candidate), findings=findings,
                scoped_verdict='BLOCKED' if 'BLOCKED' in states else 'REVISE' if 'REVISE' in states else 'PASS',
                full_brand_verdict='NOT_ASSESSED',
                limitation='Only declared regions and supplied source recipe checked. Source authenticity, bounds, color dominance, other rules and final visual review remain required.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--spec', type=Path)
    parser.add_argument('--observations',type=Path,help='Model-fed visual measurement specification; no OCR')
    parser.add_argument('--vision-template',action='store_true',help='Print incomplete model-fed vision specification')
    parser.add_argument('--evidence',type=Path,help='Optional neutral local evidence bundle (renderer_log/font/source paths)')
    parser.add_argument('--template', action='store_true', help='Print an incomplete v2 specification')
    parser.add_argument('--rules', action='store_true', help='Print manual facts and check/page inventory')
    args = parser.parse_args()
    if args.vision_template:
        path = Path(__file__).with_name('vision_review.py')
        loaded = importlib.util.spec_from_file_location('tm_vision_template',path)
        module = importlib.util.module_from_spec(loaded);loaded.loader.exec_module(module)
        print(json.dumps(module.template(),indent=2));return 0
    if args.template:
        print(json.dumps(template(), indent=2))
        return 0
    if args.rules:
        print(json.dumps(extended_module().RULES, indent=2))
        return 0
    if args.spec is not None and args.observations is not None:
        parser.error('Use either --spec or --observations')
    if args.observations is not None:
        args.spec = args.observations
    if args.candidate is None or args.spec is None:
        parser.error('--candidate and --spec or --observations are required unless exporting a template/rules')
    try:
        spec = json.loads(args.spec.read_text(encoding='utf-8'))
        if args.evidence:
            spec['_evidence_bundle'] = json.loads(args.evidence.read_text(encoding='utf-8'))
        result = inspect(args.candidate, spec, args.spec.resolve().parent)
    except (ImportError, OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json.dumps(dict(scoped_verdict='BLOCKED', error=str(error))))
        return 2
    print(json.dumps(result, indent=2))
    return {'PASS': 0, 'REVISE': 1, 'BLOCKED': 2}[result['scoped_verdict']]


if __name__ == '__main__':
    sys.exit(main())
