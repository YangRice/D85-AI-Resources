"""Benchmark protocol regressions, independent of copyrighted fixture assets."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/benchmark_poster_brand.py'
spec=importlib.util.spec_from_file_location('poster_benchmark',SCRIPT)
benchmark=importlib.util.module_from_spec(spec);spec.loader.exec_module(benchmark)


class BenchmarkProtocol(unittest.TestCase):
    def test_global_blocked_does_not_hide_missed_defect(self):
        predictions=dict(round=1,samples=[dict(id='neutral',candidate_sha256='same',
            target_checks=['palette','logo_source'],features=dict(palette=dict(status='PASS'),logo_source=dict(status='BLOCKED')))])
        oracle=dict(samples=[dict(id='neutral',candidate_sha256='same',features=dict(palette=dict(status='REVISE'),logo_source=dict(status='BLOCKED')))])
        result=benchmark.score(predictions,oracle)
        self.assertEqual(result['counts']['false_accept'],1)
        self.assertEqual(result['counts']['agreement'],1)
        self.assertFalse(result['sample_results'][0]['all_features_agree'])

    def test_changed_candidate_cannot_use_an_old_review(self):
        predictions=dict(round=1,samples=[dict(id='neutral',candidate_sha256='changed',target_checks=[],features={})])
        oracle=dict(samples=[dict(id='neutral',candidate_sha256='original',features={})])
        with self.assertRaises(ValueError):
            benchmark.score(predictions,oracle)

    def test_literal_reference_decision_is_not_redefined_by_defect_first_summary(self):
        predictions=dict(round=1,samples=[dict(id='neutral',candidate_sha256='same',
            target_checks=['palette','logo_source'],features=dict(palette=dict(status='REVISE'),logo_source=dict(status='BLOCKED')))])
        oracle=dict(samples=[dict(id='neutral',candidate_sha256='same',scope_verdict='BLOCKED',
            features=dict(palette=dict(status='REVISE'),logo_source=dict(status='BLOCKED')))])
        result=benchmark.score(predictions,oracle)
        row=result['sample_results'][0]
        self.assertEqual(row['observed_scope_verdict'],'BLOCKED')
        self.assertEqual(row['reference_scope_verdict'],'BLOCKED')
        self.assertEqual(row['derived_defect_first_observed'],'REVISE')
        self.assertTrue(row['known_defect_detected'])
        self.assertTrue(row['literal_scope_agreement'])

    def test_omitting_a_hard_sample_or_feature_cannot_inflate_agreement(self):
        prediction=dict(id='easy',candidate_sha256='same',target_checks=['palette'],features=dict(palette=dict(status='PASS')))
        oracle=dict(samples=[dict(id='easy',candidate_sha256='same',features=dict(palette=dict(status='PASS'))),
                             dict(id='hard',candidate_sha256='other',features=dict(logo_source=dict(status='REVISE')))])
        with self.assertRaisesRegex(ValueError,'sample set'):
            benchmark.score(dict(round=1,samples=[prediction]),oracle)
        oracle['samples']=oracle['samples'][:1]
        oracle['samples'][0]['features']['font_family']=dict(status='REVISE')
        with self.assertRaisesRegex(ValueError,'feature set'):
            benchmark.score(dict(round=1,samples=[prediction]),oracle)

    def test_duplicate_sample_ids_cannot_hide_failures(self):
        case=dict(id='one',candidate_sha256='same',target_checks=['palette'],features=dict(palette=dict(status='PASS')))
        oracle=dict(samples=[dict(id='one',candidate_sha256='same',features=dict(palette=dict(status='PASS')))])
        with self.assertRaisesRegex(ValueError,'duplicate'):
            benchmark.score(dict(round=1,samples=[case,case]),oracle)

    def test_mutating_checker_cannot_claim_a_frozen_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            checker=root/'check_brand.py'
            checker.write_text('''from pathlib import Path
def inspect(image,config,root):
    Path(__file__).write_text("# changed during run\\n")
    return {"findings":[],"feature_results":{}}
def feature_results(findings):
    return {}
''',encoding='utf-8')
            (root/'brand_rules.json').write_text('{}',encoding='utf-8')
            (root/'spec.json').write_text('{}',encoding='utf-8')
            (root/'candidate.png').write_bytes(b'synthetic identity only')
            manifest=root/'manifest.json'
            manifest.write_text(json.dumps(dict(round=1,samples=[dict(id='neutral',image='candidate.png',spec='spec.json',target_checks=[])])),encoding='utf-8')
            original=benchmark.SCRIPT
            try:
                benchmark.SCRIPT=checker
                with self.assertRaisesRegex(ValueError,'changed during prediction'):
                    benchmark.predict(manifest)
            finally:
                benchmark.SCRIPT=original


if __name__=='__main__':
    unittest.main()
