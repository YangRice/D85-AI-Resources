"""Corroborate supplied copy and font recipes against actual local poster pixels.

No font recognition from appearance and no external services are used. A renderer
recipe is evidence only when its glyphs reproduce the candidate region.
"""
import shutil
import json
import subprocess
import tempfile
import unicodedata
import importlib.util
from collections import Counter
from pathlib import Path


def pixels(image):
    method=getattr(image,'get_flattened_data',None)
    return method() if method else image.getdata()


def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC', text).split())


def export_comparison(reference,observed,background,offset,jpeg_settings):
    path=Path(__file__).with_name('logo_compare.py')
    spec=importlib.util.spec_from_file_location('tm_glyph_export_compare',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.compare_rendered(reference,observed,background,offset,jpeg_settings,
                                   blur=.5,mean_limit=2,maximum_limit=20,fraction_limit=.03)


def corroborate(image, run, root, rect, digest, evidence_bundle=None,jpeg_settings=None):
    """Try supplied recipes and neutral source-artifact recipes against pixels.

    A log is never itself proof. Only a successful actual glyph reproduction
    allows its font/effect/text facts to be used as observed evidence.
    """
    recipes = [run]
    supplied = run.get('render_evidence')
    artifacts = []
    if isinstance(supplied,dict) and supplied.get('source_artifact'):
        artifacts.append(root/supplied['source_artifact'])
    if isinstance(evidence_bundle,dict) and evidence_bundle.get('renderer_log'):
        artifacts.append(root/evidence_bundle['renderer_log'])
    seen = set()
    for artifact in artifacts:
        if str(artifact) in seen:
            continue
        seen.add(str(artifact))
        try:
            log = json.loads(artifact.read_text(encoding='utf-8'))
        except (OSError,ValueError):
            continue
        for record in log.get('text_runs',[]):
            if not isinstance(record,dict) or record.get('bounds') != run.get('bounds'):
                continue
            source_run = dict(run,text=record.get('text',run['text']),render_evidence=dict(record))
            recipes.append(source_run)
    fallback = None
    ocr_lang = 'eng'
    tessdata_dir = None
    if isinstance(evidence_bundle,dict):
        declared_lang = evidence_bundle.get('ocr_lang', 'eng')
        if isinstance(declared_lang,str) and declared_lang.strip() and all(
                ch.isalnum() or ch in '+_-.' for ch in declared_lang):
            ocr_lang = declared_lang
        declared_tessdata = evidence_bundle.get('tessdata_dir')
        if isinstance(declared_tessdata,str) and declared_tessdata:
            tessdata_dir = root / declared_tessdata
    for recipe in recipes:
        try:
            result = _corroborate_recipe(image,recipe,root,rect,digest,allow_ocr=False,
                                         jpeg_settings=jpeg_settings)
        except OSError:
            continue
        if fallback is None:
            fallback = result
        if result['font_status'] == 'PASS':
            result['observed_text'] = recipe['text']
            result['source_artifact_used'] = recipe is not run
            return result
    # OCR is attempted once only; it never proves a font or effect.
    try:
        ocr = _corroborate_recipe(image,run,root,rect,digest,allow_ocr=True,
                                  jpeg_settings=jpeg_settings,ocr_lang=ocr_lang,
                                  tessdata_dir=tessdata_dir)
    except OSError:
        plain = dict(run,render_evidence=None)
        ocr = _corroborate_recipe(image,plain,root,rect,digest,allow_ocr=True,
                                  jpeg_settings=jpeg_settings,ocr_lang=ocr_lang,
                                  tessdata_dir=tessdata_dir)
    return ocr


def _corroborate_recipe(image, run, root, rect, digest, allow_ocr=True,
                        jpeg_settings=None,ocr_lang='eng',tessdata_dir=None):
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat
    bounds = rect(run['bounds'], image.size)
    crop = image.crop(bounds).convert('RGB')
    evidence = run.get('render_evidence')
    result = dict(copy_status='BLOCKED', font_status='BLOCKED', effects_status='BLOCKED',
                  reason='Supplied declarations have not been corroborated against poster pixels')
    if isinstance(evidence, dict):
        required = ('font_file','font_sha256','font_size_px','origin','color','background')
        if all(k in evidence for k in required):
            path = root / evidence['font_file']
            if digest(path) != evidence['font_sha256']:
                result['reason'] = 'Renderer font-file checksum mismatch'
                return result
            size = evidence['font_size_px']
            if type(size) is not int or not 1 <= size <= 2048:
                raise ValueError('Renderer font_size_px must be an integer 1–2048')
            origin = evidence['origin']
            if not isinstance(origin,list) or len(origin) != 2 or any(type(v) not in (int,float) for v in origin):
                raise ValueError('Renderer origin must be an x/y pair')
            font = ImageFont.truetype(str(path),size)
            rendered = Image.new('RGB',crop.size,evidence['background'])
            draw = ImageDraw.Draw(rendered)
            position = (origin[0]-bounds[0],origin[1]-bounds[1])
            stroke_width = evidence.get('stroke_width',0)
            if type(stroke_width) is not int or not 0 <= stroke_width <= 64:
                raise ValueError('stroke_width must be an integer 0–64')
            glyph_bounds = draw.textbbox(position,run['text'],font=font,
                                        anchor=evidence.get('anchor','lt'),stroke_width=stroke_width)
            if (not run['text'].strip() or glyph_bounds[0] < 0 or glyph_bounds[1] < 0 or
                glyph_bounds[2] > crop.width or glyph_bounds[3] > crop.height):
                result['reason'] = 'Text is empty, clipped or positioned outside its supplied region'
                return result
            draw.text(position,run['text'],
                      font=font,fill=evidence['color'],anchor=evidence.get('anchor','lt'),
                      stroke_width=stroke_width,
                      stroke_fill=evidence.get('stroke_fill'))
            blank = Image.new('RGB',crop.size,evidence['background'])
            if ImageChops.difference(rendered,blank).getbbox() is None:
                result['reason'] = 'Renderer recipe produces no visible glyph pixels'
                return result
            diff = ImageChops.difference(rendered,crop)
            blurred = ImageChops.difference(rendered.filter(ImageFilter.GaussianBlur(.5)),
                                           crop.filter(ImageFilter.GaussianBlur(.5)))
            mean = sum(ImageStat.Stat(blurred).mean)/3
            maximum = max(high for low,high in blurred.getextrema())
            exact = diff.getbbox() is None
            matched = exact or (mean <= 2 and maximum <= 20)
            if not matched and mean<12:
                exported=export_comparison(rendered,crop,blank.getpixel((0,0)),bounds[:2],jpeg_settings)
                if exported['matched']:
                    matched=True
                    result['export_pipeline']=exported['metrics']
                    mean=exported['metrics']['mean_channel_error']
                    maximum=exported['metrics']['max_blurred_channel_error']
            actual_effects = []
            if not matched:
                # Infer bounded shadow-color candidates from actual residual
                # pixels outside the plain glyphs; never assume all shadows are
                # black or trust a declared effect string as proof.
                background=blank.getpixel((0,0))
                candidates=Counter()
                values={}
                raw=zip(pixels(rendered),pixels(crop))
                for expected,p in raw:
                    if max(abs(v-bg) for v,bg in zip(expected,background))<=3 and max(abs(v-bg) for v,bg in zip(p,background))>24:
                        key=tuple(v//8 for v in p)
                        candidates[key]+=1
                        values.setdefault(key,[0,0,0])
                        for c in range(3):values[key][c]+=p[c]
                colors=[tuple(round(v/candidates[key]) for v in values[key]) for key,count in candidates.most_common(4)]
                if (0,0,0) not in colors:colors.append((0,0,0))
                best_shadows=[]
                offsets=[(dx,dy) for dx in range(-6,7) for dy in range(-6,7) if (dx or dy)]
                hint=evidence.get('shadow_offset')
                if (isinstance(hint,list) and len(hint)==2 and
                    all(type(v) is int for v in hint) and any(hint) and
                    abs(hint[0])<=crop.width and abs(hint[1])<=crop.height):
                    # Documented source geometry is a hypothesis, not proof;
                    # it must reproduce the visible effect in candidate pixels.
                    offsets=[tuple(hint)]+[pair for pair in offsets if pair!=tuple(hint)]
                if crop.width*crop.height>400000:offsets=[]
                for dx,dy in offsets:
                    if matched:break
                    for color in colors:
                        shadowed = Image.new('RGB',crop.size,evidence['background'])
                        shadow_draw = ImageDraw.Draw(shadowed)
                        shadow_draw.text((position[0]+dx,position[1]+dy),run['text'],font=font,
                                         fill=color,anchor=evidence.get('anchor','lt'))
                        shadow_draw.text(position,run['text'],font=font,fill=evidence['color'],
                                         anchor=evidence.get('anchor','lt'))
                        shadow_diff = ImageChops.difference(shadowed,crop)
                        shadow_mean = sum(ImageStat.Stat(shadow_diff).mean)/3
                        shadow_max = max(high for low,high in shadow_diff.getextrema())
                        if shadow_diff.getbbox() is None or (shadow_mean <= 1 and shadow_max <= 12):
                            matched = True
                            actual_effects = ['drop-shadow']
                            mean,maximum = shadow_mean,shadow_max
                            result['shadow_offset'] = [dx,dy]
                            result['shadow_color'] = list(color)
                            break
                        best_shadows.append((shadow_mean,shadowed,(dx,dy),color))
                        best_shadows.sort(key=lambda item:item[0]);best_shadows=best_shadows[:3]
                if not matched:
                    for _,shadowed,(dx,dy),color in best_shadows:
                        exported=export_comparison(shadowed,crop,background,bounds[:2],jpeg_settings)
                        if exported['matched']:
                            matched=True;actual_effects=['drop-shadow']
                            result.update(shadow_offset=[dx,dy],shadow_color=list(color),export_pipeline=exported['metrics'])
                            mean=exported['metrics']['mean_channel_error']
                            maximum=exported['metrics']['max_blurred_channel_error']
                            break
            # The actual font is measured from its internal name records, never
            # copied from the claimed family in the specification.
            family, style = font.getname()
            result.update(font_family=family,font_style=style,font_file_sha256=digest(path),
                          actual_font_file=str(path),
                          pixel_match=matched,mean_channel_error=mean,
                          max_blurred_channel_error=maximum,
                          method='font-file glyph rerender against actual image',
                          engineering_thresholds=dict(mean_channel_error=2,max_blurred_channel_error=20),
                          scope='Supplied renderer recipe and run bounds; no source-free font identification')
            if matched:
                result.update(copy_status='PASS',font_status='PASS',effects_status='PASS' if stroke_width == 0 else 'BLOCKED',
                              effects=actual_effects,
                              reason='Actual font glyphs and text recipe reproduce the candidate region')
                return result
            result['reason'] = 'Supplied font/text/effect recipe does not reproduce the actual candidate region'
    # OCR is a separate copy observation, not font/effect evidence. Availability
    # and confidence are explicit; failure never silently confirms declared text.
    if not allow_ocr:
        return result
    executable = shutil.which('tesseract')
    if executable is None:
        result['ocr'] = 'NOT RUN: tesseract unavailable'
        return result
    if crop.width*crop.height > 4000000:
        result['ocr'] = 'NOT RUN: text crop exceeds 4 million pixels'
        return result
    with tempfile.TemporaryDirectory(prefix='tm-copy-') as directory:
        path = Path(directory)/'text.png'
        crop.resize((crop.width*2,crop.height*2)).save(path)
        try:
            # Do not rely on the optional `tsv` config file: minimal Tesseract
            # installations often omit it. The explicit setting is portable.
            command = [executable,str(path),'stdout','-l',ocr_lang,'--psm','7',
                       '-c','tessedit_create_tsv=1']
            if tessdata_dir is not None:
                command[1:1] = ['--tessdata-dir',str(tessdata_dir)]
            process = subprocess.run(command,
                                     capture_output=True,text=True,timeout=15)
        except (OSError,subprocess.TimeoutExpired):
            result['ocr'] = 'BLOCKED: local OCR could not complete'
            return result
    words, confidences = [], []
    for row in process.stdout.splitlines()[1:]:
        fields = row.split('\t')
        if len(fields) >= 12 and fields[11].strip():
            try:
                confidence = float(fields[10])
            except ValueError:
                continue
            words.append(fields[11]);confidences.append(confidence)
    observed = ' '.join(words)
    confidence = min(confidences) if confidences else 0
    result.update(ocr_text=observed,ocr_minimum_confidence=confidence,
                  ocr_language=ocr_lang,
                  ocr_scope='Local single-line OCR; corroboration only, not a full-image text inventory')
    if process.returncode == 0 and normalize(observed) == normalize(run['text']) and confidence >= 65:
        result['copy_status'] = 'PASS'
    return result
