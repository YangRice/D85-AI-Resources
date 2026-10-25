"""V2 source/layout measurements. Imported by check_brand; no network access.

Every source assertion remains conditional on accurate supplied inventories.
"""
import datetime
import json
import math
from decimal import Decimal
from pathlib import Path

RULES = json.loads(Path(__file__).with_name('brand_rules.json').read_text(encoding='utf-8'))
CONTEXTS = ('ordinary-club', 'area', 'division', 'district', 'region',
            'corporate-club', 'gavel-club', 'annual-district-conference')


def number(value, name, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(name + ': invalid finite number')
    return value


def inspect(image, spec, root, helpers):
    from PIL import Image, ImageDraw
    rgb, rect, digest, pixels = (helpers[k] for k in ('rgb', 'rect', 'digest', 'pixels'))
    findings = []
    manual = []

    def add(check, status, **details):
        rule = RULES['checks'][check]
        finding = dict(check=check, status=status, rule=rule['rule'],
                       manual_pages=rule['pages'], observed_status=status,
                       evidence_basis='computed from supplied evidence')
        finding.update(details)
        findings.append(finding)

    def required_list(name, check):
        value = spec.get(name)
        if value is None:
            add(check, 'BLOCKED', reason=name + ' inventory missing (use [] when none)')
            return []
        if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
            raise ValueError(name + ' must be a list of objects')
        return value

    def overlap(a, b):
        return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])

    def box(item):
        return rect(item['bounds'], image.size)

    context = spec.get('context')
    if context not in CONTEXTS:
        add('identity', 'BLOCKED', reason='A supported organizational context is required')
    if spec.get('document_kind', 'poster') != 'poster':
        add('identity', 'BLOCKED', reason='This checker covers posters; medium-specific website/video/product/banner rules are outside scope')
    if spec.get('candidate_sha256') != digest(spec['_candidate']):
        add('identity', 'BLOCKED', reason='V2 specification must be bound to the actual candidate SHA-256')
    if spec.get('inventory_complete') is not True:
        add('identity', 'BLOCKED', reason='Complete layer/text/logo/face inventory has not been established')

    # Source RGB/CMYK/Pantone formulations, without inferring press colors from RGB.
    for item in required_list('color_formulations', 'color_formulations'):
        key = item['hex'].removeprefix('#').upper()
        entry = RULES['colors'].get(key)
        if entry is None:
            add('color_formulations', 'REVISE', color=key, reason='Not a documented palette swatch')
            continue
        for model in ('rgb', 'cmyk', 'pantone'):
            if model in item:
                expected = list(rgb(key)) if model == 'rgb' else entry[model]
                add('color_formulations', 'PASS' if item[model] == expected else 'REVISE',
                    color=key, model=model, declared=item[model], expected=expected,
                    scope='Declared source swatch; not a press/PDF color-profile certification')

    # Actual image coverage, never a few favorable swatches silently passing a whole design.
    coverage = Image.new('1', image.size)
    draw = ImageDraw.Draw(coverage)
    primary = Image.new('1', image.size)
    primary_draw = ImageDraw.Draw(primary)
    exclusions = required_list('exclusions', 'color_coverage')
    for exclusion in exclusions:
        if exclusion.get('kind') not in ('photo', 'official-asset', 'text', 'qr', 'neutral', 'antialias') or not exclusion.get('reason'):
            raise ValueError('Exclusions require kind and reason')
        x, y, r, b = box(exclusion)
        draw.rectangle((x,y,r-1,b-1), fill=1)
    design = Image.new('1', image.size)
    design_draw = ImageDraw.Draw(design)
    for index, region in enumerate(required_list('color_regions', 'palette')):
        bounds = box(region)
        x0,y0,x1,y1 = bounds
        draw.rectangle((x0,y0,x1-1,y1-1), fill=1)
        design_draw.rectangle((x0,y0,x1-1,y1-1), fill=1)
        mode = region.get('mode', 'solid')
        tolerance = region.get('tolerance', 0)
        if type(tolerance) is not int or not 0 <= tolerance <= 3:
            raise ValueError('Tolerance must be an integer 0–3 RGB levels')
        opacity = number(region.get('opacity', 1), 'opacity')
        if opacity > 1:
            raise ValueError('Opacity must be <=1')
        overlay = region.get('overlay')
        if overlay is not None:
            overlay_rgb = rgb(overlay['color'])
            alpha = number(overlay['opacity'], 'overlay opacity')
            alpha_complement = float(Decimal(1)-Decimal(str(alpha)))
            if alpha > 1:
                raise ValueError('Overlay opacity must be <=1')
            if overlay_rgb not in [rgb(c) for c in RULES['colors']] + [(255,255,255)]:
                add('transparency', 'BLOCKED', region=index, reason='Overlay color treatment needs manual verification')
        if mode == 'solid':
            start = end = rgb(region['color'])
            if region['color'].removeprefix('#').upper() not in RULES['colors']:
                add('palette', 'REVISE', region=index, reason='Solid design region outside four palette colors; neutral/official/photo treatments need explicit exclusion')
                continue
            is_primary = start in [rgb(c) for c in ('004165','772432')]
        elif mode == 'gradient':
            colors = tuple(map(rgb, region['colors']))
            pairs = [tuple(map(rgb, pair)) for pair in RULES['gradients']]
            if len(colors) != 2 or not any(colors in (pair, pair[::-1]) for pair in pairs):
                add('gradient', 'REVISE', region=index, reason='Undocumented gradient endpoints')
                add('palette', 'REVISE', region=index, reason='Exposed design gradient uses colors outside the documented gradient palette')
                continue
            start, end = colors
            is_primary = colors in (pairs[0], pairs[0][::-1], pairs[1], pairs[1][::-1])
            if colors in (pairs[2], pairs[2][::-1]):
                allowed = abs(opacity*5-round(opacity*5)) < 1e-9
                add('gray_opacity', 'PASS' if allowed else 'REVISE', region=index, opacity=opacity,
                    allowed_opacities=[0, .2, .4, .6, .8, 1])
            geometry = region.get('geometry')
            inferred_plane = None
            if geometry in ('diagonal','linear') and opacity==1 and overlay is None:
                # Fit only a linear position field, then test EVERY actual pixel
                # against the documented RGB endpoint pair. This infers geometry
                # without trusting a supplied angle or fitting arbitrary artwork.
                delta = [b-a for a,b in zip(start,end)]
                denominator = sum(v*v for v in delta)
                samples=[]
                for iy in range(5):
                    for ix in range(5):
                        sx=x0+round((x1-x0-1)*ix/4);sy=y0+round((y1-y0-1)*iy/4)
                        p=image.getpixel((sx,sy))
                        t=sum((v-a)*d for v,a,d in zip(p,start,delta))/denominator
                        samples.append((sx,sy,t))
                mx=sum(s[0] for s in samples)/len(samples)
                my=sum(s[1] for s in samples)/len(samples)
                mt=sum(s[2] for s in samples)/len(samples)
                vx=sum((s[0]-mx)**2 for s in samples)
                vy=sum((s[1]-my)**2 for s in samples)
                if vx and vy and max(s[2] for s in samples)-min(s[2] for s in samples)>=.05:
                    ax=sum((s[0]-mx)*(s[2]-mt) for s in samples)/vx
                    ay=sum((s[1]-my)*(s[2]-mt) for s in samples)/vy
                    inferred_plane=(ax,ay,mt-ax*mx-ay*my)
            if geometry not in ('horizontal', 'vertical', 'radial') and inferred_plane is None:
                add('gradient', 'BLOCKED', region=index, reason='Supply horizontal/vertical/radial recipe; other geometry needs manual review')
                continue
            if geometry == 'radial':
                center = region.get('center')
                radii = region.get('radii')
                if not isinstance(center, list) or len(center) != 2 or not isinstance(radii, list) or len(radii) != 2:
                    raise ValueError('Radial center/radii must be coordinate pairs in final-image pixels')
                cx, cy = [number(v, 'radial center') for v in center]
                rx, ry = [number(v, 'radial radius', 1e-9) for v in radii]
        else:
            raise ValueError('Unsupported region mode')
        base = rgb(region['background']) if opacity != 1 else (0,0,0)
        opacity_complement = float(Decimal(1)-Decimal(str(opacity)))
        bad = 0
        maximum = 0
        for y in range(y0,y1):
            for x in range(x0,x1):
                t = 0
                if mode == 'gradient':
                    if geometry == 'horizontal':
                        t = (x-x0)/max(1,x1-x0-1)
                    elif geometry == 'vertical':
                        t = (y-y0)/max(1,y1-y0-1)
                    elif geometry=='radial':
                        t = min(1, math.hypot((x-cx)/rx,(y-cy)/ry))
                    else:
                        t = max(0,min(1,inferred_plane[0]*x+inferred_plane[1]*y+inferred_plane[2]))
                gradient_pixel = [round(a+(b-a)*t) for a,b in zip(start,end)]
                expected = [round(v*opacity + bg*opacity_complement) for v,bg in zip(gradient_pixel,base)]
                if overlay is not None:
                    expected = [round(v*alpha_complement+c*alpha) for v,c in zip(expected, overlay_rgb)]
                distance = max(abs(a-b) for a,b in zip(image.getpixel((x,y)),expected))
                bad += distance > tolerance
                maximum = max(maximum,distance)
        add('palette' if mode == 'solid' else 'gradient', 'REVISE' if bad else 'PASS',
            region=index, checked_pixels=(x1-x0)*(y1-y0), out_of_tolerance_pixels=bad,
            maximum_channel_error=maximum, tolerance=tolerance,
            scope='Match to supplied RGB recipe; rendering mismatch requires investigation')
        if overlay is not None:
            documented = (mode=='gradient' and
                ((overlay_rgb==(255,255,255) and is_primary) or
                 (overlay_rgb==rgb('004165') and colors in (pairs[2],pairs[2][::-1]))))
            add('transparency', 'PASS' if documented and not bad else 'INFO', region=index, opacity=alpha,
                reason='Actual pixels corroborate a documented color-layer treatment; 70% is not a universal requirement' if documented and not bad else
                       'Measured treatment needs manual interpretation; no universal opacity requirement')
        if is_primary:
            primary_draw.rectangle((x0,y0,x1-1,y1-1), fill=1)
    classified = coverage.histogram()[1]
    unknown = image.width*image.height-classified
    add('color_coverage', 'BLOCKED' if unknown else 'PASS', unclassified_pixels=unknown,
        scope='Declared coverage, not semantic validation of exclusion masks')
    total_design = design.histogram()[1]
    if not total_design:
        add('palette','BLOCKED',reason='No exposed design-color pixels were assigned for measurement')
    primary_count = primary.histogram()[1]
    add('color_dominance', 'INFO', declared_primary_area_pixels=primary_count,
        declared_design_area_pixels=total_design,
        primary_fraction=primary_count/total_design if total_design else None,
        reason='No numerical dominance threshold is specified by the manual')
    manual.append('B05 p.15: assess primary-color dominance; no invented percentage threshold')

    layers = required_list('layers', 'logo_overlap')
    layer_ids = [layer.get('id') for layer in layers]
    if any(not isinstance(value,str) or not value for value in layer_ids) or len(set(layer_ids)) != len(layer_ids):
        raise ValueError('Layers require unique nonempty IDs')
    for layer in layers:
        box(layer)
    faces = required_list('faces', 'face_overlap')
    face_boxes = [box(face) for face in faces]
    logos = required_list('logos', 'logo_source')
    text_runs = required_list('text_runs', 'font_family')
    identity = spec.get('identity')
    if not isinstance(identity, dict):
        add('identity','BLOCKED',reason='Declare custom_logo/custom_theme/custom_tagline independently of meeting topics')
    else:
        for field in ('custom_logo','custom_theme','custom_tagline'):
            flag = identity.get(field)
            if type(flag) is not bool:
                add('identity','BLOCKED',reason=field+' classification missing')
            else:
                allowed = not flag or context == 'annual-district-conference'
                add('identity','PASS' if allowed else 'BLOCKED',field=field,declared=flag,
                    declared_status='PASS' if allowed else 'REVISE',
                    evidence_basis='organizational-context declaration; semantic intent is not inferred from pixels',
                    reason='Declared custom organizational identity needs independent classification before an observed violation can be asserted' if not allowed else
                           'Conditional organizational context check; source/image classification remains required')

    logo_boxes = []
    badge_matches = {}
    for index, logo in enumerate(logos):
        bounds = box(logo)
        logo_boxes.append(bounds)
        x,y,r,b = bounds
        w,h = r-x,b-y
        kind = logo.get('kind')
        if kind not in ('ti','wordmark','lockup','member-badge','pathways','pathways-badge','gavel','corporate','conference','sponsor'):
            raise ValueError('Unsupported logo kind')
        official = kind in ('ti','wordmark','lockup','member-badge','pathways','pathways-badge','gavel')
        if official and logo.get('layer_id') not in layer_ids:
            add('logo_overlap','BLOCKED',logo=index,reason='Official logo must reference its own inventoried layer_id')
        if official:
            variant = logo.get('variant')
            variants = ('full-color','grayscale','white')
            if kind == 'wordmark':
                variants = ('full-color','black','white')
            elif kind == 'gavel':
                variants = ('loyal-blue','true-maroon','black')
            elif kind in ('lockup','member-badge','pathways-badge'):
                variants = ('official',)
            add('logo_source','PASS' if variant in variants else 'REVISE',logo=index,variant=variant,allowed=list(variants))
            if logo.get('era') == 'pre-2011' or logo.get('experimental') is True:
                add('logo_source','BLOCKED',logo=index,declared_status='REVISE',
                    evidence_basis='unverified source-era/experimental declaration',
                    reason='Claimed legacy/experimental status needs source corroboration; it is not an observed emblem violation')
        # Minimum size does not depend on having a source file.
        for unit, target, minimum in (
            ('px',spec.get('target_width_px'),72),
            ('in',spec.get('print_width_in'),1 if kind == 'pathways' else .75)):
            if official and target is not None and kind not in ('lockup','pathways-badge'):
                number(target,'output width',1e-9)
                measured = w*target/image.width
                add('logo_size','PASS' if measured >= minimum else 'REVISE',logo=index,width=measured,minimum=minimum,unit=unit)
        if official and kind!='pathways-badge' and spec.get('target_width_px') is None and spec.get('print_width_in') is None:
            add('logo_size','BLOCKED',logo=index,reason='Intended display/print size is missing')
        if official and kind=='lockup':
            add('logo_size','BLOCKED',logo=index,reason='No separate numeric minimum specified for this asset; establish applicable logo standard manually')
        if kind=='pathways-badge':
            add('logo_size','INFO',logo=index,eligibility='NOT_SPECIFIED',manual_pages=[22],
                reason='No independent numeric minimum is specified for Pathways badges; do not invent the primary Pathways-logo minimum')
        if not official:
            continue
        effects = logo.get('effects')
        if not isinstance(effects,list):
            add('logo_effects','BLOCKED',logo=index,reason='Logo effect inventory missing')
        elif 'patterned-glow' in effects:
            add('logo_effects','BLOCKED',logo=index,declared_status='REVISE',
                evidence_basis='unverified declared logo effect',
                reason='Patterned glow is prohibited, but the declared effect must be corroborated against actual surrounding pixels')
        elif effects:
            add('logo_effects','BLOCKED',logo=index,effects=effects,reason='Other visual effects require source review')
        else:
            add('logo_effects','PASS',logo=index)
        transform = logo.get('transform')
        if not isinstance(transform, dict) or any(k not in transform for k in ('rotation_deg','skew_x_deg','skew_y_deg','perspective')):
            add('logo_transform','BLOCKED',logo=index,reason='Source transform metadata missing')
        else:
            values = [number(abs(transform[k]), k) for k in ('rotation_deg','skew_x_deg','skew_y_deg')]
            # Manual explicitly forbids perspective and disproportionate scale;
            # arbitrary in-plane rotation needs review, not an invented rule.
            if transform['perspective'] is True or any(values[1:]):
                add('logo_transform','REVISE',logo=index,reason='Perspective/skew changes logo geometry')
            elif transform['perspective'] is not False:
                add('logo_transform','BLOCKED',logo=index,reason='Perspective must be explicit boolean')
            elif values[0]:
                add('logo_transform','BLOCKED',logo=index,reason='Rotated treatment needs visual/source review')
            else:
                add('logo_transform','PASS',logo=index)
        for layer in layers:
            if logo.get('layer_id') and layer.get('id') == logo.get('layer_id'):
                continue
            # Underlying photography is permitted; foreground copy is not.
            if layer.get('kind') not in ('background','photo') and overlap(bounds,box(layer)):
                add('logo_overlap','BLOCKED',logo=index,layer=layer.get('id'),reason='Foreground bounding boxes overlap; inspect actual ink before declaring an overlap violation')
        if any(overlap(bounds,face) for face in face_boxes):
            add('face_overlap','BLOCKED',logo=index,reason='Logo bounds overlap face bounds; verify ink/masks before declaring face coverage')
        else:
            add('face_overlap','PASS',logo=index,scope='Supplied face bounds only')
        if kind == 'pathways-badge':
            association = logo.get('association')
            if not association or logo.get('decorative') is not False:
                add('badge_relevance','BLOCKED',logo=index,reason='Associated path/project/program and non-decorative usage evidence required')
            else:
                add('badge_relevance','INFO',logo=index,association=association,reason='Association supplied; semantic relevance requires human review')
        if not logo.get('source'):
            add('logo_source','BLOCKED',logo=index,reason='An original reference source is required for visual comparison')
            continue
        source = root / logo['source']
        if not source.is_file():
            add('logo_source','BLOCKED',logo=index,reason='Original source file is unavailable; other measurements retained')
            continue
        if logo.get('source_sha256') is not None and digest(source) != logo['source_sha256']:
            add('logo_source','BLOCKED',logo=index,reason='Source checksum mismatch')
            continue
        if not logo.get('source_sha256'):
            add('logo_source','INFO',logo=index,source_sha256=digest(source),
                reason='Reference-file identity recorded; no trusted expected checksum was supplied. Visual comparison is separate from provenance verification')
        if not logo.get('provenance'):
            add('logo_source','BLOCKED',logo=index,reason='Official provenance evidence missing; matching an arbitrary source is insufficient')
        with Image.open(source) as original_file:
            source_image = original_file.convert('RGBA')
        if logo.get('source_bounds'):
            crop_bounds = rect(logo['source_bounds'],source_image.size)
            alpha_bounds = source_image.getchannel('A').getbbox()
            if alpha_bounds is not None and not (crop_bounds[0] <= alpha_bounds[0] and crop_bounds[1] <= alpha_bounds[1] and crop_bounds[2] >= alpha_bounds[2] and crop_bounds[3] >= alpha_bounds[3]):
                add('logo_source','BLOCKED',logo=index,reason='Source crop removes nontransparent pixels; only verified padding removal can be automated')
            source_image = source_image.crop(crop_bounds)
        expected_h = w*source_image.height/source_image.width
        proportions_ok = abs(h-expected_h) <= 1
        add('logo_proportions','PASS' if proportions_ok else 'REVISE',logo=index,
            actual_height=h,expected_height=expected_h,rounding_allowance_px=1)
        # An opaque foreground rectangle can be confirmed from actual pixels,
        # unlike an arbitrary bounding box which may contain only whitespace.
        confirmed_intruders = []
        alpha = source_image.getchannel('A').resize((w,h))
        reference_canvas = Image.new('RGBA',(w,h),rgb(logo.get('background','#FFFFFF'))+(255,))
        reference_canvas.alpha_composite(source_image.resize((w,h)))
        reference_canvas = reference_canvas.convert('RGB')
        for layer in layers:
            if layer.get('id')==logo.get('layer_id') or layer.get('kind')=='background':
                continue
            lb = box(layer)
            if not overlap(lb,bounds):
                continue
            patch = image.crop(lb)
            extrema = patch.getextrema()
            constant = all(low==high for low,high in extrema)
            intersection = (max(x,lb[0])-x,max(y,lb[1])-y,min(r,lb[2])-x,min(b,lb[3])-y)
            visible_ink = alpha.crop(intersection).getbbox() is not None
            different_ink = False
            for yy in range(intersection[1],intersection[3]):
                for xx in range(intersection[0],intersection[2]):
                    if alpha.getpixel((xx,yy)) >= 250 and max(abs(a-b) for a,b in zip(
                            image.getpixel((x+xx,y+yy)),reference_canvas.getpixel((xx,yy))))>30:
                        different_ink = True
                        break
                if different_ink:
                    break
            confirmed = constant and visible_ink and different_ink and tuple(low for low,high in extrema)!=rgb(logo.get('background','#FFFFFF'))
            if not confirmed and different_ink and patch.width*patch.height<=1000000:
                # A connected, nearly constant-color observed component that
                # extends from outside the logo into altered opaque official ink
                # corroborates actual foreground coverage (not just rectangles).
                data = list(pixels(patch))
                keys = [tuple(channel//8 for channel in p) for p in data]
                visited = bytearray(len(keys))
                bg_key = tuple(channel//8 for channel in rgb(logo.get('background','#FFFFFF')))
                for seed,key in enumerate(keys):
                    if visited[seed] or key==bg_key:
                        continue
                    pending=[seed];visited[seed]=1;outside=damaged=0
                    while pending:
                        point=pending.pop();px,py=point%patch.width,point//patch.width
                        gx,gy=lb[0]+px,lb[1]+py
                        if not (x<=gx<r and y<=gy<b):
                            outside+=1
                        elif alpha.getpixel((gx-x,gy-y))>=250 and max(abs(a-b) for a,b in zip(
                                data[point],reference_canvas.getpixel((gx-x,gy-y))))>30:
                            damaged+=1
                        neighbours=[]
                        if px:neighbours.append(point-1)
                        if px+1<patch.width:neighbours.append(point+1)
                        if py:neighbours.append(point-patch.width)
                        if py+1<patch.height:neighbours.append(point+patch.width)
                        for other in neighbours:
                            if not visited[other] and keys[other]==key:
                                visited[other]=1;pending.append(other)
                    if outside>=4 and damaged>=4:
                        confirmed=True
                        break
            if confirmed:
                confirmed_intruders.append(layer['id'])
                add('logo_overlap','REVISE',logo=index,layer=layer['id'],
                    evidence_basis='connected actual foreground pixels cross and alter opaque official source ink',
                    reason='Observed foreground component covers nontransparent official artwork; source pixels differ, not merely boxes')
        if 'background' not in logo:
            add('logo_source','BLOCKED',logo=index,reason='Visual comparison needs a declared uniform background; photographic underlays require review')
        else:
            comparison = helpers['compare_logo'](source_image, image.crop(bounds), rgb(logo['background']), bounds[:2])
            transform_changed = isinstance(transform,dict) and (transform.get('perspective') is True or
                                transform.get('skew_x_deg',0)!=0 or transform.get('skew_y_deg',0)!=0)
            substantial = comparison.get('metrics',{}).get('mean_channel_error',0)>12
            if comparison['status']=='BLOCKED' and (not proportions_ok or confirmed_intruders or (transform_changed and substantial)):
                comparison.update(status='REVISE',confirmed_appearance_change=True,
                    reason='Visual source mismatch is corroborated by measured distortion or actual opaque foreground coverage')
            if kind=='pathways-badge':
                badge_matches[index]=comparison['status']=='PASS'
            add('logo_source',comparison.pop('status'),logo=index,**comparison)
        if kind=='pathways-badge':
            add('logo_clear_space','INFO',logo=index,eligibility='NOT_SPECIFIED',manual_pages=[22],
                reason='No separate numeric wordmark-X requirement is specified for Pathways badges')
            continue
        wordmark = logo.get('source_wordmark_height_px')
        if type(wordmark) not in (float,int) or not math.isfinite(wordmark) or wordmark <= 0 or wordmark > source_image.height:
            add('logo_clear_space','BLOCKED',logo=index,reason='Verified source wordmark height needed')
        else:
            margin = math.ceil(wordmark*w/source_image.width)
            expanded = (x-margin,y-margin,r+margin,b+margin)
            if min(expanded[:2]) < 0 or expanded[2] > image.width or expanded[3] > image.height:
                add('logo_clear_space','REVISE',logo=index,required_margin_px=margin,reason='Clear space crosses canvas edge')
            else:
                intruders = [layer.get('id') for layer in layers
                             if not (logo.get('layer_id') and layer.get('id') == logo.get('layer_id')) and layer.get('kind') not in ('background','photo') and overlap(expanded,box(layer))]
                add('logo_clear_space','REVISE' if confirmed_intruders else 'BLOCKED' if intruders else 'PASS',logo=index,
                    intruding_bounds=intruders,required_margin_px=margin,scope='Supplied foreground bounding boxes; overlapping whitespace needs inspection')
                if 'background' in logo:
                    bg = rgb(logo['background'])
                    strips = ((x-margin,y-margin,r+margin,y),(x-margin,b,r+margin,b+margin),
                              (x-margin,y,x,b),(r,y,r+margin,b))
                    count = sum(p != bg for strip in strips for p in pixels(image.crop(strip)))
                    add('logo_clear_space','BLOCKED' if count else 'PASS',logo=index,
                        nonbackground_pixels=count,reason='Uniform-background ring test; nonuniform photography is not automatically forbidden')
                    if isinstance(effects,list) and 'patterned-glow' in effects:
                        bg=rgb(logo['background'])
                        scanlines=[]
                        for yy in (max(0,y-2),min(image.height-1,b+1)):
                            scanlines.append([image.getpixel((xx,yy)) for xx in range(x,r)])
                        for xx in (max(0,x-2),min(image.width-1,r+1)):
                            scanlines.append([image.getpixel((xx,yy)) for yy in range(y,b)])
                        periodic=False
                        for line in scanlines:
                            binary=[max(abs(c-base) for c,base in zip(p,bg))>20 for p in line]
                            transitions=sum(a!=b for a,b in zip(binary,binary[1:]))
                            fraction=sum(binary)/len(binary)
                            if transitions<6 or not .1<=fraction<=.9:continue
                            for lag in range(2,min(17,len(binary)//3)):
                                agreement=sum(a==b for a,b in zip(binary,binary[lag:]))/(len(binary)-lag)
                                if agreement>=.9:
                                    periodic=True;break
                            if periodic:break
                        if periodic:
                            add('logo_effects','REVISE',logo=index,
                                evidence_basis='actual repeated high-contrast color transitions around reference artwork',
                                reason='Declared patterned effect corroborated by periodic stripe structure in the actual logo surround')

    # Exact source text and font-role checks. A font declaration alone is not
    # proof of the actually resolved renderer font. Verify optional font files.
    if isinstance(identity,dict) and identity.get('custom_logo') is True and context!='annual-district-conference':
        observed_alteration=any(f['check']=='logo_source' and f['status']=='REVISE' and
                               (f.get('material_chromatic_change') or f.get('confirmed_appearance_change')) for f in findings)
        if observed_alteration:
            add('identity','REVISE',field='custom_logo',
                evidence_basis='supplied organizational-use intent corroborated by actual material logo alteration',
                reason='An actual altered official mark is declared to serve as custom organizational identity')
    phrase_runs = []
    all_text = []
    for index, run in enumerate(text_runs):
        first_finding = len(findings)
        text = run.get('text')
        if not isinstance(text,str):
            raise ValueError('Every text run needs text')
        bounds = box(run)
        observation = helpers['corroborate_text'](image,run,root)
        if observation.get('observed_text') is not None:
            text = observation['observed_text']
        all_text.append(text if observation['copy_status']=='PASS' else '')
        role = run.get('role')
        if role in ('tagline','marketing-phrase') and any(overlap(bounds,f) for f in face_boxes):
            add('face_overlap','BLOCKED',text_run=index,reason='Text bounds overlap face bounds; inspect actual glyphs/masks')
        if role == 'tagline':
            if run.get('language','en') != 'en':
                add('tagline','BLOCKED',text_run=index,reason='Translated official tagline requires separately verified approval')
            else:
                add('tagline','PASS' if text in RULES['taglines'] else 'REVISE',text_run=index,text=text)
        if role == 'marketing-phrase':
            phrase_runs.append(dict(run,text=text,_copy_corroborated=observation['copy_status']=='PASS'))
            if run.get('language','en') != 'en':
                add('marketing_phrases','BLOCKED',text_run=index,reason='Translated marketing phrase needs verified approval')
            else:
                add('marketing_phrases','PASS' if text in RULES['phrases'] else 'REVISE',text_run=index,text=text)
        family = observation.get('font_family') if observation['font_status'] == 'PASS' else run.get('font_family')
        font_role = run.get('font_role',role)
        allowed = RULES['headline_fonts'] if font_role in ('headline','subhead') else RULES['body_fonts']
        if spec.get('special_event') is True:
            allowed = allowed + RULES['special_event_fonts']
        if run.get('script','latin') != 'latin':
            add('font_family','INFO',text_run=index,eligibility='NOT_SPECIFIED',
                actual_font_identity=observation['font_status'],
                reason='Manual specifies no Chinese/non-Latin font whitelist; disclose actual fallback without inventing an approval requirement')
        elif not family:
            add('font_family','BLOCKED',text_run=index,reason='Resolved font family missing')
        else:
            add('font_family','PASS' if family in allowed else 'REVISE',text_run=index,font_family=family,font_role=font_role)
            font = observation.get('actual_font_file') if observation['font_status']=='PASS' else run.get('font_file')
            if font:
                path = root / font
                expected_hash = observation.get('font_file_sha256') if observation['font_status']=='PASS' else run.get('font_sha256')
                if not expected_hash or digest(path) != expected_hash:
                    add('font_family','BLOCKED',text_run=index,reason='Font file checksum missing/mismatched')
                else:
                    try:
                        from fontTools.ttLib import TTFont, TTLibError
                    except ImportError:
                        add('font_family','BLOCKED',text_run=index,reason='Install optional fontTools for font-file identity checks')
                    else:
                        try:
                            with TTFont(path) as actual:
                                names = {record.toUnicode() for record in actual['name'].names if record.nameID in (1,16)}
                        except (TTLibError, KeyError):
                            add('font_family','BLOCKED',text_run=index,reason='Invalid font file or missing family-name table')
                        else:
                            add('font_family','PASS' if family in names else 'REVISE',text_run=index,
                                source_families=sorted(names),scope='Font file identity; still requires proof this file rendered this text')
            if observation['font_status'] != 'PASS':
                add('font_family','BLOCKED',text_run=index,reason='Resolved-render font evidence required, not just manifest declaration')
        effects = observation.get('effects') if observation['effects_status'] == 'PASS' else run.get('effects')
        if not isinstance(effects,list):
            add('font_effects','BLOCKED',text_run=index,reason='Effects inventory missing')
        elif any(effect in ('word-art','drop-shadow','radical-manipulation') for effect in effects):
            add('font_effects','REVISE',text_run=index,effects=effects)
        elif effects:
            add('font_effects','BLOCKED',text_run=index,effects=effects,reason='Unrecognized effects need review')
        else:
            add('font_effects','PASS',text_run=index)
        for finding in findings[first_finding:]:
            if finding['check'] in ('tagline','marketing_phrases'):
                verified = observation['copy_status'] == 'PASS'
            elif finding['check'] == 'font_family':
                verified = observation['font_status'] == 'PASS'
            elif finding['check'] == 'font_effects':
                verified = observation['effects_status'] == 'PASS'
            else:
                continue
            finding['observed_status'] = finding['status'] if verified else 'BLOCKED'
            if finding['check']=='font_family' and run.get('script','latin')!='latin':
                finding['observed_status']='INFO'
            finding['declared_status'] = finding['status']
            finding['status'] = finding['observed_status']
            finding['evidence_basis'] = 'actual glyph/text pixels corroborated' if verified else 'unverified declaration'
            finding['image_evidence'] = observation
        if observation['copy_status'] != 'PASS':
            manual.append('Text run %d: supplied text has not been corroborated against actual pixels' % index)
    unique_phrases = {run['text'] for run in phrase_runs}
    observed_phrases = {run['text'] for run in phrase_runs if run['_copy_corroborated']}
    complete = all(run['_copy_corroborated'] for run in phrase_runs)
    count_status = 'REVISE' if len(observed_phrases)>1 else 'PASS' if complete else 'BLOCKED'
    add('marketing_phrases',count_status,count=len(observed_phrases),maximum=1,
        declared_count=len(unique_phrases),declared_status='REVISE' if len(unique_phrases)>1 else 'PASS',
        scope='Corroborated visible marketing phrases, excluding event titles and official tagline')
    # Scan unclassified exact official strings too, to catch incorrectly labeled phrases.
    visible = '\n'.join(all_text)
    for i,logo in enumerate(logos):
        if logo.get('kind')!='pathways-badge' or not badge_matches.get(i):
            continue
        association=logo.get('association')
        if isinstance(association,str) and association.strip() and association.casefold() in visible.casefold() and logo.get('decorative') is False:
            for finding in findings:
                if finding['check']=='badge_relevance' and finding.get('logo')==i:
                    finding.update(status='PASS',observed_status='PASS',
                        evidence_basis='verified displayed badge plus corroborated program-name copy; source association supplied',
                        reason='Associated program name appears in actual corroborated visible copy')
        elif logo.get('decorative') is True:
            for finding in findings:
                if finding['check']=='badge_relevance' and finding.get('logo')==i:
                    finding.update(status='REVISE',observed_status='REVISE',
                        evidence_basis='verified displayed badge with explicit decorative-use context',
                        reason='Displayed official badge is explicitly used as decoration rather than associated program content')
    detected = sum(phrase in visible for phrase in RULES['phrases'])
    if detected > 1:
        add('marketing_phrases','REVISE',detected_occurrences=detected,reason='Multiple official phrase occurrences in supplied visible text')

    ti_indices = [i for i,l in enumerate(logos) if l.get('kind') in ('ti','wordmark','lockup')]
    if context == 'gavel-club':
        gavel = [l for l in logos if l.get('kind') == 'gavel']
        add('gavel_identity','REVISE' if ti_indices else 'PASS',reason='Gavel must replace TI organizational identity',ti_logo_count=len(ti_indices))
        if not gavel:
            add('gavel_identity','BLOCKED',reason='Establish where a member club would use the logo and supply official Gavel replacement')
    if context == 'corporate-club':
        for i in ti_indices:
            for j,other in enumerate(logos):
                if other.get('kind') == 'corporate':
                    a,b = logo_boxes[i],logo_boxes[j]
                    if overlap(a,b):
                        add('corporate_placement','REVISE',logos=[i,j],reason='Corporate and TI logos overlap')
                    elif a[3] <= b[1] or b[3] <= a[1]:
                        add('corporate_placement','PASS',logos=[i,j],reason='Top/bottom separation verified')
                    else:
                        add('corporate_placement','BLOCKED',logos=[i,j],reason='Shared vertical band: inspect side-by-side prohibition versus opposite-side placement; no numeric separation specified')
    if context == 'annual-district-conference':
        conference = spec.get('conference',{})
        try:
            event_date = datetime.date.fromisoformat(conference.get('date',''))
            annual = conference.get('annual') is True
            add('conference','PASS' if annual and event_date.month in (4,5) else 'REVISE',date=event_date.isoformat(),annual=annual)
            as_of = datetime.date.fromisoformat(spec['as_of_date'])
            end = datetime.date.fromisoformat(conference.get('end_date',conference['date']))
            if end < event_date:
                raise ValueError('Conference end precedes start')
            add('conference','REVISE' if as_of > end else 'PASS',as_of=as_of.isoformat(),end_date=end.isoformat(),reason='Conference identity cannot be used after the event')
        except (ValueError,TypeError,KeyError):
            add('conference','BLOCKED',reason='Valid conference date/end_date and explicit as_of_date required')
        district = conference.get('district_number')
        if district is None:
            add('conference','BLOCKED',reason='District number missing')
        else:
            import re
            has_district = re.search(r'\bDistrict\s+'+re.escape(str(district))+r'\b',visible,re.I) is not None
            has_annual = 'annual conference' in visible.lower()
            add('conference','PASS' if has_district and has_annual else 'BLOCKED',
                district_number_present=has_district,annual_conference_present=has_annual,
                reason='English required identifiers checked; translated wording needs separate review')
        sponsor_sections = required_list('sponsor_sections','sponsor_placement')
        sponsor_boxes = [box(s) for s in sponsor_sections]
        for i, logo in enumerate(logos):
            if logo.get('kind') == 'sponsor':
                b = logo_boxes[i]
                contained = any(a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3] for a in sponsor_boxes)
                add('sponsor_placement','PASS' if contained else 'REVISE',logo=i,reason='Sponsor logo must be in a sponsor-designated section')
        for i, run in enumerate(text_runs):
            if run.get('role') == 'sponsor':
                b = box(run)
                contained = any(a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3] for a in sponsor_boxes)
                add('sponsor_placement','PASS' if contained else 'REVISE',text_run=i,reason='Sponsor name must be in a sponsor-designated section')
                if any(overlap(b,logo_boxes[j]) for j in ti_indices):
                    add('sponsor_placement','BLOCKED',text_run=i,reason='Sponsor text bounds overlap TI logo; inspect actual ink')
        for i in ti_indices:
            for j,other in enumerate(logos):
                if j == i:
                    continue
                a,b = logo_boxes[i],logo_boxes[j]
                if overlap(a,b):
                    add('sponsor_placement','REVISE',logos=[i,j],reason='TI logo must stand alone')
                elif max(a[1],b[1]) < min(a[3],b[3]):
                    add('sponsor_placement','BLOCKED',logos=[i,j],reason='Shared vertical band may be prohibited side-by-side placement; no distance threshold specified')
        manual.append('B15 p.41: theme/material Brand Team approval and third-party rights must be evidenced separately before distribution')
    # Contrast ratio is an engineering measurement, never a claimed manual cutoff.
    for item in required_list('contrast_pairs','contrast'):
        def luminance(color):
            channels = [v/255 for v in rgb(color)]
            linear = [c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in channels]
            return sum(c*w for c,w in zip(linear,(.2126,.7152,.0722)))
        a,b = sorted((luminance(item['foreground']),luminance(item['background'])))
        add('contrast','INFO',ratio=(b+.05)/(a+.05),scope='Declared colors; no numerical contrast cutoff specified by TI')
    manual.extend([
        'B01 pp.4–6: voice and tone require judgment',
        'B02 pp.12,28: accurate inventories, busy backgrounds, patterned glow, object integration, legibility and authentic official provenance require visual/source review',
        'B07 p.22: badge association relevance requires semantic review',
        'B08 pp.23–25: verify actual rendered fonts, standard styles and visual hierarchy; examples do not mandate H1/H2 weights universally',
        'B09 p.27: photography subject/context and secondary illustration prominence require judgment; image permissions require external evidence',
        'B10 pp.28–29: contrast, face inventory completeness and visual competition require judgment; corner placement is preferred, not mandatory',
        'B11 p.29: identify marketing claims versus factual topic copy; translations require evidence, not invented approval',
        'B12 pp.31,35–37,44: rights, authorization, distribution and experimental-status evidence are not verifiable from pixels',
    ])
    return findings, manual
