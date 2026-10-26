"""Execute neutral existing cases on the visual route, retaining untested scopes.

Does not read intended labels or prior reviewer answers. Outputs are local only.
Optional crops expose the detected logo plus clear-space margin for inspection.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'skills/toastmasters-poster-reviewer/scripts'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(manifest_path, output, artifacts=None):
    from PIL import Image
    import cv2
    if output.exists():raise ValueError('Refuse to overwrite a frozen output')
    if artifacts is not None:
        if artifacts.exists():raise ValueError('Artifacts directory must be fresh')
        artifacts.mkdir(parents=True)
    paths=sorted(FOLDER.glob('*.py'))+[FOLDER/'brand_rules.json',Path(__file__)]
    revision={str(p.relative_to(ROOT)):sha(p) for p in paths}
    manifest_hash=sha(manifest_path)
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    loaded=importlib.util.spec_from_file_location('vision_benchmark_brand',FOLDER/'check_brand.py')
    module=importlib.util.module_from_spec(loaded);loaded.loader.exec_module(module)
    predictions,skipped,seen=[],[],set()
    for sample in manifest['samples']:
        identifier=sample['id']
        if identifier in seen:raise ValueError('Duplicate case id')
        seen.add(identifier)
        checks=sample['target_checks']
        if not checks:
            skipped.append(dict(id=identifier,reason='Original targets outside implemented vision scope',
                                source_target_checks=sample.get('source_target_checks',[])))
            continue
        image_path=manifest_path.parent/sample['image']
        spec_path=manifest_path.parent/sample['observations']
        before=(sha(image_path),sha(spec_path))
        spec=json.loads(spec_path.read_text(encoding='utf-8'))
        if set(spec.get('requested_checks',[]))!=set(checks):
            raise ValueError('Observation scope differs from neutral manifest')
        result=module.inspect(image_path,spec,spec_path.parent)
        if before!=(sha(image_path),sha(spec_path)):
            raise ValueError('Candidate or observations changed during execution')
        if any(sha(Path(p))!=v for p,v in result['reference_file_sha256'].items()):
            raise ValueError('Reference changed during execution')
        crops=[]
        if artifacts is not None:
            with Image.open(image_path) as image:
                for i,logo in enumerate(result['logo_measurements']):
                    selected=logo.get('selected',{})
                    quad=selected.get('detection',{}).get('polygon')
                    if not quad:continue
                    margin=selected.get('clear_space',{}).get('required_margin_px',0)
                    # Field name is explicit in the logo module; unknown margin
                    # is shown as artwork-only crop rather than a fabricated X.
                    import math
                    left=max(0,math.floor(min(p[0] for p in quad)-margin))
                    top=max(0,math.floor(min(p[1] for p in quad)-margin))
                    right=min(image.width,math.ceil(max(p[0] for p in quad)+margin))
                    bottom=min(image.height,math.ceil(max(p[1] for p in quad)+margin))
                    path=artifacts/f'{len(predictions):03d}-logo-{i}.png'
                    image.crop((left,top,right,bottom)).save(path)
                    crops.append(dict(path=str(path),bounds=[left,top,right-left,bottom-top],
                                      sha256=sha(path),requested_margin_px=margin))
        predictions.append(dict(id=identifier,candidate_sha256=before[0],observations_sha256=before[1],
                                target_checks=checks,origin=spec.get('producer'),result=result,crops=crops))
    if revision!={str(p.relative_to(ROOT)):sha(p) for p in paths} or sha(manifest_path)!=manifest_hash:
        raise ValueError('Code or manifest changed during run; rerun after freezing revision')
    counts={s:sum(f['status']==s for p in predictions for f in p['result']['feature_results'].values())
            for s in ('PASS','REVISE','BLOCKED','INFO')}
    report=dict(format='tm-poster-vision-benchmark/v1',manifest_sha256=manifest_hash,
                checker_revision=revision,revision_stable=True,
                environment=dict(python=platform.python_version(),opencv=cv2.__version__),
                counts=counts,evaluated_cases=len(predictions),out_of_scope_cases=len(skipped),
                samples=predictions,untested=skipped,
                limitation='Execution on selected feature scopes; no new independent accuracy or Luna parity claim')
    with output.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--artifacts',type=Path)
    args=parser.parse_args()
    result=run(args.manifest.resolve(),args.out.resolve(),args.artifacts.resolve() if args.artifacts else None)
    print(json.dumps(dict(output=str(args.out),sha256=sha(args.out),counts=result['counts'],
                          evaluated=result['evaluated_cases'],out_of_scope=result['out_of_scope_cases']),indent=2))


if __name__=='__main__':main()
