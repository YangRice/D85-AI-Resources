"""Image-based logo measurements; thresholds are disclosed screening settings.

SIFT locates a supplied reference. Geometry is judged in the original poster,
before rectification. Appearance matching never proves official provenance.
OpenCV/numpy are imported only when this optional route is executed.
"""
import math


THRESHOLDS = {
    'sift_ratio': .72, 'minimum_inliers': 8, 'minimum_inlier_fraction': .55,
    'maximum_reprojection_error_px': 3.0, 'minimum_reference_hull_fraction': .08,
    'geometry_pass_ratio': 1.06, 'geometry_revise_ratio': 1.12,
    'template_minimum_score': .78, 'template_minimum_edge_recall': .55,
    'lab_mean_pass': 11.0, 'lab_mean_revise': 24.0,
    'lab_changed_fraction_revise': .55, 'lab_changed_threshold': 22.0,
    'comparison_blur_sigma_px': .8,
    'local_delta_e76': 35.0, 'local_minimum_area_fraction': .0015,
    'local_minimum_area_pixels': 40, 'local_opening_kernel_px': 3,
    'negative_space_background_delta_e76': 12.0,
    'negative_space_background_fraction': .96,
    'negative_space_minimum_background_samples': 32,
    'negative_space_sample_band_fraction': .12,
    'maximum_analysis_dimension': 1800,
}


def _result(status, reason, **details):
    return dict(status=status, reason=reason, **details)


def _box(bounds, size):
    if (not isinstance(bounds, list) or len(bounds) != 4 or
            any(type(v) is not int for v in bounds)):
        raise ValueError('Logo region must be integer [x,y,width,height]')
    x, y, w, h = bounds
    if min(x, y) < 0 or min(w, h) <= 0 or x+w > size[0] or y+h > size[1]:
        raise ValueError('Logo region outside image')
    return x, y, w, h


def _project(points, matrix):
    import cv2
    import numpy as np
    return cv2.perspectiveTransform(np.asarray(points, np.float32).reshape(-1, 1, 2), matrix).reshape(-1, 2)


def _detect(reference, alpha, search, offset, hint=None):
    import cv2
    import numpy as np
    cv2.setRNGSeed(0)
    height, width = reference.shape[:2]
    sh, sw = search.shape[:2]
    factor = min(1., THRESHOLDS['maximum_analysis_dimension']/max(sh, sw))
    # A supplied approximate box can make small wordmark/line features readable
    # to SIFT. This scaling changes coordinates, never measured geometry.
    factor = max(factor, min(2., 500/max(sh, sw)))
    scene = cv2.resize(search, None, fx=factor, fy=factor)
    gray = cv2.cvtColor(scene, cv2.COLOR_RGB2GRAY)
    sift = cv2.SIFT_create(nfeatures=3500, contrastThreshold=.025, edgeThreshold=15)
    scene_keys, scene_desc = sift.detectAndCompute(gray, None)
    diagnostics = {'scene_keypoints': len(scene_keys), 'attempts': []}
    for reference_width in (400, 220, 110):
        scale = reference_width/width
        model = cv2.resize(reference, None, fx=scale, fy=scale)
        mask = cv2.resize(alpha, (model.shape[1], model.shape[0]))
        keys, desc = sift.detectAndCompute(cv2.cvtColor(model, cv2.COLOR_RGB2GRAY), mask)
        if desc is None or scene_desc is None or len(scene_desc) < 2:
            continue
        pairs = cv2.BFMatcher().knnMatch(desc, scene_desc, k=2)
        good = [a for pair in pairs if len(pair) == 2 for a,b in [pair]
                if a.distance < THRESHOLDS['sift_ratio']*b.distance]
        entry = {'reference_width': reference_width, 'matches': len(good)}
        diagnostics['attempts'].append(entry)
        if len(good) < THRESHOLDS['minimum_inliers']:
            continue
        source = np.float32([keys[m.queryIdx].pt for m in good])/scale
        target = np.float32([scene_keys[m.trainIdx].pt for m in good])/factor
        matrix, inliers = cv2.findHomography(source, target, cv2.RANSAC, 3.0,
                                            maxIters=2500, confidence=.995)
        if matrix is None or inliers is None:
            continue
        selected = inliers.ravel().astype(bool)
        count = int(selected.sum())
        fraction = count/len(good)
        hull = cv2.contourArea(cv2.convexHull(source[selected]))/(width*height) if count >= 3 else 0
        error = float(np.median(np.linalg.norm(_project(source[selected], matrix)-target[selected], axis=1)))
        entry.update(inliers=count, inlier_fraction=fraction, reference_hull_fraction=hull,
                     median_reprojection_error_px=error)
        if (count < THRESHOLDS['minimum_inliers'] or
                fraction < THRESHOLDS['minimum_inlier_fraction'] or
                hull < THRESHOLDS['minimum_reference_hull_fraction'] or
                error > THRESHOLDS['maximum_reprojection_error_px']):
            continue
        shift = np.array([[1.,0.,offset[0]],[0.,1.,offset[1]],[0.,0.,1.]])
        return shift@matrix, 'SIFT + RANSAC homography', diagnostics

    # Translation/scale fallback for sparse wordmarks. Search a bounded range of
    # sizes, then verify actual edge recall, rather than accepting one maximum.
    scene_edge = cv2.Canny(cv2.cvtColor(search, cv2.COLOR_RGB2GRAY), 50, 130)
    center = hint[2] if hint else min(sw*.75, width)
    sizes = sorted(set(max(24, round(center*r)) for r in (.6,.75,.85,.95,1.,1.05,1.15,1.3,1.5)))
    best = None
    for candidate_width in sizes:
        candidate_height = round(candidate_width*height/width)
        if candidate_width > sw or candidate_height > sh or candidate_height < 12:
            continue
        model = cv2.resize(reference, (candidate_width,candidate_height))
        edges = cv2.Canny(cv2.cvtColor(model, cv2.COLOR_RGB2GRAY), 50, 130)
        if int((edges>0).sum()) < 25:
            continue
        matches = cv2.matchTemplate(scene_edge, edges, cv2.TM_CCOEFF_NORMED)
        _, score, _, where = cv2.minMaxLoc(matches)
        x,y = where
        actual = scene_edge[y:y+candidate_height,x:x+candidate_width]
        near = cv2.dilate(actual, np.ones((3,3), np.uint8))
        recall = float((near[edges>0]>0).mean())
        if best is None or score > best[0]:
            best = (score, recall, x, y, candidate_width, candidate_height)
    if best:
        score, recall, x, y, w, h = best
        diagnostics['template'] = dict(score=float(score), edge_recall=recall)
        if score >= THRESHOLDS['template_minimum_score'] and recall >= THRESHOLDS['template_minimum_edge_recall']:
            matrix = np.array([[w/width,0,x+offset[0]],[0,h/height,y+offset[1]],[0,0,1.]], dtype=float)
            return matrix, 'bounded multiscale edge template', diagnostics
    return None, None, diagnostics


def _geometry(matrix, width, height):
    import numpy as np
    quad = _project([[0,0],[width,0],[width,height],[0,height]], matrix)
    sides = np.roll(quad,-1,axis=0)-quad
    lengths = np.linalg.norm(sides,axis=1)
    if min(lengths) < 8 or not np.isfinite(quad).all():
        return None, _result('BLOCKED','Detected geometry is degenerate')
    # At the artwork center, homography's Jacobian preserves the actual
    # anisotropy/skew which appearance rectification would otherwise remove.
    x,y = width/2,height/2
    denominator = matrix[2,0]*x+matrix[2,1]*y+matrix[2,2]
    if abs(denominator) < 1e-8:
        return None, _result('BLOCKED','Detected homography crosses infinity')
    u,v = _project([[x,y]],matrix)[0]
    jacobian = (matrix[:2,:2]-np.outer([u,v],matrix[2,:2]))/denominator
    singular = np.linalg.svd(jacobian, compute_uv=False)
    if min(singular)<1e-8:
        return None,_result('BLOCKED','Detected geometry has no finite two-dimensional scale')
    anisotropy = float(max(singular)/min(singular))
    perspective = float(max(lengths[0]/lengths[2],lengths[2]/lengths[0],
                            lengths[1]/lengths[3],lengths[3]/lengths[1]))
    cosine = float(abs(np.dot(jacobian[:,0],jacobian[:,1])) /
                   (np.linalg.norm(jacobian[:,0])*np.linalg.norm(jacobian[:,1])))
    worst = max(anisotropy,perspective)
    reflected=bool(np.linalg.det(jacobian)<0)
    status = 'REVISE' if reflected or worst > THRESHOLDS['geometry_revise_ratio'] or cosine > .12 else (
        'PASS' if worst <= THRESHOLDS['geometry_pass_ratio'] and cosine <= .04 else 'BLOCKED')
    return quad, _result(status,'Original poster transform measured before rectification',
        anisotropy=anisotropy,opposite_edge_ratio=perspective,axis_cosine=cosine,reflected=reflected,
        rotation_degrees=float(math.degrees(math.atan2(jacobian[1,0],jacobian[0,0]))),
        polygon=quad.tolist(),matrix=matrix.tolist(),rounding_and_localization_allowance='screening thresholds, not brand exemptions')


def _negative_space(poster, observed_lab, alpha, valid, matrix, source_size, observation):
    """Check enclosed transparent holes without treating a photo as extra ink.

    Opaque-only residuals can match a white outline superimposed on an altered
    colored globe. A supported match also needs its enclosed transparent holes
    to agree with the locally verified backdrop. Open exterior transparency is
    excluded: colored logos may sit over arbitrary photographs legitimately.
    """
    import cv2
    import numpy as np
    filled=np.zeros(alpha.shape,np.uint8)
    contours,_=cv2.findContours((alpha>16).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(filled,contours,-1,1,cv2.FILLED)
    interior=cv2.erode(((alpha<8)&(filled>0)).astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
    interior &= valid
    minimum_area=max(THRESHOLDS['local_minimum_area_pixels'],
                     math.ceil(alpha.size*THRESHOLDS['local_minimum_area_fraction']))
    pixels=int(interior.sum())
    if pixels<minimum_area:
        return _result('INFO','No measurable enclosed transparent interior',pixels=pixels)

    # Sample a narrow annulus outside the actual source rectangle. The source
    # is alpha-tight; samples are background evidence rather than white ink or
    # transparent holes whose content is the subject of this check.
    width,height=source_size
    band=THRESHOLDS['negative_space_sample_band_fraction']
    grid=np.linspace(-band,1+band,20)
    locations=np.array([(x*width,y*height) for x in grid for y in grid
                        if x<0 or x>1 or y<0 or y>1],np.float32)
    projected=_project(locations,matrix)
    coords=np.rint(projected).astype(int)
    inside=(coords[:,0]>=0)&(coords[:,1]>=0)&(coords[:,0]<poster.shape[1])&(coords[:,1]<poster.shape[0])
    coords=np.unique(coords[inside],axis=0)
    if len(coords)<THRESHOLDS['negative_space_minimum_background_samples']:
        return _result('BLOCKED','Enclosed transparent interior needs visible exterior-background evidence',
                       pixels=pixels,background_samples=len(coords))
    rgb=poster[coords[:,1],coords[:,0]].astype(np.float32)/255
    samples=cv2.cvtColor(rgb.reshape(-1,1,3),cv2.COLOR_RGB2LAB).reshape(-1,3)
    background=np.median(samples,axis=0)
    threshold=THRESHOLDS['negative_space_background_delta_e76']
    fraction=float((np.linalg.norm(samples-background,axis=1)<=threshold).mean())
    details=dict(pixels=pixels,background_samples=len(coords),background_lab=background.tolist(),
                 uniform_background_fraction=fraction,
                 comparison_basis='Enclosed transparent pixels versus independently sampled local exterior background')
    if fraction<THRESHOLDS['negative_space_background_fraction']:
        return _result('BLOCKED','Backdrop is not locally uniform; transparent-interior content remains unassessed',**details)
    difference=np.linalg.norm(observed_lab-background,axis=2)
    components=[]
    for cutoff in (threshold,THRESHOLDS['local_delta_e76']):
        mask=cv2.morphologyEx(((difference>cutoff)&interior).astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        count,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
        components.append([dict(bounds=[int(v) for v in row[:4]],pixels=int(row[4]))
                           for row in stats[1:] if row[4]>=minimum_area and min(row[2:4])>=4])
    details.update(uncertain_components=components[0],material_components=components[1])
    # A uniform exterior does not establish what is behind transparent holes:
    # an allowed photo could occupy just the globe interior. Require an explicit
    # model/source assertion before calling inconsistent interior content a
    # defect. Without it, withhold the match rather than condemning the photo.
    asserted=observation.get('background_uniform_across_logo') is True
    color=observation.get('background')
    consistent=False
    if asserted and color is not None:
        expected=np.array([int(color.lstrip('#')[i:i+2],16) for i in (0,2,4)],np.float32)/255
        expected_lab=cv2.cvtColor(expected.reshape(1,1,3),cv2.COLOR_RGB2LAB)[0,0]
        consistent=bool(np.linalg.norm(expected_lab-background)<=threshold)
    details.update(uniform_across_logo_asserted=asserted,
                   supplied_background_matches_exterior=consistent,
                   assertion_basis='Supplied model/source fact; exterior samples do not independently prove interior backdrop')
    status=('REVISE' if components[1] and consistent else
            'BLOCKED' if components[0] or components[1] else 'PASS')
    return _result(status,'Transparent-interior consistency against locally verified uniform background',**details)


def _appearance(poster, reference, alpha, matrix, observation):
    import cv2
    import numpy as np
    height,width = reference.shape[:2]
    inverse = np.linalg.inv(matrix)
    actual = cv2.warpPerspective(poster,inverse,(width,height),flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT)
    valid = cv2.warpPerspective(np.full(poster.shape[:2],255,np.uint8),inverse,(width,height))>250
    # Use a bounded comparison resolution. Sampling a large source reconstructed
    # from a tiny crop must not pretend to create new detail.
    quad = _project([[0,0],[width,0],[width,height],[0,height]],matrix)
    observed_width = float(np.linalg.norm(quad[1]-quad[0]))
    out_width = min(450,max(24,round(observed_width)))
    out_height = max(8,round(height*out_width/width))
    ref = cv2.resize(reference,(out_width,out_height),interpolation=cv2.INTER_AREA)
    obs = cv2.resize(actual,(out_width,out_height),interpolation=cv2.INTER_AREA)
    comparison_alpha=cv2.resize(alpha,(out_width,out_height))
    comparison_valid=cv2.resize(valid.astype(np.uint8),(out_width,out_height),interpolation=cv2.INTER_NEAREST)>0
    core = comparison_alpha>245
    core = cv2.erode(core.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
    core &= comparison_valid
    if core.sum() < 50:
        return _result('BLOCKED','Insufficient visible opaque artwork pixels')
    # A symmetric subpixel low-pass reduces resize/JPEG edge ringing without
    # recoloring, moving or normalizing either image. Retain raw residuals too.
    raw_ref_lab=cv2.cvtColor(ref.astype(np.float32)/255,cv2.COLOR_RGB2LAB)
    raw_obs_lab=cv2.cvtColor(obs.astype(np.float32)/255,cv2.COLOR_RGB2LAB)
    sigma=THRESHOLDS['comparison_blur_sigma_px']
    ref_lab = cv2.cvtColor(cv2.GaussianBlur(ref,(0,0),sigma).astype(np.float32)/255,cv2.COLOR_RGB2LAB)
    obs_lab = cv2.cvtColor(cv2.GaussianBlur(obs,(0,0),sigma).astype(np.float32)/255,cv2.COLOR_RGB2LAB)
    residual = (obs_lab-ref_lab)[core]
    distances = np.linalg.norm(residual,axis=1)
    mean = float(distances.mean()); changed = float((distances>THRESHOLDS['lab_changed_threshold']).mean())
    # A local altered element must not disappear into the whole-logo average.
    # Remove thin JPEG/registration fringes, then inspect surviving spatial
    # components at the actual observed resolution. Do not use histogram/PCA
    # similarity to override coherent high-error patches.
    delta_map=np.linalg.norm(obs_lab-ref_lab,axis=2)
    local_mask=((delta_map>THRESHOLDS['local_delta_e76']) & core).astype(np.uint8)
    kernel=THRESHOLDS['local_opening_kernel_px']
    opened=cv2.morphologyEx(local_mask,cv2.MORPH_OPEN,np.ones((kernel,kernel),np.uint8))
    count,labels,stats,_=cv2.connectedComponentsWithStats(opened,8)
    minimum_area=max(THRESHOLDS['local_minimum_area_pixels'],
                     math.ceil(out_width*out_height*THRESHOLDS['local_minimum_area_fraction']))
    local_components=[]
    for component in range(1,count):
        x,y,w,h,area=map(int,stats[component])
        if area>=minimum_area and min(w,h)>=4:
            component_errors=delta_map[labels==component]
            local_components.append(dict(bounds=[x,y,w,h],pixels=area,
                mean_delta_e76=float(component_errors.mean()),
                coordinate_space='aligned comparison image pixels'))
    local_change=bool(local_components)
    covariance = np.cov(residual.T)
    values = np.linalg.eigvalsh(covariance)[::-1]
    histogram_distance = []
    for channel,range_ in ((0,(0,100)),(1,(-128,128)),(2,(-128,128))):
        a=np.histogram(ref_lab[:,:,channel][core],bins=24,range=range_)[0].astype(float)
        b=np.histogram(obs_lab[:,:,channel][core],bins=24,range=range_)[0].astype(float)
        histogram_distance.append(float(np.abs(a/a.sum()-b/b.sum()).sum()/2))
    status = ('REVISE' if local_change or (mean>THRESHOLDS['lab_mean_revise'] and changed>THRESHOLDS['lab_changed_fraction_revise'])
              else 'PASS' if mean<=THRESHOLDS['lab_mean_pass'] and changed<.18 else 'BLOCKED')
    negative_space=_negative_space(poster,obs_lab,comparison_alpha,comparison_valid,matrix,(width,height),observation)
    if negative_space['status']=='REVISE':
        status='REVISE'
    elif status=='PASS' and negative_space['status']=='BLOCKED':
        status='BLOCKED'
    return _result(status,'Aligned spatial Lab differences; histograms/PCA are diagnostic, not independent verdicts',
        mean_delta_e76=mean,p95_delta_e76=float(np.percentile(distances,95)),changed_core_fraction=changed,
        raw_mean_delta_e76=float(np.linalg.norm((raw_obs_lab-raw_ref_lab)[core],axis=1).mean()),
        comparison_blur_sigma_px=sigma,
        localized_change=local_change,localized_components=local_components,
        localized_minimum_area_pixels=minimum_area,comparison_size=[out_width,out_height],
        negative_space=negative_space,
        core_pixels=int(core.sum()),lab_histogram_total_variation=histogram_distance,
        residual_pca_eigenvalues=values.tolist(),evidence_basis='actual aligned opaque pixels; reference provenance remains external')


def _clear_space(poster, alpha, matrix, quad, observation):
    import cv2
    import numpy as np
    ratio=observation.get('wordmark_height_ratio')
    if type(ratio) not in (int,float) or not math.isfinite(ratio) or not 0 < ratio <= 1:
        return _result('BLOCKED','Applicable source wordmark-height ratio is required'), _result('BLOCKED','Clear-space ring unavailable')
    h,w=poster.shape[:2]
    artwork_width=float((np.linalg.norm(quad[1]-quad[0])+np.linalg.norm(quad[2]-quad[3]))/2)
    margin=artwork_width*ratio
    localization=max(1.5,artwork_width*.008)
    x0,y0=quad.min(axis=0);x1,y1=quad.max(axis=0)
    gaps=np.array([x0,y0,w-x1,h-y1])
    projected_ring=np.zeros((h,w),np.uint8)
    expanded=_project([[-ratio*alpha.shape[1],-ratio*alpha.shape[1]],
                        [(1+ratio)*alpha.shape[1],-ratio*alpha.shape[1]],
                        [(1+ratio)*alpha.shape[1],alpha.shape[0]+ratio*alpha.shape[1]],
                        [-ratio*alpha.shape[1],alpha.shape[0]+ratio*alpha.shape[1]]],matrix)
    # Project the source-space margin before assessing canvas or foreground
    # clearance. A rotated corner can extend beyond an axis-aligned margin.
    ex0,ey0=expanded.min(axis=0);ex1,ey1=expanded.max(axis=0)
    expanded_gaps=np.array([ex0,ey0,w-ex1,h-ey1])
    boundary=('REVISE' if min(expanded_gaps)<-localization else
              'BLOCKED' if min(expanded_gaps)<localization else 'PASS')
    cv2.fillConvexPoly(projected_ring,np.round(expanded).astype(np.int32),1)
    cv2.fillConvexPoly(projected_ring,np.round(quad).astype(np.int32),0)
    intruders=[];uncertain_intruders=[]
    for index,bounds in enumerate(observation.get('foreground_regions',[])):
        x,y,rw,rh=_box(bounds,(w,h))
        if max(x,ex0)<min(x+rw,ex1) and max(y,ey0)<min(y+rh,ey1):
            # Bounds alone may contain whitespace. Require visible local ink;
            # nonuniform/photo backgrounds cannot be judged as intruders here.
            patch=poster[y:y+rh,x:x+rw]
            bg=observation.get('background')
            if isinstance(bg,str):
                color=np.array([int(bg.lstrip('#')[i:i+2],16) for i in (0,2,4)])
                visible=np.max(np.abs(patch.astype(float)-color),axis=2)>30
                if (visible & (projected_ring[y:y+rh,x:x+rw]>0)).sum()>=4:
                    intruders.append(index)
            else:
                uncertain_intruders.append(index)
    status='REVISE' if boundary=='REVISE' or intruders else boundary
    if (status=='PASS' and observation.get('foreground_complete') is not True and
            observation.get('foreground_inventory_complete') is not True):
        # On a uniform observed ring actual pixels can establish absence of
        # foreground. On photos the model must supply a completed inventory.
        bg=observation.get('background')
        uniform=False
        if isinstance(bg,str) and projected_ring.sum()>0:
            color=np.array([int(bg.lstrip('#')[i:i+2],16) for i in (0,2,4)])
            delta=np.max(np.abs(poster.astype(float)-color),axis=2)
            uniform=bool((delta[projected_ring>0]<=20).mean()>=.98)
        if not uniform:status='BLOCKED'
    if status=='PASS' and uncertain_intruders:status='BLOCKED'
    space=_result(status,'Canvas-edge gaps and supplied foreground regions; textures alone are not violations',
        required_margin_px=margin,localization_allowance_px=localization,canvas_gaps_px=gaps.tolist(),
        expanded_canvas_gaps_px=expanded_gaps.tolist(),
        confirmed_foreground_regions=intruders,uncertain_foreground_regions=uncertain_intruders,
        foreground_inventory_asserted=observation.get('foreground_complete') is True or
            observation.get('foreground_inventory_complete') is True,
        polygon=expanded.tolist())
    # Diagnose extra ink/shadow around the projected alpha only when the user
    # supplies a genuinely uniform backdrop; textured photography stays INFO.
    bg=observation.get('background')
    if not isinstance(bg,str):
        return space,_result('INFO','Effect screening needs uniform-background evidence; textured backgrounds are permitted')
    color=np.array([int(bg.lstrip('#')[i:i+2],16) for i in (0,2,4)],float)
    projected=cv2.warpPerspective(alpha,matrix,(w,h))>16
    radius=max(2,round(artwork_width*.025))
    outside=cv2.dilate(projected.astype(np.uint8),np.ones((2*radius+1,2*radius+1),np.uint8))>0
    near=cv2.dilate(projected.astype(np.uint8),np.ones((5,5),np.uint8))>0
    ring=outside&~near
    # Verify the backdrop beyond the candidate effect halo. Using an immediately
    # adjacent band would include a real offset shadow and defeat its own test.
    far_outer=cv2.dilate(projected.astype(np.uint8),np.ones((8*radius+1,8*radius+1),np.uint8))>0
    far_inner=cv2.dilate(projected.astype(np.uint8),np.ones((6*radius+1,6*radius+1),np.uint8))>0
    far=far_outer&~far_inner
    difference=np.max(np.abs(poster.astype(float)-color),axis=2)
    background_verified=bool(far.sum()>10 and (difference[far]<=20).mean()>=.96)
    extra=ring&(difference>35)
    count=int(extra.sum());fraction=float(count/max(1,int(ring.sum())))
    effects= _result('REVISE' if background_verified and count>=max(15,artwork_width*.2) and fraction>.08 else
                    'PASS' if background_verified and fraction<.02 else 'BLOCKED',
        'Extra observed ink outside projected artwork on verified uniform background',
        uniform_background_verified=background_verified,extra_ink_pixels=count,ring_fraction=fraction,
        interpretation='Extra ink may be shadow/glow or foreground intrusion; appearance alone cannot identify its authoring effect')
    return space,effects


def inspect_logo(image, reference, observation):
    """Measure one reference candidate within a model-supplied search region.

    The caller should try permitted variants and retain uncertainty when several
    match. Bounds/ROI are localization hints, never verdict or source proof.
    """
    import cv2
    import numpy as np
    if not isinstance(observation,dict):raise ValueError('Logo observation must be an object')
    poster=np.array(image.convert('RGB'))
    blocked=lambda reason: {key:_result('BLOCKED',reason) for key in
        ('detection','geometry','appearance','clear_space','effects','size')}
    source=reference.convert('RGBA')
    tight=source.getchannel('A').getbbox()
    if tight is None:return blocked('Reference has no visible artwork')
    source=source.crop(tight)
    if min(source.size)<8:return blocked('Reference is too small')
    background=observation.get('background')
    if background is not None:
        if not isinstance(background,str) or len(background.lstrip('#'))!=6:
            raise ValueError('Background must be #RRGGBB')
        bg=tuple(int(background.lstrip('#')[i:i+2],16) for i in (0,2,4))
    else:
        bg=(0,65,101)
    from PIL import Image
    composed=Image.new('RGBA',source.size,bg+(255,));composed.alpha_composite(source)
    ref=np.array(composed.convert('RGB'));alpha=np.array(source.getchannel('A'))
    roi=observation.get('roi')
    hint=observation.get('bounds')
    if roi is not None:x,y,w,h=_box(roi,image.size)
    elif hint is not None:
        hx,hy,hw,hh=_box(hint,image.size);pad=max(8,round(max(hw,hh)*.25))
        x,y=max(0,hx-pad),max(0,hy-pad);w=min(image.width,hx+hw+pad)-x;h=min(image.height,hy+hh+pad)-y
    else:x,y,w,h=0,0,image.width,image.height
    matrix,method,diagnostics=_detect(ref,alpha,poster[y:y+h,x:x+w],(x,y),hint)
    result={'detection':_result('BLOCKED','No reliable reference match; absence is not proved'),
            'geometry':_result('BLOCKED','No reliable localization'),
            'appearance':_result('BLOCKED','No reliable localization'),
            'clear_space':_result('BLOCKED','No reliable localization'),
            'effects':_result('BLOCKED','No reliable localization'),
            'size':_result('BLOCKED','No reliable localization'),
            'diagnostics':diagnostics,'engineering_thresholds':dict(THRESHOLDS),
            'reference_tight_bounds':list(tight),'reference_tight_size':list(source.size)}
    if matrix is None:return result
    quad,geometry=_geometry(matrix,source.width,source.height)
    if quad is None:return result
    area=abs(cv2.contourArea(quad.astype(np.float32)))
    if not cv2.isContourConvex(quad.astype(np.float32)) or area<100 or area>image.width*image.height*1.05:
        return result
    result['detection']=_result('PASS','Located supplied reference appearance, not provenance',method=method,polygon=quad.tolist())
    result['geometry']=geometry
    result['appearance']=_appearance(poster,ref,alpha,matrix,observation)
    result['clear_space'],result['effects']=_clear_space(poster,alpha,matrix,quad,observation)
    target=observation.get('target_width_px')
    if target is None:result['size']=_result('BLOCKED','Intended output width not supplied')
    elif type(target) not in (int,float) or not math.isfinite(target) or target<=0:
        raise ValueError('Intended output width must be positive and finite')
    else:
        width=float(min(np.linalg.norm(quad[1]-quad[0]),np.linalg.norm(quad[2]-quad[3]))*target/image.width)
        result['size']=_result('REVISE' if width<70 else 'PASS' if width>=74 else 'BLOCKED',
            'Applicable 72 px digital minimum with localization uncertainty; no print-size claim',
            measured_width_px=width,minimum_width_px=72,localization_allowance_px=2)
    return result
