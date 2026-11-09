"""Composition/distribution invariants; these do not certify model behavior."""
import importlib.util
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('club_builder', ROOT/'scripts/build_portable_prompts.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
BY_ID = {s['id']: s for s in builder.CATALOG['skills']}
GROUPS = {
 'perform-toastmasters-meeting-role': ('prepare-saa-meeting-role','prepare-topicsmaster-role','prepare-table-topics-evaluation','prepare-ah-counter-role','prepare-grammarian-role','prepare-toastmaster-role','prepare-general-evaluator-role','prepare-timer-role','prepare-speech-evaluation'),
 'serve-toastmasters-club-officer': ('serve-club-president','serve-club-vpe','serve-club-vpm','serve-club-vppr','serve-club-secretary','serve-club-treasurer','serve-club-saa'),
 'mentor-toastmasters-member': ('establish-mentoring-agreement','coach-mentee-practice','practice-mentoring-conversation','review-mentoring-relationship'),
}

class ClubServicePackaging(unittest.TestCase):
    def test_aggregate_composition_reuses_existing_timer_and_evaluator(self):
        for parent, children in GROUPS.items():
            item=BY_ID[parent]
            self.assertEqual(item['type'],'journey')
            self.assertEqual(set(item['requires']+item['recommends']),set(children))
            self.assertFalse(item.get('portable_references'))
            for child in children:
                self.assertEqual(BY_ID[child]['type'],'atomic')
                self.assertEqual(BY_ID[child]['requires'],[])
                self.assertEqual(BY_ID[child]['recommends'],[])

    def test_all_atomic_content_and_references_are_bundled(self):
        for parent, children in GROUPS.items():
            for lang in ('en','zh'):
                with self.subTest(parent=parent,lang=lang):
                    output=builder.build_prompt(BY_ID[parent],lang)
                    for child in children:
                        self.assertIn(builder.resolve_actions(builder.skill_body(child,lang)).splitlines()[0],output)
                        for template in BY_ID[child].get('portable_references',[]):
                            ref=(ROOT/'skills'/child/'references'/template.format(lang=lang)).read_text().strip()
                            self.assertIn(ref,output)
                    self.assertNotIn('](references/',output)
                    self.assertNotIn('`action:',output)
                    self.assertEqual(output,(ROOT/'prompts'/f'{parent}.{lang}.md').read_text())

    def test_atomics_standalone_distribution(self):
        for child in {c for children in GROUPS.values() for c in children}:
            for lang in ('en','zh'):
                with self.subTest(child=child,lang=lang):
                    body=builder.skill_body(child,lang)
                    self.assertIsNotNone(body)
                    self.assertNotIn('`action:',body)
                    self.assertNotIn('](../',body)
                    out=builder.build_prompt(BY_ID[child],lang)
                    self.assertNotIn('](references/',out)
                    self.assertEqual(out,(ROOT/'prompts'/f'{child}.{lang}.md').read_text())

if __name__ == '__main__':
    unittest.main()
