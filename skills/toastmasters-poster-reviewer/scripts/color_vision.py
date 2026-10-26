"""Measure model-selected design pixels; never infer mask semantics or approval.

Lab distances are engineering screening settings, not Toastmasters tolerances.
K-means describes dominant colors; a second pixel-bucket check prevents a small
wrong color from disappearing into a large acceptable cluster.
"""
import math


def polygon_mask(size, regions):
    import cv2
    import numpy as np
    mask = np.zeros((size[1], size[0]), np.uint8)
    if not isinstance(regions, list):
        raise ValueError('Mask regions must be a list')
    for region in regions:
        if not isinstance(region, dict) or not region.get('reason'):
            raise ValueError('Every mask region needs an observation reason')
        points = region.get('polygon')
        if not isinstance(points, list) or len(points) < 3 or any(
                not isinstance(p, list) or len(p) != 2 or
                any(type(v) not in (int, float) or not math.isfinite(v) for v in p)
                for p in points):
            raise ValueError('Mask polygon needs at least three finite x/y points')
        # Continuous edge coordinates can reach width/height; fill clips at edge.
        if any(x < 0 or y < 0 or x > size[0] or y > size[1] for x, y in points):
            raise ValueError('Mask polygon outside image')
        pts = np.rint(points).astype(np.int32)
        if abs(cv2.contourArea(pts)) < 1:
            raise ValueError('Mask polygon has no area')
        cv2.fillPoly(mask, [pts], 1)
    return mask.astype(bool)


def lab(rgb):
    import cv2
    import numpy as np
    values = np.asarray(rgb, np.float32).reshape(-1, 1, 3) / 255
    return cv2.cvtColor(values, cv2.COLOR_RGB2LAB).reshape(-1, 3)


def kmeans(values, k):
    """Bounded Lloyd clustering with deterministic farthest-point initial seeds."""
    import numpy as np
    distinct = np.unique(values, axis=0)
    k = min(k, len(distinct))
    centers = [distinct[np.argmin(np.sum((distinct - values.mean(axis=0)) ** 2, axis=1))]]
    for _ in range(1, k):
        distance = np.min(np.sum((distinct[:, None] - np.asarray(centers)) ** 2, axis=2), axis=1)
        centers.append(distinct[np.argmax(distance)])
    centers = np.asarray(centers)
    for _ in range(30):
        labels = np.argmin(np.sum((values[:, None] - centers) ** 2, axis=2), axis=1)
        changed = np.asarray([values[labels == i].mean(axis=0) if np.any(labels == i)
                              else centers[i] for i in range(k)])
        if np.max(np.abs(changed - centers)) < .01:
            centers = changed
            break
        centers = changed
    return centers


def reference_colors(rules):
    import numpy as np
    solids = np.asarray([[int(key[i:i+2], 16) for i in (0, 2, 4)] for key in rules['colors']], float)
    points = [solids]
    for pair in rules['gradients']:
        endpoints = np.asarray([[int(key[i:i+2], 16) for i in (0, 2, 4)] for key in pair], float)
        t = np.linspace(0, 1, 129)[:, None]
        points.append(endpoints[0] * (1-t) + endpoints[1] * t)
    # Manual pp.19–20 documents white over primary colors and blue over gray.
    # Membership in a blend range does not certify its spatial/opacity recipe.
    for a,b in ((solids[0],[255,255,255]),(solids[1],[255,255,255]),(solids[0],solids[2])):
        t = np.linspace(0,1,129)[:,None]
        points.append(np.asarray(a)*(1-t)+np.asarray(b)*t)
    # Neutral ink/background is reported separately, never as additional brand swatches.
    points.append(np.repeat(np.arange(256)[:, None], 3, axis=1))
    return lab(np.vstack(points)), lab(solids[:2])


def nearest_distance(values, references):
    import numpy as np
    result = []
    for start in range(0, len(values), 1024):
        d = np.sum((values[start:start+1024, None] - references[None]) ** 2, axis=2)
        result.append(np.sqrt(d.min(axis=1)))
    return np.concatenate(result)


def inspect_colors(image, observation, rules):
    import cv2
    import numpy as np
    included = polygon_mask(image.size, observation.get('include', []))
    excluded = polygon_mask(image.size, observation.get('exclude', []))
    requested = included & ~excluded
    # Boundary pixels are explicitly unmeasured, not declared acceptable.
    stable = cv2.erode(requested.astype(np.uint8), np.ones((3, 3), np.uint8),
                       borderType=cv2.BORDER_CONSTANT, borderValue=0).astype(bool)
    rgb_image = np.asarray(image.convert('RGB'))
    # Rough model masks include type/icon edges. Their antialias mixtures are
    # not additional design swatches. Retain smooth gradients and flat fill
    # interiors; count high-variation details as unmeasured rather than wrong.
    local_span = cv2.dilate(rgb_image,np.ones((5,5),np.uint8)).astype(int)-cv2.erode(
        rgb_image,np.ones((5,5),np.uint8)).astype(int)
    detail = np.max(local_span,axis=2)>48
    uncertain_detail = int((stable & detail).sum())
    stable &= ~detail
    area = image.width * image.height
    counts = dict(included=int(included.sum()), excluded=int(excluded.sum()),
                  measured=int(stable.sum()), uncertain_boundary=int(requested.sum()-stable.sum())-uncertain_detail,
                  uncertain_detail=uncertain_detail,
                  unclassified=int((~(included | excluded)).sum()), canvas=area)
    common = dict(mask_counts=counts, mask_basis='supplied region classifications; not independently verified',
                  scope='Stable pixels inside supplied design masks only',
                  inventory_complete_claim=observation.get('inventory_complete') is True,
                  thresholds=dict(delta_e76_screening=12, material_delta_e76=20,
                                  material_component_pixels=16, boundary_erosion_px=1,
                                  detail_neighborhood_px=5,detail_rgb_span=48),
                  limitations=['No official numerical color-difference or dominance cutoff is claimed',
                               'Gradient color membership does not prove spatial geometry or approved opacity',
                               'Pixels excluded or unclassified by the model remain unassessed'])
    if counts['measured'] < 32:
        return dict(common, status='BLOCKED', reason='Insufficient design pixels; empty masks cannot pass')
    rgb_values = rgb_image[stable]
    values = lab(rgb_values)
    k = observation.get('requested_k', 6)
    if type(k) is not int or not 1 <= k <= 12:
        raise ValueError('requested_k must be an integer 1–12')
    # Limit fitting work, then assign ALL selected pixels to fitted centers.
    training = values[np.linspace(0, len(values)-1, min(20000, len(values)), dtype=int)]
    centers = kmeans(training, k)
    labels = np.empty(len(values), np.int32)
    for start in range(0, len(values), 10000):
        labels[start:start+10000] = np.argmin(
            np.sum((values[start:start+10000, None]-centers) ** 2, axis=2), axis=1)
    references, primaries = reference_colors(rules)
    clusters = []
    for i in range(len(centers)):
        members = labels == i
        n = int(members.sum())
        if not n:
            continue
        mean_rgb = np.rint(rgb_values[members].mean(axis=0)).astype(int)
        mean_lab = values[members].mean(axis=0)
        distance = float(nearest_distance(mean_lab[None], references)[0])
        clusters.append(dict(rgb=mean_rgb.tolist(), hex='#'+''.join(f'{v:02X}' for v in mean_rgb),
                             pixels=n, fraction=n/len(values), lab=mean_lab.tolist(),
                             nearest_allowed_delta_e76=distance,
                             membership='near-permitted-color' if distance <= 12 else 'review'))
    # Bucket-level checks are independent of k. Retain positions/area, not just histogram centers.
    keys, inverse, frequency = np.unique(rgb_values//8, axis=0, return_inverse=True, return_counts=True)
    bucket_means = np.stack([np.bincount(inverse, weights=rgb_values[:, c], minlength=len(keys))
                             / frequency for c in range(3)], axis=1)
    bucket_distance = nearest_distance(lab(bucket_means), references)
    outside = bucket_distance > 12
    def spatial_support(threshold):
        region=np.zeros(stable.shape,np.uint8)
        region[stable]=(bucket_distance[inverse]>threshold).astype(np.uint8)
        region=cv2.morphologyEx(region,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        count,_,stats,_=cv2.connectedComponentsWithStats(region,8)
        supported=[i for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>=16
                   and min(stats[i,cv2.CC_STAT_WIDTH],stats[i,cv2.CC_STAT_HEIGHT])>=4]
        return stats,supported
    stats,coherent=spatial_support(20)
    uncertain_stats,uncertain_regions=spatial_support(12)
    supported_uncertain_pixels=int(sum(uncertain_stats[i,cv2.CC_STAT_AREA] for i in uncertain_regions))
    wrong_pixels = int(frequency[outside].sum())
    material_pixels = int(sum(stats[i,cv2.CC_STAT_AREA] for i in coherent))
    regions = [dict(bounds=stats[i,:4].astype(int).tolist(),pixels=int(stats[i,cv2.CC_STAT_AREA]))
               for i in sorted(coherent,key=lambda j:stats[j,cv2.CC_STAT_AREA],reverse=True)[:12]]
    uncertain_bounds = [dict(bounds=uncertain_stats[i,:4].astype(int).tolist(),
                             pixels=int(uncertain_stats[i,cv2.CC_STAT_AREA]))
                        for i in sorted(uncertain_regions,
                            key=lambda j:uncertain_stats[j,cv2.CC_STAT_AREA],reverse=True)[:12]]
    offending = sorted([dict(rgb=np.rint(bucket_means[i]).astype(int).tolist(), pixels=int(frequency[i]),
                             delta_e76=float(bucket_distance[i])) for i in np.where(outside)[0]],
                       key=lambda v: v['pixels'], reverse=True)[:12]
    # Primary proximity is only a metric. No invented percentage becomes a brand gate.
    primary_distance = nearest_distance(lab(bucket_means), primaries)
    status = 'REVISE' if material_pixels else 'BLOCKED' if supported_uncertain_pixels else 'PASS'
    return dict(common, status=status, clusters=sorted(clusters, key=lambda c: c['pixels'], reverse=True),
                outside_screening_pixels=wrong_pixels, material_off_palette_pixels=material_pixels,
                spatially_supported_uncertain_pixels=supported_uncertain_pixels,
                isolated_outliers_assessed_as='Unresolved small detail/quantization pixels; not independent swatches or certified compliant pixels',
                material_regions=regions,
                uncertain_regions=uncertain_bounds,
                primary_near_fraction=float(frequency[primary_distance <= 12].sum()/len(values)),
                offending_buckets=offending,
                reason='Material off-palette color in supplied design masks' if material_pixels else
                       'Color differences require review' if wrong_pixels else
                       'Coherent design fills are visually consistent with permitted ranges/neutrals; isolated outliers remain disclosed')
