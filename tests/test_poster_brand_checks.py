"""Actual PNG measurements with synthetic art, not redistributed TI assets."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/toastmasters-poster-reviewer/scripts/check_brand.py'
spec = importlib.util.spec_from_file_location('check_brand', SCRIPT)
brand = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand)


@unittest.skipIf(Image is None, 'Pillow required for actual pixel tests')
class BrandChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.logo = Image.new('RGB', (100, 80), '#772432')
        self.logo.save(self.root / 'logo.png')
        self.canvas = Image.new('RGB', (300, 400), 'white')
        self.canvas.paste('#004165', (0, 0, 300, 100))
        self.canvas.paste(self.logo, (100, 250))
        self.candidate = self.root / '候选 poster.png'
        self.spec = {
            'format': 'tm-poster-brand-check/v1', 'rule_set': brand.RULE_SET,
            'target_width_px': 300,
            'color_regions': [{'bounds': [0, 0, 300, 100], 'color': '#004165'}],
            'logos': [{'source': 'logo.png', 'source_sha256': brand.digest(self.root / 'logo.png'),
                       'kind': 'ti', 'bounds': [100, 250, 100, 80], 'background': '#FFFFFF',
                       'source_wordmark_height_px': 10}],
        }

    def check(self):
        self.canvas.save(self.candidate)
        return brand.inspect(self.candidate, self.spec, self.root)

    def test_valid_pixels_pass_only_scoped_checks(self):
        result = self.check()
        self.assertEqual(result['scoped_verdict'], 'PASS')
        self.assertEqual(result['full_brand_verdict'], 'NOT_ASSESSED')

    def test_single_stray_pixel_fails_palette(self):
        self.canvas.putpixel((299, 99), (255, 0, 255))
        result = self.check()
        self.assertEqual(result['scoped_verdict'], 'REVISE')
        self.assertEqual(result['findings'][0]['out_of_tolerance_pixels'], 1)

    def test_photos_outside_regions_are_not_palette_failures(self):
        self.canvas.putpixel((20, 180), (255, 128, 0))
        self.assertEqual(self.check()['scoped_verdict'], 'PASS')

    def test_gradient_endpoints_and_pixel_colors(self):
        self.spec['color_regions'][0].update(mode='gradient', colors=['#004165', '#006094'])
        self.assertEqual(self.check()['scoped_verdict'], 'PASS')
        self.spec['color_regions'][0]['colors'][1] = '#FF9900'
        self.assertEqual(self.check()['scoped_verdict'], 'REVISE')

    def test_logo_recoloring_blocks_exact_source_match(self):
        self.canvas.putpixel((120, 270), (0, 0, 0))
        self.assertEqual(self.check()['scoped_verdict'], 'BLOCKED')

    def test_wrong_aspect_ratio_is_reported(self):
        self.spec['logos'][0]['bounds'][3] = 60
        result = self.check()
        finding = next(f for f in result['findings'] if f['check'] == 'B02 proportions')
        self.assertEqual(finding['status'], 'REVISE')

    def test_mobile_and_print_minimum_sizes(self):
        for target, expected in ((216, 'PASS'), (215, 'REVISE')):
            self.spec['target_width_px'] = target
            self.assertEqual(self.check()['scoped_verdict'], expected)
        self.spec['target_width_px'] = 300
        self.spec['print_width_in'] = 2
        self.assertEqual(self.check()['scoped_verdict'], 'REVISE')

    def test_missing_source_hash_or_measurement_blocks(self):
        self.spec['logos'][0]['source_sha256'] = 'incorrect'
        self.assertEqual(self.check()['scoped_verdict'], 'BLOCKED')

        self.spec['logos'][0]['source_sha256'] = brand.digest(self.root / 'logo.png')
        del self.spec['logos'][0]['source_wordmark_height_px']
        self.assertEqual(self.check()['scoped_verdict'], 'BLOCKED')

    def test_clear_space_edge_and_nonuniform_background(self):
        self.canvas.putpixel((99, 250), (0, 0, 0))
        self.assertEqual(self.check()['scoped_verdict'], 'BLOCKED')
        self.spec['logos'][0]['bounds'][0] = 0
        finding = next(f for f in self.check()['findings'] if f['check'] == 'B03 clear space')
        self.assertEqual(finding['status'], 'REVISE')

    def test_invalid_bounds_rejected(self):
        self.spec['color_regions'][0]['bounds'][2] = 301
        with self.assertRaises(ValueError):
            self.check()

    def test_cli_pass_and_bad_input(self):
        self.check()
        config = self.root / 'spec.json'
        for data, expected in ((self.spec, 0), ({}, 2)):
            config.write_text(json.dumps(data), encoding='utf-8')
            result = subprocess.run([sys.executable, str(SCRIPT), '--candidate', str(self.candidate), '--spec', str(config)], capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertIn('scoped_verdict', json.loads(result.stdout))


@unittest.skipIf(Image is None, 'Pillow required for actual pixel tests')
class ExtendedBrandChecks(BrandChecks):
    def setUp(self):
        super().setUp()
        self.spec.update(format='tm-poster-brand-check/v2', context='ordinary-club',
                         inventory_complete=True, document_kind='poster',
                         color_formulations=[],
                         exclusions=[dict(bounds=[0,100,300,300],kind='neutral',reason='White synthetic fixture background, logo region inventoried separately')],
                         layers=[dict(id='logo',kind='logo',bounds=[100,250,100,80])],
                         faces=[],text_runs=[],contrast_pairs=[],
                         identity=dict(custom_logo=False,custom_theme=False,custom_tagline=False))
        self.spec['logos'][0].update(variant='full-color',layer_id='logo',effects=[],
                                    provenance='Synthetic unit-test source, not an official asset',
                                    transform=dict(rotation_deg=0,skew_x_deg=0,skew_y_deg=0,perspective=False))

    def check(self):
        self.canvas.save(self.candidate)
        self.spec['candidate_sha256'] = brand.digest(self.candidate)
        return brand.inspect(self.candidate,self.spec,self.root)

    def findings(self,check):
        return [f for f in self.check()['findings'] if f['check']==check]

    def run_text(self,**changes):
        run=dict(text='Headline',bounds=[10,120,150,20],role='headline',
                 font_family='Montserrat',script='latin',effects=[],render_evidence='Synthetic renderer fixture declaration')
        run.update(changes)
        self.spec['text_runs']=[run]
        return run

    # Old-schema-specific assertions are overridden; shared pixel cases also run in v2.
    def test_wrong_aspect_ratio_is_reported(self):
        self.spec['logos'][0]['bounds'][3]=60
        self.assertEqual(self.findings('logo_proportions')[0]['status'],'REVISE')

    def test_clear_space_edge_and_nonuniform_background(self):
        self.canvas.putpixel((99,250),(0,0,0))
        self.assertIn('BLOCKED',[f['status'] for f in self.findings('logo_clear_space')])
        self.spec['logos'][0]['bounds'][0]=0
        self.assertIn('REVISE',[f['status'] for f in self.findings('logo_clear_space')])

    def test_gradient_endpoints_and_pixel_colors(self):
        self.spec['color_regions'][0].update(mode='gradient',colors=['#004165','#006094'],geometry='horizontal')
        for x in range(300):
            color=tuple(round(a+(b-a)*x/299) for a,b in zip((0,65,101),(0,96,148)))
            self.canvas.paste(color,(x,0,x+1,100))
        self.assertEqual(self.check()['scoped_verdict'],'PASS')
        self.canvas.putpixel((150,50),(0,65,101))
        self.assertEqual(self.findings('gradient')[0]['status'],'REVISE')
        self.spec['color_regions'][0]['colors'][1]='#FF9900'
        self.assertEqual(self.findings('gradient')[0]['status'],'REVISE')

    def test_missing_inventory_and_candidate_binding(self):
        self.spec['inventory_complete']=False
        self.assertEqual(self.check()['scoped_verdict'],'BLOCKED')
        self.spec['inventory_complete']=True
        self.check()
        self.spec['candidate_sha256']='wrong'
        self.assertEqual(brand.inspect(self.candidate,self.spec,self.root)['scoped_verdict'],'BLOCKED')

    def test_coverage_detects_unchecked_strip(self):
        self.spec['color_regions'][0]['bounds'][2]=299
        self.assertEqual(self.findings('color_coverage')[0]['unclassified_pixels'],100)
        self.assertEqual(self.findings('color_coverage')[0]['status'],'BLOCKED')

    def test_pathways_badge_does_not_invent_primary_logo_numeric_rules(self):
        self.spec['logos'][0].update(kind='pathways-badge',variant='official')
        self.spec['logos'][0].pop('source_wordmark_height_px')
        self.spec['target_width_px']=None
        self.assertEqual(self.findings('logo_size')[0]['status'],'INFO')
        self.assertEqual(self.findings('logo_clear_space')[0]['status'],'INFO')

    def test_rgb_cmyk_pantone_formulations(self):
        self.spec['color_formulations']=[dict(hex='#004165',rgb=[0,65,101],cmyk=[100,43,12,56],pantone='302')]
        self.assertTrue(all(f['status']=='PASS' for f in self.findings('color_formulations')))
        self.spec['color_formulations'][0]['cmyk']=[100,40,12,56]
        self.assertIn('REVISE',[f['status'] for f in self.findings('color_formulations')])

    def test_gray_opacity_increments(self):
        self.spec['color_regions'][0].update(mode='gradient',colors=['#A9B2B1','#F5F5F5'],geometry='vertical',opacity=.3,background='#FFFFFF')
        self.assertEqual(self.findings('gray_opacity')[0]['status'],'REVISE')
        self.spec['color_regions'][0]['opacity']=.4
        self.assertEqual(self.findings('gray_opacity')[0]['status'],'PASS')

    def test_radial_geometry_and_overlay(self):
        region=self.spec['color_regions'][0]
        region.update(mode='gradient',colors=['#004165','#006094'],geometry='radial',center=[150,50],radii=[150,50],overlay=dict(color='#FFFFFF',opacity=.5))
        import math
        for y in range(100):
            for x in range(300):
                t=min(1,math.hypot((x-150)/150,(y-50)/50))
                base=[round(a+(b-a)*t) for a,b in zip((0,65,101),(0,96,148))]
                self.canvas.putpixel((x,y),tuple(round(v*.5+255*.5) for v in base))
        self.assertEqual(self.findings('gradient')[0]['status'],'PASS')
        # 50% is not rejected because the manual's 70% transparency is an example.
        self.assertEqual(self.findings('transparency')[0]['status'],'PASS')

    def test_logo_minimum_without_source(self):
        self.spec['logos'][0].pop('source')
        self.spec['target_width_px']=150
        self.assertEqual(self.findings('logo_size')[0]['status'],'REVISE')
        self.assertIn('BLOCKED',[f['status'] for f in self.findings('logo_source')])

    def test_source_variants_and_transform(self):
        self.spec['logos'][0]['variant']='purple'
        self.assertEqual(self.findings('logo_source')[0]['status'],'REVISE')
        self.spec['logos'][0]['transform']['perspective']=True
        self.assertEqual(self.findings('logo_transform')[0]['status'],'REVISE')

    def test_bounding_overlap_is_uncertain_not_automatic_violation(self):
        self.spec['faces']=[dict(bounds=[110,260,20,20])]
        self.assertEqual(self.findings('face_overlap')[0]['status'],'BLOCKED')
        self.spec['layers'].append(dict(id='copy',kind='text',bounds=[100,250,10,10]))
        self.assertEqual(self.findings('logo_overlap')[0]['status'],'BLOCKED')

    def test_metadata_rectangle_cannot_invent_actual_coverage(self):
        # The poster remains unchanged. This alleged text box covers only
        # original, uniform maroon logo pixels, not a real overlay.
        self.spec['layers'].append(dict(id='unverified-box',kind='text',bounds=[110,260,20,20]))
        statuses=[f['status'] for f in self.findings('logo_overlap')]
        self.assertNotIn('REVISE',statuses)
        self.assertIn('BLOCKED',statuses)

    def test_photo_label_does_not_override_actual_opaque_ink_evidence(self):
        self.spec['layers'].append(dict(id='alleged-underlay',kind='photo',bounds=[180,260,40,40]))
        unchanged=[f['status'] for f in self.findings('logo_overlap')]
        self.assertNotIn('REVISE',unchanged)
        self.canvas.paste('#F2DF74',(180,260,220,300))
        changed=[f['status'] for f in self.findings('logo_overlap')]
        self.assertIn('REVISE',changed)

    def test_fonts_roles_effects_and_chinese_fallback(self):
        run=self.run_text(font_family='Arial')
        self.assertEqual(self.findings('font_family')[0]['declared_status'],'REVISE')
        self.assertEqual(self.findings('font_family')[0]['status'],'BLOCKED')
        run.update(font_role='body')
        self.assertEqual(self.findings('font_family')[0]['declared_status'],'PASS')
        self.assertEqual(self.findings('font_family')[0]['status'],'BLOCKED')
        run['effects']=['drop-shadow']
        self.assertEqual(self.findings('font_effects')[0]['declared_status'],'REVISE')
        self.assertEqual(self.findings('font_effects')[0]['status'],'BLOCKED')
        run.update(script='han',font_family='Chinese fallback')
        self.assertEqual(self.findings('font_family')[0]['status'],'INFO')

    def test_font_file_name_and_hash(self):
        try:
            from fontTools.ttLib import TTFont,newTable
        except ImportError:
            self.skipTest('fontTools optional for font-file identity')
        font=TTFont()
        table=newTable('name');table.names=[]
        table.setName('Wrong Family',1,3,1,0x409)
        font['name']=table
        font.save(self.root/'synthetic.ttf')
        self.run_text(font_file='synthetic.ttf',font_sha256=brand.digest(self.root/'synthetic.ttf'))
        self.assertIn('REVISE',[f.get('declared_status') for f in self.findings('font_family')])
        self.assertTrue(all(f['status']=='BLOCKED' for f in self.findings('font_family')))

    def test_tagline_exact_case_and_phrase_count(self):
        run=self.run_text(role='tagline',font_role='body',font_family='Arial',text='where leaders are made')
        self.assertEqual(self.findings('tagline')[0]['declared_status'],'REVISE')
        self.assertEqual(self.findings('tagline')[0]['status'],'BLOCKED')
        run['text']='Where Leaders Are Made'
        self.assertEqual(self.findings('tagline')[0]['declared_status'],'PASS')
        self.assertEqual(self.findings('tagline')[0]['status'],'BLOCKED')
        run.update(role='marketing-phrase',text='Find Your Voice')
        self.spec['text_runs'].append(dict(run,text='Invest in a Brighter Future'))
        self.assertIn('REVISE',[f.get('declared_status') for f in self.findings('marketing_phrases')])
        self.assertTrue(all(f['status']=='BLOCKED' for f in self.findings('marketing_phrases')))

    def test_identity_and_gavel_rules(self):
        self.spec['identity']['custom_logo']=True
        self.assertIn('REVISE',[f.get('declared_status') for f in self.findings('identity')])
        self.assertIn('BLOCKED',[f['status'] for f in self.findings('identity')])
        self.spec.update(context='gavel-club')
        self.assertIn('REVISE',[f['status'] for f in self.findings('gavel_identity')])

    def test_corporate_top_bottom_and_ambiguous_same_row(self):
        self.spec['context']='corporate-club'
        other=dict(kind='corporate',bounds=[100,150,50,30])
        self.spec['logos'].append(other)
        self.assertEqual(self.findings('corporate_placement')[0]['status'],'PASS')
        other['bounds']=[220,250,50,30]
        self.assertEqual(self.findings('corporate_placement')[0]['status'],'BLOCKED')

    def test_conference_eligibility_expiry_text_and_sponsors(self):
        self.spec.update(context='annual-district-conference',as_of_date='2026-04-01',
                         conference=dict(date='2026-04-20',district_number=85,annual=True),
                         sponsor_sections=[])
        self.run_text(text='District 85 Annual Conference')
        self.assertEqual(self.findings('conference')[0]['status'],'PASS')
        self.assertIn('BLOCKED',[f['status'] for f in self.findings('conference')])
        self.spec['conference']['date']='2026-10-24'
        self.assertEqual(self.findings('conference')[0]['status'],'REVISE')
        self.spec['conference']['date']='2026-04-20'
        self.spec['as_of_date']='2026-04-21'
        self.assertIn('REVISE',[f['status'] for f in self.findings('conference')])
        self.spec['logos'].append(dict(kind='sponsor',bounds=[10,180,50,20]))
        self.assertEqual(self.findings('sponsor_placement')[0]['status'],'REVISE')

    def test_contrast_and_dominance_no_invented_threshold(self):
        self.spec['contrast_pairs']=[dict(foreground='#FFFFFF',background='#000000')]
        self.assertEqual(self.findings('contrast')[0]['ratio'],21)
        self.assertEqual(self.findings('contrast')[0]['status'],'INFO')
        self.assertEqual(self.findings('color_dominance')[0]['status'],'INFO')

    def test_jpeg_mismatch_is_not_definitive_color_violation(self):
        self.check()
        self.canvas.save(self.root/'photo.jpg',quality=80)
        candidate=self.root/'photo.jpg'
        self.spec['candidate_sha256']=brand.digest(candidate)
        result=brand.inspect(candidate,self.spec,self.root)
        palette=[f for f in result['findings'] if f['check']=='palette']
        self.assertEqual(palette[0]['status'],'BLOCKED')


    def test_wordmark_black_variant_and_invalid_grayscale(self):
        logo=self.spec['logos'][0]
        logo.update(kind='wordmark',variant='black')
        self.assertEqual(self.findings('logo_source')[0]['status'],'PASS')
        logo['variant']='grayscale'
        self.assertEqual(self.findings('logo_source')[0]['status'],'REVISE')

    def test_source_crop_cannot_hide_logo_elements(self):
        self.spec['logos'][0]['source_bounds']=[10,0,90,80]
        self.assertIn('BLOCKED',[f['status'] for f in self.findings('logo_source')])

    def test_effect_and_translation_missing_evidence(self):
        run=self.run_text(role='tagline',font_role='body',font_family='Arial',text='Translated slogan',language='zh')
        self.assertEqual(self.findings('tagline')[0]['status'],'BLOCKED')
        del run['render_evidence']
        self.assertIn('BLOCKED',[f['status'] for f in self.findings('font_family')])

    def test_missing_geometry_does_not_invent_violation(self):
        self.spec['color_regions'][0].update(mode='gradient',colors=['#004165','#006094'],geometry='diagonal')
        self.assertEqual(self.findings('gradient')[0]['status'],'BLOCKED')

    def test_linear_diagonal_recipe_is_measured_without_invented_angle_ban(self):
        region=self.spec['color_regions'][0]
        region.update(mode='gradient',colors=['#004165','#006094'],geometry='diagonal',tolerance=1)
        for y in range(100):
            for x in range(300):
                t=(x/299+y/99)/2
                self.canvas.putpixel((x,y),tuple(round(a+(b-a)*t) for a,b in zip((0,65,101),(0,96,148))))
        self.assertEqual(self.findings('gradient')[0]['status'],'PASS')

    def test_era_claim_is_not_an_observed_logo_violation(self):
        self.spec['logos'][0]['era']='pre-2011'
        findings=self.findings('logo_source')
        self.assertNotIn('REVISE',[f['status'] for f in findings])
        self.assertIn('BLOCKED',[f['status'] for f in findings])
        self.assertIn('REVISE',[f.get('declared_status') for f in findings])

    def test_template_and_registry_cli(self):
        for flag in ('--template','--rules'):
            result=subprocess.run([sys.executable,str(SCRIPT),flag],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['rule_set'],brand.RULE_SET)

    def test_logo_patterned_glow(self):
        self.spec['logos'][0]['effects']=['patterned-glow']
        self.assertEqual(self.findings('logo_effects')[0]['declared_status'],'REVISE')
        self.assertEqual(self.findings('logo_effects')[0]['status'],'BLOCKED')


@unittest.skipIf(Image is None, 'Pillow required')
class LogoVisualComparison(unittest.TestCase):
    def setUp(self):
        from PIL import ImageDraw
        self.source = Image.new('RGBA', (240,180), (255,255,255,0))
        draw = ImageDraw.Draw(self.source)
        draw.ellipse((15,10,225,170), fill='#004165', outline='#772432', width=7)
        for x in (60,100,140,180):
            draw.line((x,25,x,155), fill='white', width=3)
        draw.rectangle((5,65,235,115), fill='white', outline='#772432', width=3)
        draw.text((35,82),'SYNTHETIC LOGO',fill='#004165')
        self.render = Image.new('RGBA',(160,120),'white')
        self.render.alpha_composite(self.source.resize((160,120),Image.Resampling.LANCZOS))
        self.render = self.render.convert('RGB')

    def check(self,image):
        return brand.compare_logo(self.source,image,(255,255,255))

    def test_jpeg_and_resizing_are_accepted(self):
        import io
        for quality in (95,85,70,55,40):
            with self.subTest(quality=quality):
                buf=io.BytesIO();self.render.save(buf,format='JPEG',quality=quality)
                buf.seek(0)
                self.assertEqual(self.check(Image.open(buf))['status'],'PASS')

    def test_different_resampler_is_accepted(self):
        rendered=Image.new('RGBA',(160,120),'white')
        rendered.alpha_composite(self.source.resize((160,120),Image.Resampling.BILINEAR))
        self.assertEqual(self.check(rendered)['status'],'PASS')

    def test_unlisted_jpeg_quality_and_whole_poster_block_phase(self):
        import io
        canvas=Image.new('RGB',(300,230),'white')
        canvas.paste(self.render,(57,49))
        data=io.BytesIO();canvas.save(data,format='JPEG',quality=63)
        data.seek(0)
        with Image.open(data) as image:
            observed=image.crop((57,49,217,169))
        result=brand.compare_logo(self.source,observed,(255,255,255),(57,49))
        self.assertEqual(result['status'],'PASS',result)

    def test_recoloring_not_accepted(self):
        from PIL import ImageOps
        changed=ImageOps.colorize(self.render.convert('L'),'#FF00FF','white')
        self.assertNotEqual(self.check(changed)['status'],'PASS')

    def test_removed_elements_not_accepted(self):
        changed=self.render.copy();changed.paste('white',(0,40,160,80))
        self.assertEqual(self.check(changed)['status'],'BLOCKED')

    def test_stretching_not_accepted(self):
        changed=Image.new('RGB',(160,120),'white')
        changed.paste(self.render.resize((120,120)),(20,0))
        self.assertEqual(self.check(changed)['status'],'BLOCKED')

    def test_low_resolution_not_certified_by_similarity(self):
        small=self.render.resize((30,23))
        self.assertEqual(self.check(small)['status'],'BLOCKED')

    def test_invisible_exact_render_is_not_visual_logo_evidence(self):
        original=Image.new('RGBA',(240,180),(255,255,255,0))
        from PIL import ImageDraw
        ImageDraw.Draw(original).ellipse((20,20,220,160),outline='white',width=10)
        blank=Image.new('RGB',(160,120),'white')
        result=brand.compare_logo(original,blank,(255,255,255))
        self.assertEqual(result['status'],'BLOCKED')

    def test_whole_poster_jpeg_chroma_modes_use_actual_quantization(self):
        import io
        from PIL import JpegImagePlugin
        for subsampling in (0,1,2):
            with self.subTest(subsampling=subsampling):
                canvas=Image.new('RGB',(300,230),'white');canvas.paste(self.render,(57,49))
                data=io.BytesIO();canvas.save(data,format='JPEG',quality=63,subsampling=subsampling)
                data.seek(0)
                with Image.open(data) as decoded:
                    settings=dict(qtables=decoded.quantization,subsampling=JpegImagePlugin.get_sampling(decoded))
                    observed=decoded.crop((57,49,217,169))
                result=brand.compare_logo(self.source,observed,(255,255,255),(57,49),settings)
                self.assertEqual(result['status'],'PASS',result)

    def test_alpha_only_white_outline_keeps_compressed_shape_evidence(self):
        import io
        from PIL import ImageDraw
        original=Image.new('RGBA',(240,180),(255,255,255,0))
        draw=ImageDraw.Draw(original)
        draw.ellipse((15,10,225,170),outline='white',width=8)
        draw.line((20,70,220,70),fill='white',width=6)
        rendered=Image.new('RGBA',(160,120),'#004165')
        rendered.alpha_composite(original.resize((160,120),Image.Resampling.LANCZOS))
        data=io.BytesIO();rendered.convert('RGB').save(data,format='JPEG',quality=63)
        data.seek(0)
        result=brand.compare_logo(original,Image.open(data),(0,65,101))
        self.assertEqual(result['status'],'PASS',result)


if __name__ == '__main__':
    unittest.main()
