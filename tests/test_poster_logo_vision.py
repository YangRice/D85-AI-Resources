"""Actual synthetic image tests for optional logo vision; no official assets."""
import importlib.util
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    cv2 = None

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('logo_vision',ROOT/'skills/toastmasters-poster-reviewer/scripts/logo_vision.py')
vision=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(vision)


@unittest.skipIf(cv2 is None,'Optional OpenCV required')
class LogoVision(unittest.TestCase):
    def setUp(self):
        self.logo=Image.new('RGBA',(260,200),(0,0,0,0))
        d=ImageDraw.Draw(self.logo)
        d.ellipse((31,1,229,199),fill='#004165',outline='#F2DF74',width=4)
        for x in (68,98,130,160,192):d.arc((x//2,7,260-x//2,192),0,360,fill='white',width=2)
        for y in (30,60,140,170):d.line((42,y,218,y),fill='#A9B2B1',width=2)
        d.rectangle((1,75,258,125),fill='white',outline='#772432',width=3)
        f=ImageFont.load_default(size=24)
        d.text((12,81),'REFERENCE 17',font=f,fill='#004165')
        # Nonrepeating fine detail supports SIFT/RANSAC coverage checks.
        for i,(x,y) in enumerate(((52,42),(91,31),(155,49),(201,62),(63,152),(171,165))):
            d.text((x,y),str(i),font=ImageFont.load_default(size=13),fill='white')
        self.poster=Image.new('RGB',(600,700),'#004165')
        self.poster.paste(self.logo,(110,130),self.logo)
        self.observation=dict(bounds=[110,130,260,200],wordmark_height_ratio=.19,
            background='#004165',target_width_px=600,foreground_regions=[],foreground_complete=True)

    def check(self,poster=None):
        return vision.inspect_logo(poster or self.poster,self.logo,self.observation)

    def test_actual_reference_geometry_and_appearance_pass(self):
        result=self.check()
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['geometry']['status'],'PASS',result)
        self.assertEqual(result['appearance']['status'],'PASS',result)
        self.assertEqual(result['size']['status'],'PASS',result)
        self.assertEqual(result['clear_space']['status'],'PASS',result)

    def test_compressed_reference_is_not_recoloring(self):
        buffer=io.BytesIO();self.poster.save(buffer,format='JPEG',quality=65)
        result=self.check(Image.open(io.BytesIO(buffer.getvalue())))
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['geometry']['status'],'PASS',result)
        self.assertNotEqual(result['appearance']['status'],'REVISE',result)

    def test_matching_later_variant_is_selected_and_local_edit_still_fails(self):
        # Synthetic artwork only: the first reference has the same shape but a
        # different fill. Selecting only that variant used to reject a valid
        # poster without ever testing the matching official variant.
        route_spec=importlib.util.spec_from_file_location('variant_route',
            ROOT/'skills/toastmasters-poster-reviewer/scripts/vision_review.py')
        route=importlib.util.module_from_spec(route_spec);route_spec.loader.exec_module(route)
        wrong=np.array(self.logo)
        blue=(wrong[:,:,2]>60)&(wrong[:,:,0]<40)&(wrong[:,:,1]<100)
        wrong[blue,:3]=(180,20,180)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            first=root/'FirstColorVariant.png';Image.fromarray(wrong).save(first)
            correct=root/'Matching3ColorVariant.png';self.logo.save(correct)
            candidate=root/'poster.jpg'
            self.poster.save(candidate,quality=80)
            logo=dict(self.observation,id='primary',references=[str(first)])
            spec=dict(format=route.FORMAT,rule_set=route.RULES['rule_set'],
                candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
                requested_checks=['logo_detection','logo_geometry','logo_appearance'],logos=[logo])
            with Image.open(candidate) as image:
                initial=route.inspect(image.convert('RGB'),spec,root,candidate)
                self.assertNotEqual(initial['feature_results']['logo_appearance']['status'],'PASS')
                for references in ([str(first),str(correct)], [str(correct),str(first)]):
                    logo['references']=references
                    result=route.inspect(image.convert('RGB'),spec,root,candidate)
                    self.assertEqual(result['scoped_verdict'],'PASS',result)
                    measured=result['logo_measurements'][0]
                    self.assertEqual(measured['selected']['reference_name'],correct.name)
                    self.assertEqual(len(measured['hypotheses']),2)
            altered=self.poster.copy()
            ImageDraw.Draw(altered).rectangle((115,210,165,240),fill='#00FF00')
            altered.save(candidate,quality=80)
            spec['candidate_sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
            with Image.open(candidate) as image:
                result=route.inspect(image.convert('RGB'),spec,root,candidate)
            self.assertEqual(result['feature_results']['logo_appearance']['status'],'REVISE',result)

    def test_transparent_interior_prevents_sparse_outline_recolor_bypass(self):
        # White outline ink stays identical while a filled interior is changed.
        # Opaque-only comparisons cannot see that altered interior at all.
        sparse=np.array(self.logo)
        blue=(sparse[:,:,0]<40)&(sparse[:,:,1]<100)&(sparse[:,:,2]>60)
        sparse[blue,3]=0
        sparse[:,:,:3]=255
        outline=Image.fromarray(sparse)
        poster=Image.new('RGB',self.poster.size,'#004165')
        poster.paste(outline,(110,130),outline)
        control=vision.inspect_logo(poster,outline,self.observation)
        self.assertEqual(control['detection']['status'],'PASS',control)
        self.assertEqual(control['appearance']['status'],'PASS',control)
        self.assertEqual(control['appearance']['negative_space']['status'],'PASS',control)

        changed=poster.copy()
        ImageDraw.Draw(changed).ellipse((145,135,335,325),fill='#B400B4')
        changed.paste(outline,(110,130),outline)
        result=vision.inspect_logo(changed,outline,self.observation)
        self.assertEqual(result['detection']['status'],'PASS',result)
        # The exterior alone cannot rule out a permitted photo in the holes.
        self.assertEqual(result['appearance']['status'],'BLOCKED',result)
        self.assertTrue(result['appearance']['negative_space']['material_components'],result)
        self.observation['background_uniform_across_logo']=True
        result=vision.inspect_logo(changed,outline,self.observation)
        self.assertEqual(result['appearance']['status'],'REVISE',result)
        self.observation['background']='#FFFFFF'
        result=vision.inspect_logo(changed,outline,self.observation)
        self.assertEqual(result['appearance']['status'],'BLOCKED',result)

    def test_white_logo_on_nonuniform_photo_is_uncertain_not_extra_ink(self):
        sparse=np.array(self.logo)
        blue=(sparse[:,:,0]<40)&(sparse[:,:,1]<100)&(sparse[:,:,2]>60)
        sparse[blue,3]=0
        sparse[:,:,:3]=255
        outline=Image.fromarray(sparse)
        # A varied, smooth background is permitted. Without its separate layer
        # the transparent holes must remain uncertain rather than prohibited.
        y,x=np.indices((700,600))
        pixels=np.stack((x*255//599,y*255//699,np.full_like(x,80)),axis=2).astype(np.uint8)
        poster=Image.fromarray(pixels)
        poster.paste(outline,(110,130),outline)
        result=vision.inspect_logo(poster,outline,self.observation)
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['appearance']['negative_space']['status'],'BLOCKED',result)
        self.assertEqual(result['appearance']['status'],'BLOCKED',result)

    def test_stretch_is_reported_before_rectification(self):
        stretched=self.logo.resize((325,200))
        self.poster.paste('#004165',(0,0,600,700));self.poster.paste(stretched,(100,130),stretched)
        self.observation['bounds']=[100,130,325,200]
        result=self.check()
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['geometry']['status'],'REVISE',result)

    def test_projective_distortion_is_not_hidden_by_alignment(self):
        src=np.float32([[0,0],[260,0],[260,200],[0,200]])
        dst=np.float32([[110,130],[400,155],[355,315],[160,355]])
        matrix=cv2.getPerspectiveTransform(src,dst)
        art=cv2.warpPerspective(np.array(self.logo),matrix,(600,700))
        rgba=Image.fromarray(art,'RGBA')
        self.poster=Image.new('RGB',(600,700),'#004165');self.poster.paste(rgba,(0,0),rgba)
        self.observation['bounds']=[100,120,320,250]
        result=self.check()
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['geometry']['status'],'REVISE',result)

    def test_recoloring_is_not_accepted_from_shape(self):
        changed=np.array(self.logo)
        mask=(changed[:,:,2]>60)&(changed[:,:,0]<40)&(changed[:,:,1]<100)
        changed[mask,:3]=(180,20,180)
        art=Image.fromarray(changed,'RGBA')
        self.poster.paste('#004165',(0,0,600,700));self.poster.paste(art,(110,130),art)
        result=self.check()
        self.assertNotEqual(result['appearance']['status'],'PASS',result)

    def test_local_recolor_cannot_hide_in_whole_logo_average(self):
        # Small local patches span much less than the global changed-area gate.
        for box in ((115,210,165,240),(160,215,205,245),(220,210,250,245)):
            with self.subTest(box=box):
                actual=self.poster.copy()
                ImageDraw.Draw(actual).rectangle(box,fill='#FF00FF')
                result=self.check(actual)
                self.assertEqual(result['detection']['status'],'PASS',result)
                self.assertEqual(result['appearance']['status'],'REVISE',result)
                self.assertTrue(result['appearance']['localized_change'],result)

    def test_removed_artwork_component_cannot_hide_in_global_average(self):
        # Erase a portion of the white wordmark bar with its blue background.
        actual=self.poster.copy()
        ImageDraw.Draw(actual).rectangle((115,210,165,240),fill='#004165')
        result=self.check(actual)
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['appearance']['status'],'REVISE',result)
        self.assertTrue(result['appearance']['localized_change'],result)

    def test_near_edge_clear_space_defect(self):
        self.poster.paste('#004165',(0,0,600,700));self.poster.paste(self.logo,(12,130),self.logo)
        self.observation['bounds']=[12,130,260,200]
        result=self.check()
        self.assertEqual(result['clear_space']['status'],'REVISE',result)

    def test_blank_image_cannot_match(self):
        result=self.check(Image.new('RGB',(600,700),'#004165'))
        self.assertEqual(result['detection']['status'],'BLOCKED',result)

    def test_actual_shadow_ink_is_detected_outside_artwork(self):
        silhouette=Image.new('RGBA',self.logo.size,(0,0,0,255))
        self.poster.paste(silhouette,(117,137),self.logo)
        self.poster.paste(self.logo,(110,130),self.logo)
        result=self.check()
        self.assertEqual(result['detection']['status'],'PASS',result)
        self.assertEqual(result['effects']['status'],'REVISE',result)

    def test_foreground_box_whitespace_does_not_create_intrusion(self):
        # Box overlaps the left clear-space ring but ink is outside the ring.
        ImageDraw.Draw(self.poster).rectangle((25,155,35,165),fill='white')
        self.observation['foreground_regions']=[[20,150,60,20]]
        result=self.check()
        self.assertEqual(result['clear_space']['status'],'PASS',result)

    def test_foreground_ink_inside_ring_is_a_defect(self):
        ImageDraw.Draw(self.poster).rectangle((80,155,90,165),fill='white')
        self.observation['foreground_regions']=[[75,150,30,20]]
        result=self.check()
        self.assertEqual(result['clear_space']['status'],'REVISE',result)

    def test_texture_without_completed_foreground_inventory_is_uncertain(self):
        self.observation.pop('background');self.observation.pop('foreground_complete')
        result=self.check()
        self.assertEqual(result['clear_space']['status'],'BLOCKED',result)
        self.assertEqual(result['effects']['status'],'INFO',result)

    def test_missing_physical_scale_does_not_invent_size(self):
        self.observation.pop('target_width_px')
        result=self.check()
        self.assertEqual(result['size']['status'],'BLOCKED')

    def test_invalid_hint_does_not_escape_image(self):
        self.observation['bounds']=[590,690,100,100]
        with self.assertRaises(ValueError):self.check()


if __name__=='__main__':unittest.main()
