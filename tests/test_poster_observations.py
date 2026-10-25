"""Pixel corroboration must never certify a bare text/font declaration."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image,ImageDraw,ImageFont
except ImportError:
    Image=None

SCRIPT=Path(__file__).resolve().parents[1]/'skills/toastmasters-poster-reviewer/scripts/check_brand.py'
spec=importlib.util.spec_from_file_location('observation_brand',SCRIPT)
brand=importlib.util.module_from_spec(spec);spec.loader.exec_module(brand)


@unittest.skipIf(Image is None,'Pillow required')
class PixelTextEvidence(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
        font=ImageFont.load_default(size=28)
        if not hasattr(font.path,'getvalue'):
            self.skipTest('Pillow embedded test font unavailable')
        self.path=self.root/'embedded-test-font.ttf'
        self.path.write_bytes(font.path.getvalue())
        self.font=ImageFont.truetype(str(self.path),28)
        self.image=Image.new('RGB',(360,80),'white')
        ImageDraw.Draw(self.image).text((10,10),'Find Your Voice',font=self.font,fill='black',anchor='lt')
        self.run=dict(text='Find Your Voice',bounds=[10,10,280,40],font_family='Invented Claimed Family',
            render_evidence=dict(font_file=str(self.path),font_sha256=brand.digest(self.path),
                font_size_px=28,origin=[10,10],color='black',background='white',anchor='lt'))

    def test_actual_glyphs_verify_copy_and_measure_font(self):
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['copy_status'],'PASS')
        self.assertEqual(result['font_status'],'PASS')
        self.assertNotEqual(result['font_family'],self.run['font_family'])

    @unittest.skipUnless(shutil.which('tesseract'),'Tesseract OCR is optional')
    def test_ocr_evidence_uses_explicit_tsv_and_language(self):
        image=Image.new('RGB',(420,100),'white')
        ImageDraw.Draw(image).text((12,18),'Bright Vision',font=self.font,fill='black',anchor='lt')
        run={'text':'Bright Vision','bounds':[0,0,300,80], 'role':'body',
             'font_role':'body','language':'en','script':'latin','effects':[]}
        result=brand.corroborate_text(image,run,self.root,{'ocr_lang':'eng'})
        self.assertEqual(result.get('ocr_language'),'eng')
        self.assertEqual(result.get('copy_status'),'PASS',result)

    def test_string_assertion_cannot_verify_font_or_effects(self):
        self.run['render_evidence']='Trust the renderer'
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'BLOCKED')
        self.assertEqual(result['effects_status'],'BLOCKED')

    def test_blank_outside_crop_cannot_match(self):
        self.run['bounds']=[0,50,200,20]
        self.run['render_evidence']['origin']=[1000,1000]
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'BLOCKED')
        self.assertEqual(result['copy_status'],'BLOCKED')

    def test_invisible_glyphs_cannot_match_blank_region(self):
        self.run['render_evidence']['color']='white'
        self.image.paste('white',(0,0,360,80))
        self.assertEqual(brand.corroborate_text(self.image,self.run,self.root)['font_status'],'BLOCKED')

    def test_changed_actual_pixels_do_not_verify_recipe(self):
        self.image.paste('red',(10,10,290,50))
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'BLOCKED')

    def test_nonstandard_stroke_does_not_certify_no_effects(self):
        self.run['bounds']=[5,5,290,50]
        self.run['render_evidence'].update(stroke_width=2,stroke_fill='black')
        ImageDraw.Draw(self.image).text((10,10),self.run['text'],font=self.font,fill='black',anchor='lt',stroke_width=2,stroke_fill='black')
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'PASS')
        self.assertEqual(result['effects_status'],'BLOCKED')

    def test_unverified_conditional_pass_is_not_observed_pass(self):
        results=brand.feature_results([dict(check='font_family',status='PASS',observed_status='BLOCKED',evidence_basis='unverified declaration')])
        self.assertEqual(results['font_family']['status'],'BLOCKED')

    def test_known_defect_survives_other_abstentions(self):
        results=brand.feature_results([dict(check='logo_size',status='REVISE'),dict(check='logo_size',status='BLOCKED')])
        self.assertEqual(results['logo_size']['status'],'REVISE')

    def test_actual_shadow_overrides_false_no_effects_claim(self):
        self.run['bounds']=[5,5,300,55]
        self.run['effects']=[]
        self.image.paste('white',(0,0,360,80))
        draw=ImageDraw.Draw(self.image)
        draw.text((13,13),self.run['text'],font=self.font,fill='black',anchor='lt')
        draw.text((10,10),self.run['text'],font=self.font,fill='black',anchor='lt')
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'PASS')
        self.assertEqual(result['effects'],['drop-shadow'])

    def test_nonblack_shadow_color_is_inferred_from_actual_residual_pixels(self):
        self.run['bounds']=[5,5,300,55]
        self.run['effects']=[]
        self.image.paste('white',(0,0,360,80))
        draw=ImageDraw.Draw(self.image)
        draw.text((13,14),self.run['text'],font=self.font,fill='#772432',anchor='lt')
        draw.text((10,10),self.run['text'],font=self.font,fill='black',anchor='lt')
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'PASS')
        self.assertEqual(result['effects'],['drop-shadow'])
        self.assertEqual(result['shadow_offset'],[3,4])

    def test_documented_large_shadow_offset_is_verified_against_pixels(self):
        self.run['bounds']=[5,5,310,60]
        self.run['render_evidence']['shadow_offset']=[13,8]
        self.image.paste('white',(0,0,360,80))
        draw=ImageDraw.Draw(self.image)
        draw.text((23,18),self.run['text'],font=self.font,fill='#772432',anchor='lt')
        draw.text((10,10),self.run['text'],font=self.font,fill='black',anchor='lt')
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['font_status'],'PASS',result)
        self.assertEqual(result['effects'],['drop-shadow'])
        self.assertEqual(result['shadow_offset'],[13,8])

    def test_false_shadow_hint_does_not_invent_an_effect(self):
        self.run['render_evidence']['shadow_offset']=[13,8]
        result=brand.corroborate_text(self.image,self.run,self.root)
        self.assertEqual(result['effects_status'],'PASS')
        self.assertEqual(result['effects'],[])

    def test_compressed_glyph_recipe_keeps_font_evidence(self):
        import io
        from PIL import JpegImagePlugin
        data=io.BytesIO();self.image.save(data,format='JPEG',quality=63,subsampling=0)
        data.seek(0)
        with Image.open(data) as decoded:
            settings=dict(qtables=decoded.quantization,subsampling=JpegImagePlugin.get_sampling(decoded))
            result=brand.corroborate_text(decoded,self.run,self.root,jpeg_settings=settings)
        self.assertEqual(result['font_status'],'PASS',result)


if __name__=='__main__':
    unittest.main()
