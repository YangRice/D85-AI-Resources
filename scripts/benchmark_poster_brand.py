#!/usr/bin/env python3
"""Run unlabelled poster specimens and score a separately frozen reviewer oracle.

The run command never reads an oracle. Score consumes already saved predictions,
so held-out labels cannot influence the run. No images/third-party assets are
copied to the repository or sent to network services.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'skills/toastmasters-poster-reviewer/scripts/check_brand.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predict(manifest_path):
    manifest_hash = sha(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    module_spec = importlib.util.spec_from_file_location('brand_benchmark',SCRIPT)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    files = sorted(SCRIPT.parent.glob('*.py')) + [SCRIPT.parent/'brand_rules.json']
    revision = {path.name:sha(path) for path in files}
    revision['benchmark_poster_brand.py'] = sha(Path(__file__))
    predictions = []
    for sample in manifest['samples']:
        spec_path = manifest_path.parent/sample['spec']
        image = manifest_path.parent/sample['image']
        candidate_hash = sha(image)
        spec_hash = sha(spec_path)
        config = json.loads(spec_path.read_text(encoding='utf-8'))
        config['_evidence_bundle'] = sample.get('evidence',{})
        evidence_hashes = {}
        for key,value in sample.get('evidence',{}).items():
            paths = value if isinstance(value,list) else [value]
            for value_path in paths:
                if isinstance(value_path,str) and not value_path.startswith(('http:','https:')):
                    path = manifest_path.parent/value_path
                    if path.is_file():
                        evidence_hashes[str(path)] = sha(path)
        result = module.inspect(image,config,spec_path.parent)
        features = result.get('feature_results',module.feature_results(result['findings']))
        for check,selector in sample.get('target_selectors',{}).items():
            if check not in sample['target_checks'] or not isinstance(selector,dict):
                raise ValueError('Invalid target selector for '+check)
            selected = [f for f in result['findings'] if f['check']==check and
                        all(f.get(key)==value for key,value in selector.items())]
            features[check] = module.feature_results(selected).get(check,dict(status='BLOCKED',reason='No finding matches entity selector'))
        if sha(image)!=candidate_hash or sha(spec_path)!=spec_hash or any(sha(Path(path))!=value for path,value in evidence_hashes.items()):
            raise ValueError('Input evidence changed during prediction for '+sample['id'])
        predictions.append(dict(id=sample['id'],candidate_sha256=candidate_hash,spec_sha256=spec_hash,
                                input_evidence_sha256=evidence_hashes,
                                target_checks=sample['target_checks'],
                                target_selectors=sample.get('target_selectors',{}),
                                features={key:features.get(key,dict(status='BLOCKED',reason='No finding emitted')) for key in sample['target_checks']},
                                all_features=features,result=result))
    after_revision = {path.name:sha(path) for path in files}
    after_revision['benchmark_poster_brand.py'] = sha(Path(__file__))
    if revision!=after_revision or manifest_hash!=sha(manifest_path):
        raise ValueError('Checker or manifest changed during prediction; run is not a frozen revision')
    return dict(format='tm-poster-benchmark-predictions/v1',round=manifest['round'],
                manifest_sha256=manifest_hash,checker_revision=revision,revision_stable=True,samples=predictions)


def score(predictions,oracle):
    def indexed(samples,label):
        values={}
        for sample in samples:
            identifier=sample.get('id')
            if not isinstance(identifier,str) or not identifier or identifier in values:
                raise ValueError(label+' contains a missing or duplicate sample ID')
            values[identifier]=sample
        return values
    actual_samples=indexed(predictions['samples'],'Predictions')
    oracle_samples=indexed(oracle['samples'],'Oracle')
    if set(actual_samples)!=set(oracle_samples):
        raise ValueError('Prediction sample set must exactly match the frozen oracle; omitted/extra cases cannot be scored as success')
    expected = {sample['id']:sample for sample in oracle['samples']}
    comparisons = []
    sample_results = []
    confusion = {name:0 for name in ('agreement','mismatch','false_accept','false_reject','abstention','missing_oracle')}
    for sample in predictions['samples']:
        truth = expected.get(sample['id'],{})
        sample_comparisons = []
        if truth.get('candidate_sha256') != sample['candidate_sha256']:
            raise ValueError('Oracle/prediction candidate mismatch for '+sample['id'])
        targets=sample['target_checks']
        if len(targets)!=len(set(targets)) or set(targets)!=set(truth.get('features',{})) or set(sample['features'])!=set(targets):
            raise ValueError('Prediction target feature set must exactly match the frozen oracle for '+sample['id'])
        for feature in sample['target_checks']:
            expected_feature = truth.get('features',{}).get(feature)
            actual = sample['features'][feature]['status']
            wanted = expected_feature.get('status') if isinstance(expected_feature,dict) else expected_feature
            if wanted is None:
                confusion['missing_oracle'] += 1
                classification = 'missing_oracle'
            elif actual == wanted:
                confusion['agreement'] += 1
                classification = 'agreement'
            else:
                confusion['mismatch'] += 1
                if actual == 'PASS' and wanted in ('REVISE','BLOCKED'):
                    confusion['false_accept'] += 1; classification='false_accept'
                elif actual == 'REVISE' and wanted == 'PASS':
                    confusion['false_reject'] += 1; classification='false_reject'
                elif actual == 'BLOCKED' and wanted in ('PASS','REVISE'):
                    confusion['abstention'] += 1; classification='abstention'
                else:
                    classification='mismatch'
            comparisons.append(dict(id=sample['id'],feature=feature,expected=wanted,observed=actual,
                                    classification=classification,oracle_evidence=expected_feature,
                                    expected_checker_input_status=expected_feature.get('expectedCheckerInputStatus') if isinstance(expected_feature,dict) else None))
            sample_comparisons.append(comparisons[-1])
        actual_states = [row['observed'] for row in sample_comparisons]
        expected_states = [row['expected'] for row in sample_comparisons]
        def verdict(states):
            return 'REVISE' if 'REVISE' in states else 'BLOCKED' if 'BLOCKED' in states or None in states else 'PASS'
        def conservative(states):
            return 'BLOCKED' if 'BLOCKED' in states or None in states else 'REVISE' if 'REVISE' in states else 'PASS'
        literal=truth.get('scope_verdict')
        observed=conservative(actual_states)
        sample_results.append(dict(id=sample['id'],observed_scope_verdict=observed,
                                   expected_scope_verdict=literal if literal is not None else conservative(expected_states),
                                   reference_scope_verdict=literal,
                                   literal_scope_agreement=observed==literal if literal is not None else None,
                                   derived_defect_first_observed=verdict(actual_states),
                                   derived_defect_first_expected=verdict(expected_states),
                                   known_defect_detected='REVISE' in actual_states,
                                   reference_has_known_defect='REVISE' in expected_states,
                                   all_features_agree=all(row['classification']=='agreement' for row in sample_comparisons)))
    total = len(comparisons)-confusion['missing_oracle']
    literal_rows=[row for row in sample_results if row['reference_scope_verdict'] is not None]
    return dict(format='tm-poster-benchmark-score/v2',round=predictions['round'],counts=confusion,
                compared_features=total,agreement_fraction=confusion['agreement']/total if total else None,
                literal_scope_decisions=dict(compared=len(literal_rows),agreement=sum(row['literal_scope_agreement'] for row in literal_rows)),
                comparisons=comparisons,sample_results=sample_results,
                limitation='Scoped synthetic/collected evidence, not a guarantee of real-world whole-brand correctness')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    run=commands.add_parser('run');run.add_argument('--manifest',required=True,type=Path);run.add_argument('--out',required=True,type=Path)
    evaluate=commands.add_parser('score');evaluate.add_argument('--predictions',required=True,type=Path);evaluate.add_argument('--oracle',required=True,type=Path);evaluate.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    if args.command=='run':
        result=predict(args.manifest.resolve())
    else:
        result=score(json.loads(args.predictions.read_text(encoding='utf-8')),json.loads(args.oracle.read_text(encoding='utf-8')))
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(output=str(args.out),sha256=sha(args.out),round=result['round'],counts=result.get('counts')),indent=2))


if __name__=='__main__':
    main()
