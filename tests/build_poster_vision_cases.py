"""Adapt private existing posters for geometric/masked-color measurements.

This is a test-input adapter, not a model or OCR implementation. Source-derived
fixture regions are labeled as such. Optional real-poster regions are the
assistant's visually inspected rough observations for the three calibrated
layouts, not a source-verified inventory. Images, official references and
generated JSON remain in a fresh private output directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from PIL import Image


TARGET_MAP = {
    'logo_source': ('logo_detection', 'logo_appearance'),
    'logo_proportions': ('logo_geometry',),
    'logo_transform': ('logo_geometry',),
    'logo_size': ('logo_size',),
    'logo_clear_space': ('logo_clear_space',),
    'logo_overlap': ('logo_clear_space', 'logo_appearance'),
    'logo_effects': ('logo_effects', 'logo_appearance'),
    'palette': ('design_palette',),
    'gradient': ('design_palette',),
}

# Permitted raster variants from the official logo archive. Keep filenames so
# diagnostics identify the matched variant, rather than a renamed ti.png.
OFFICIAL_LOGO_MEMBERS = (
    'ToastmastersLogo/Color/ToastmastersLogoColor.png',
    'ToastmastersLogo/Color/ToastmastersLogo3Color.png',
    'ToastmastersLogo/Grayscale/ToastmastersLogoGrayscale.png',
    'ToastmastersLogo/White/ToastmastersLogoWhite.png',
)
OFFICIAL_WORDMARK_MEMBERS = tuple(
    f'ToastmastersWordmark/{color}/ToastmastersWordmark{color}.png'
    for color in ('Black', 'Color', 'Grayscale', 'White'))

# Premeasured wordmark-bar X and tight artwork width for these exact downloads.
# Measurements use nonzero-alpha bounds (including antialias fringes). Hashes
# identify source files only; poster matching still uses SIFT/spatial Lab.
# An archive revision may be compared, but cannot inherit stale measurements.
LOGO_X_MEASUREMENTS = {
    'd37b4a178c62fc94649d9beb1e52240a50965f92eb98db6565c775fa96818456': (405, 1810),
    'a6e1f36d02a3caa6695e1e4b65ed6ad5562585c18af2d8b2cbaac91af3e2dcda': (293, 1304),
    'e845967960b2ead33c8096953c3e435d2c8fd71726edb3922049aa8730181a54': (292, 1303),
    'b5e4f519d02331681a39c67c6a51858f4b1b844d40a9a9c7463b0711d232e3c6': (417, 1803),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def polygon(bounds):
    x, y, w, h = bounds
    # Continuous pixel-edge coordinates preserve positive area even for the
    # renderer's one-pixel-wide partition cells. The measurement layer owns
    # rasterization and boundary uncertainty; this adapter must not collapse
    # those cells to lines by converting both edges into pixel-center indices.
    return [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]


def loose_roi(bounds, size):
    x, y, w, h = bounds
    pad = max(24, round(w*.45))
    left, top = max(0, x-pad), max(0, y-pad)
    right, bottom = min(size[0], x+w+pad), min(size[1], y+h+pad)
    return [left, top, right-left, bottom-top]


def resolve(root, value):
    path = Path(value)
    return path if path.is_absolute() else root/path


def official_logo_references(assets, output):
    """Prepare all four permitted variants, never selecting from poster labels.

    Read only the named PNG entries; no archive-wide extraction or SVG execution.
    Missing entries are input errors rather than silently incomplete coverage.
    Unknown file revisions retain appearance coverage with an unmeasured X.
    """
    variants = []
    with zipfile.ZipFile(assets/'logo.zip') as archive:
        for member in OFFICIAL_LOGO_MEMBERS:
            data = archive.read(member)
            destination = output/'references'/Path(member).name
            destination.write_bytes(data)
            entry = dict(path=str(destination.resolve()))
            measurement = LOGO_X_MEASUREMENTS.get(hashlib.sha256(data).hexdigest())
            if measurement:
                entry['wordmark_height_ratio'] = measurement[0]/measurement[1]
            variants.append(entry)
    return variants


def official_wordmark_references(assets, output):
    """Prepare each standalone wordmark; X is its alpha-tight artwork height."""
    variants = []
    with zipfile.ZipFile(assets/'wordmark.zip') as archive:
        for member in OFFICIAL_WORDMARK_MEMBERS:
            destination = output/'references'/Path(member).name
            destination.write_bytes(archive.read(member))
            with Image.open(destination) as opened:
                bounds = opened.convert('RGBA').getchannel('A').getbbox()
            if not bounds:
                raise ValueError('Official wordmark reference has no visible artwork')
            variants.append(dict(path=str(destination.resolve()),
                wordmark_height_ratio=(bounds[3]-bounds[1])/(bounds[2]-bounds[0])))
    return variants


def adapt_manifest(manifest_path, output, reference_cache):
    """Use existing source regions, never earlier predictions or reviewer labels."""
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    samples = []
    for sample in manifest['samples']:
        image_path = resolve(manifest_path.parent, sample['image']).resolve()
        spec_path = resolve(manifest_path.parent, sample['spec']).resolve()
        spec = json.loads(spec_path.read_text(encoding='utf-8'))
        with Image.open(image_path) as opened:
            size = opened.size
        identifier = sample['id']
        observation = dict(
            format='tm-poster-vision-check/v1', rule_set='tm-poster-brand-2026-08-v1',
            candidate_sha256=sha(image_path), target_width_px=spec.get('target_width_px'),
            producer=dict(method='fixture-source-derived',
                          limitation='Prepared source regions; not model extraction accuracy'),
            logos=[], colors=dict(include=[], exclude=[], inventory_complete=False))
        logos = spec.get('logos', [])
        selectors = sample.get('target_selectors', {})
        selected = {selector['logo'] for selector in selectors.values()
                    if isinstance(selector, dict) and 'logo' in selector}
        for index, logo in enumerate(logos):
            if selected and index not in selected:
                continue
            if logo.get('kind') not in ('ti', 'wordmark', 'gavel', 'pathways', 'member-badge', 'pathways-badge'):
                continue
            source = resolve(spec_path.parent, logo['source']) if logo.get('source') else None
            bounds = logo['bounds']
            adapted = dict(id=f'logo-{index}', kind=logo['kind'], roi=loose_roi(bounds, size),
                           foreground_regions=[layer['bounds'] for layer in spec.get('layers', [])
                               if layer.get('id') != logo.get('layer_id') and
                               layer.get('kind') not in ('background', 'photo')],
                           foreground_inventory_complete=spec.get('inventory_complete') is True,
                           evidence_basis='Fixture source geometry; original bounds not supplied as detection answer')
            if 'background' in logo:
                # This is a measurement hypothesis, not evidence that the
                # observed crop actually has a uniform background. The engine
                # must verify the applicable background pixels itself.
                adapted['background'] = logo['background']
            if source and source.is_file():
                with Image.open(source) as opened:
                    reference = opened.convert('RGBA')
                crop = logo.get('source_bounds')
                if crop:
                    x, y, w, h = crop
                    reference = reference.crop((x, y, x+w, y+h))
                alpha = reference.getchannel('A').getbbox()
                if alpha:
                    reference = reference.crop(alpha)
                key = sha(source)+'-'+str(crop)
                if key not in reference_cache:
                    path = output/'references'/f'{len(reference_cache):03d}.png'
                    reference.save(path)
                    reference_cache[key] = path
                adapted['reference'] = str(reference_cache[key])
                measurement = logo.get('source_wordmark_height_px')
                if isinstance(measurement, (int, float)) and measurement > 0:
                    adapted['wordmark_height_ratio'] = measurement/reference.width
            observation['logos'].append(adapted)
        for region in spec.get('color_regions', []):
            observation['colors']['include'].append(dict(
                polygon=polygon(region['bounds']), reason='Fixture-design region from actual renderer inventory'))
        for region in spec.get('exclusions', []):
            observation['colors']['exclude'].append(dict(
                polygon=polygon(region['bounds']), kind=region['kind'], reason=region.get('reason', 'Fixture exclusion')))
        # All prepared design rectangles are carried forward, but this adapter
        # cannot independently certify whether their semantic classification is correct.
        observation['colors']['inventory_complete'] = spec.get('inventory_complete') is True
        target_checks = sorted({new for old in sample['target_checks'] for new in TARGET_MAP.get(old, ())})
        observation['requested_checks'] = target_checks
        destination = output/f'{identifier}-observations.json'
        write(destination, observation)
        samples.append(dict(id=identifier, image=str(image_path), observations=str(destination),
                            target_checks=target_checks, source_target_checks=sample['target_checks'],
                            untested_source_checks=[key for key in sample['target_checks'] if key not in TARGET_MAP],
                            origin_scope=sample.get('scope'), source_manifest=str(manifest_path),
                            limitation='New vision scope is a subset/reinterpretation; original positive/negative labels are not new ground truth'))
    return samples


def real_observations(images, assets, output):
    """Rough regions visually inspected for the three user-accepted layouts.

    The supplied files must be those layouts in the specified order. Coordinates
    below come from direct model image inspection of their available prior
    720-ish-pixel exports. Scaling them is coordinate conversion, not a fresh
    image observation or a claim that a high-resolution attachment was tested.
    """
    logo_variants = official_logo_references(assets, output)
    wordmark_variants = official_wordmark_references(assets, output)
    # Rough plain-design coverage; exclusions preserve photographs, official
    # artwork and QR code colors. Broad masks intentionally include text pixels,
    # so an implementation must handle neutral/antialias colors transparently.
    shapes = [
        dict(label='AI project-management poster', base=(720, 1280),
             roi=[35, 25, 255, 220],
             include=[[[0, 0], [390, 0], [390, 1100], [0, 1100]],
                      [[0, 1110], [719, 1110], [719, 1279], [0, 1279]]],
             exclude=[('official-asset', [45, 35, 235, 195]), ('qr', [540, 1125, 155, 145])],
             foreground=[[45, 258, 322, 81]],
             ambiguity='Top clear space may be close to the wordmark-height requirement; user acceptance is not a geometry exemption.'),
        dict(label='District poster-design training poster', base=(719, 1280),
             roi=[25, 25, 290, 75],
             include=[[[0, 0], [718, 0], [718, 1279], [0, 1279]]],
             exclude=[('official-asset', [30, 25, 280, 65]),
                      ('photo', [[0, 270], [235, 230], [465, 380], [540, 780], [515, 1050], [0, 1050]]),
                      ('qr', [460, 1100, 225, 105])],
             foreground=[[38, 115, 645, 40], [489, 35, 194, 46]],
             ambiguity='EVERYONE CAN GLOW needs topic/slogan versus District-identity classification; not evaluated by geometric/color checks.'),
        dict(label='Coaching case-discussion poster', base=(720, 1280),
             roi=[565, 10, 140, 120],
             include=[[[0, 0], [719, 0], [719, 1279], [0, 1279]]],
             exclude=[('official-asset', [575, 20, 120, 100]), ('photo', [112, 435, 495, 172]),
                      ('qr', [420, 1090, 210, 110])],
             foreground=[[105, 50, 410, 60], [260, 132, 320, 75]],
             ambiguity='Topic illustration is excluded by visual role, not by proof of source layers or image rights.'),
    ]
    samples = []
    for number, (image, shape) in enumerate(zip(images, shapes), 1):
        image = image.resolve()
        with Image.open(image) as opened:
            width, height = opened.size
        sx, sy = width/shape['base'][0], height/shape['base'][1]
        def scaled_polygon(points):
            return [[min(width-1, round(x*sx)), min(height-1, round(y*sy))] for x, y in points]
        def scaled_box(box):
            x, y, w, h = box
            return [round(x*sx), round(y*sy), round(w*sx), round(h*sy)]
        colors = dict(include=[dict(polygon=scaled_polygon(poly), reason='Visually selected rough design region')
                               for poly in shape['include']], exclude=[], inventory_complete=False)
        for kind, value in shape['exclude']:
            poly = value if isinstance(value[0], list) else polygon(value)
            colors['exclude'].append(dict(polygon=scaled_polygon(poly), kind=kind,
                reason='Model-observed '+kind+' region; rough mask, source classification not independently verified'))
        observation = dict(format='tm-poster-vision-check/v1', rule_set='tm-poster-brand-2026-08-v1',
            candidate_sha256=sha(image), target_width_px=width,
            requested_checks=['logo_detection', 'logo_geometry', 'logo_appearance',
                              'logo_clear_space', 'logo_size', 'design_palette'],
            producer=dict(method='model-image-observation', model_id='not-exposed',
                          limitation='Assistant visually inspected prior available lower-resolution exports; not a Luna 5.6 extraction trial'),
            logos=[dict(id='primary-logo', kind='wordmark' if number == 2 else 'ti',
                        roi=scaled_box(shape['roi']),
                        foreground_regions=[scaled_box(box) for box in shape['foreground']],
                        foreground_inventory_complete=True)], colors=colors,
            review_notes=[shape['ambiguity'],
                'Target width assumes this decoded export is reviewed at native pixel width; other intended sizes require new scale facts.'])
        # The first and third layouts contain TI globe logos. Try every official
        # variant, even when a model has guessed a specific variant. Wordmarks
        # use their own complete family; no model-picked color variant gate.
        observation['logos'][0]['references'] = wordmark_variants if number == 2 else logo_variants
        destination = output/f'real-{number}-observations.json'
        write(destination, observation)
        samples.append(dict(id=f'real-{number}', description=shape['label'], image=str(image),
            observations=str(destination), target_checks=['logo_detection', 'logo_geometry', 'logo_appearance',
                'logo_clear_space', 'logo_size', 'design_palette'],
            origin_scope='User-accepted positive calibration, restricted to vision measurements; not independently verified brand approval',
            user_expected='PASS', resolution=list((width, height))))
    return samples


def build(manifests, assets, output, real_images=()):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Fresh nonempty output directory must not be overwritten')
    output.mkdir(parents=True, exist_ok=True)
    (output/'references').mkdir()
    references = {}
    samples = []
    for manifest in manifests:
        samples.extend(adapt_manifest(manifest.resolve(), output, references))
    if real_images:
        if len(real_images) != 3:
            raise ValueError('Provide exactly three real images in the documented calibration order')
        samples.extend(real_observations(real_images, assets.resolve(), output))
    identifiers = [sample['id'] for sample in samples]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError('Duplicate sample IDs across manifests')
    write(output/'manifest.json', dict(format='tm-poster-vision-cases/v1', samples=samples,
        limitation='Prepared inputs for image measurement, not evidence of Luna extraction or end-to-end parity'))
    write(output/'sha256-inventory.json', {str(path.relative_to(output)):sha(path)
        for path in output.rglob('*') if path.is_file() and path.name != 'sha256-inventory.json'})
    return samples


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, action='append', default=[])
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--real-images', type=Path, nargs=3)
    args = parser.parse_args()
    cases = build(args.manifest, args.assets, args.output, args.real_images or ())
    print(json.dumps(dict(output=str(args.output), samples=len(cases),
        cases_with_measurement_targets=sum(bool(case['target_checks']) for case in cases)), indent=2))
