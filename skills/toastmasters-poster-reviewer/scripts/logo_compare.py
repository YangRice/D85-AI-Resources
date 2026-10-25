"""Local, compression-tolerant visual comparison; never authenticates a logo.

Thresholds are engineering screening settings, not Toastmasters brand rules.
No geometric registration, warping or color normalization can hide alterations.
"""
import io


def pixels(image):
    method = getattr(image,'get_flattened_data',None)
    return method() if method else image.getdata()


def jpeg_crop(reference, background, offset, quality=None, subsampling=2, qtables=None):
    """Reproduce the actual whole-canvas DCT/chroma block phase for a crop."""
    from PIL import Image
    block_x=16 if subsampling in (1,2) else 8
    block_y=16 if subsampling==2 else 8
    dx,dy=offset[0]%block_x,offset[1]%block_y
    padded=Image.new('RGB',(reference.width+dx+block_x,reference.height+dy+block_y),tuple(background))
    padded.paste(reference,(dx,dy))
    buffer=io.BytesIO()
    options=dict(format='JPEG',subsampling=subsampling)
    if qtables is not None:options['qtables']=qtables
    elif quality is not None:options['quality']=quality
    padded.save(buffer,**options)
    buffer.seek(0)
    with Image.open(buffer) as decoded:
        return decoded.crop((dx,dy,dx+reference.width,dy+reference.height)).convert('RGB')


def compare_rendered(reference, observed, background, offset=(0,0), jpeg_settings=None,
                     blur=.8, mean_limit=4, maximum_limit=40, fraction_limit=.03):
    """Bounded export-pipeline search shared by logo and glyph comparisons.

    This never changes geometry, hue or content. Parsed actual JPEG tables, when
    available, are tested first rather than guessing or weakening tolerances.
    """
    from PIL import ImageChops,ImageFilter,ImageStat
    reference,observed=reference.convert('RGB'),observed.convert('RGB')
    blurred_observed=observed.filter(ImageFilter.GaussianBlur(blur))
    best=None
    def assess(expected,quality,subsampling,actual_tables=False):
        nonlocal best
        exact=ImageChops.difference(expected,observed).getbbox() is None
        diff=ImageChops.difference(expected.filter(ImageFilter.GaussianBlur(blur)),blurred_observed)
        mean=sum(ImageStat.Stat(diff).mean)/3
        maximum=max(high for low,high in diff.getextrema())
        hist=diff.histogram()
        fraction=sum(sum(hist[c*256+13:(c+1)*256]) for c in range(3))/(reference.width*reference.height*3)
        metrics=dict(mean_channel_error=mean,max_blurred_channel_error=maximum,
                     channel_fraction_over_12=fraction,jpeg_quality=quality,
                     jpeg_subsampling=subsampling,actual_quantization_tables=actual_tables)
        matched=exact or (mean<=mean_limit and maximum<=maximum_limit and fraction<=fraction_limit)
        score=mean+fraction*100+maximum/20
        if best is None or score<best[0]:best=(score,metrics)
        return dict(matched=matched,exact=exact,metrics=metrics)
    result=assess(reference,None,None)
    if result['matched']:return result
    if jpeg_settings and jpeg_settings.get('qtables'):
        for subsampling in (jpeg_settings.get('subsampling',2),):
            if subsampling not in (0,1,2):continue
            result=assess(jpeg_crop(reference,background,offset,subsampling=subsampling,
                                    qtables=jpeg_settings['qtables']),None,subsampling,True)
            if result['matched']:return result
    for subsampling in (0,1,2):
        for quality in (95,85,70,55,40):
            result=assess(jpeg_crop(reference,background,offset,quality,subsampling),quality,subsampling)
            if result['matched']:return result
    # Refine quality around the best coarse export pipeline, keeping a bounded
    # search. This is inference of an export parameter, not fitting poster art.
    seed=best[1]
    if seed['jpeg_quality'] is not None and seed['mean_channel_error']<12:
        for quality in range(max(20,seed['jpeg_quality']-8),min(98,seed['jpeg_quality']+8)+1):
            result=assess(jpeg_crop(reference,background,offset,quality,seed['jpeg_subsampling']),quality,seed['jpeg_subsampling'])
            if result['matched']:return result
    return dict(matched=False,exact=False,metrics=best[1])


def compare(original, observed, background, offset=(0, 0), jpeg_settings=None):
    from PIL import Image, ImageChops, ImageFilter, ImageStat
    observed = observed.convert('RGB')
    size = observed.size
    methods = (Image.Resampling.LANCZOS, Image.Resampling.BICUBIC,
               Image.Resampling.BILINEAR, Image.Resampling.NEAREST)
    visibility=Image.new('RGBA',size,tuple(background)+(255,))
    visibility.alpha_composite(original.convert('RGBA').resize(size,Image.Resampling.LANCZOS))
    blank=Image.new('RGB',size,tuple(background))
    if ImageChops.difference(visibility.convert('RGB'),blank).getbbox() is None:
        return dict(status='BLOCKED',method='visibility evidence',
                    reason='Reference renders completely invisible on the declared background; blank pixels cannot verify a displayed logo')
    if ImageChops.difference(observed,blank).getbbox() is None:
        return dict(status='BLOCKED',method='visibility evidence',
                    reason='Candidate region contains no foreground pixels against the declared background')
    best = None
    matched=False
    for method in methods:
        reference = Image.new('RGBA', size, tuple(background)+(255,))
        reference.alpha_composite(original.convert('RGBA').resize(size, method))
        reference = reference.convert('RGB')
        result=compare_rendered(reference,observed,background,offset,jpeg_settings)
        metrics=dict(result['metrics'],resampling=int(method))
        if result['exact']:
                return dict(status='PASS', method='exact visual pixels',
                            scope='Visual consistency with supplied reference; not provenance or byte preservation')
        score=metrics['mean_channel_error']+metrics['channel_fraction_over_12']*100+metrics['max_blurred_channel_error']/20
        if result['matched']:
            best=(score,metrics);matched=True;break
        if best is None or score<best[0]:best=score,metrics
    metrics = best[1]
    # Diagnose only a large chromatic alteration with a matching silhouette.
    # Ordinary grayscale/white alternate variants and uncertain alignment remain
    # inconclusive without the correct reference, rather than false violations.
    expected_alpha = original.convert('RGBA').getchannel('A').resize(size,Image.Resampling.LANCZOS)
    ref = Image.new('RGBA',size,tuple(background)+(255,))
    ref.alpha_composite(original.convert('RGBA').resize(size,Image.Resampling.LANCZOS))
    ref = ref.convert('RGB')
    mask = list(pixels(expected_alpha))
    candidate_pixels = list(pixels(observed))
    reference_pixels = list(pixels(ref))
    intersection = union = chromatic = core = changed_core = 0
    error_sum = 0
    for a,p,q in zip(mask,candidate_pixels,reference_pixels):
        source_ink = a>128
        candidate_ink = max(abs(v-bg) for v,bg in zip(p,background))>20
        intersection += source_ink and candidate_ink
        union += source_ink or candidate_ink
        if a>=250:
            core += 1
            error = sum(abs(v-r) for v,r in zip(p,q))/3
            error_sum += error
            changed_core += error>40
            chromatic += max(p)-min(p)>25
    iou = intersection/union if union else 0
    material_recolor = (core>0 and iou>=.95 and error_sum/core>35 and
                       changed_core/core>=.5 and chromatic/core>=.5)
    # Strong changes across most opaque reference pixels are also material
    # when a patterned/colored backdrop expands the observed silhouette. Keep
    # grayscale/white alternatives and small compression deviations uncertain.
    material_core_change = (core>=size[0]*size[1]*.25 and error_sum/core>60 and
                            changed_core/core>.5 and chromatic/core>.5)
    # Small or featureless references cannot support tolerant shape validation.
    # Alpha-only white/black logos carry their structure in transparency; ignore
    # neither that structure nor its contrast with the actual declared backdrop.
    gray = ref.convert('L')
    edge_energy = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES).crop(
        (1,1,max(2,gray.width-1),max(2,gray.height-1)))).mean[0]
    eligible = min(size) >= 48 and edge_energy >= 2
    matched = (eligible and matched and metrics['mean_channel_error'] <= 4 and
               metrics['max_blurred_channel_error'] <= 40 and
               metrics['channel_fraction_over_12'] <= .03)
    return dict(status='PASS' if matched else 'REVISE' if material_recolor or material_core_change else 'BLOCKED',
                method='compression-tolerant visual screening', metrics=metrics,
                thresholds=dict(mean_channel_error=4, max_blurred_channel_error=40,
                                channel_fraction_over_12=.03, minimum_dimension=48,
                                minimum_reference_edge_energy=2),
                reference_edge_energy=edge_energy,
                silhouette_iou=iou,
                material_chromatic_change=material_recolor or material_core_change,
                opaque_core=dict(pixels=core,mean_channel_error=error_sum/core if core else None,
                    changed_fraction=changed_core/core if core else None,chromatic_fraction=chromatic/core if core else None),
                core_change_thresholds=dict(minimum_reference_coverage=.25,mean_channel_error_over=60,
                    changed_majority_over=.5,chromatic_majority_over=.5),
                reason='Visually consistent under tested resize/compression pipelines' if matched else
                       'Material non-neutral pixel/color changes across the opaque reference artwork; correct appearance or verify placement/reference' if material_recolor or material_core_change else
                       'Visual consistency not established; inspect alignment, compression damage or alteration',
                scope='Heuristic visual consistency only; small alterations may escape detection. Source authenticity and final visual review remain required.')
