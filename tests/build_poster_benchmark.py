"""Build private, source-backed poster benchmark rounds from official web assets.

No copyrighted assets are bundled. Supply downloaded sources in --assets; all
generated posters and source evidence stay in --output. Never publish these
private original/derived official assets as repository MIT material.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def extract(assets, archive, member, name):
    path=assets/name
    with zipfile.ZipFile(assets/archive) as z:
        path.write_bytes(z.read(member))
    return path


def build(assets, output, revision=3):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a fresh output directory; frozen benchmark artifacts must not be overwritten')
    output.mkdir(parents=True,exist_ok=True)
    sources={
        'ti':extract(assets,'logo.zip','ToastmastersLogo/Color/ToastmastersLogoColor.png','ti.png'),
        'gavel':extract(assets,'gavel.zip','GavelClubLogo/LoyalBlue/GavelClubLogoLoyalBlue-RGB.png','gavel.png'),
        'pathways':extract(assets,'pathways.zip','PathwaysLogo/Color/PathwaysTypeTreatmentColor-RGB.png','pathways.png'),
        'badge':extract(assets,'badges.zip','PathwaysBadge/Pathways/pathways-badge-presentation-mastery.png','badge.png'),
        'wordmark':extract(assets,'wordmark.zip','ToastmastersWordmark/Black/ToastmastersWordmarkBlack.png','wordmark.png'),
    }
    urls={
        'ti':'https://ccdn.toastmasters.org/content/toastmasters-logo.zip',
        'gavel':'https://ccdn.toastmasters.org/content/gavel-club-logo.zip',
        'pathways':'https://ccdn.toastmasters.org/content/pathways-logo.zip',
        'badge':'https://ccdn.toastmasters.org/content/pathways-badge.zip',
        'wordmark':'https://ccdn.toastmasters.org/content/toastmasters-wordmark.zip',
    }
    # Neutral IDs/order prevent the independent reviewer from inheriting labels.
    scenarios={
        1:[('a17','base'),('b42','small'),('c08','corporate'),('d31','purple'),
           ('e56','gray'),('f23','shadow'),('g64','gavel'),('h05','recolor'),
           ('i90','conference'),('j12','fall')],
        2:[('k38','pathways'),('l61','fakefont'),('m09','jpeg'),('n74','phrases'),
           ('o25','radial'),('p46','legacy'),('q83','ornate'),('r11','faces'),
           ('s57','wordmark'),('t69','missing')],
    }
    intended_positive={'base','corporate','gray','gavel','conference','pathways','jpeg','radial','ornate','wordmark'}
    targets={
        'base':['palette','color_formulations','logo_source','logo_size','logo_proportions','logo_transform','logo_effects','logo_clear_space','font_family','font_effects','tagline','marketing_phrases'],
        'small':['logo_size','logo_proportions'],
        'corporate':['corporate_placement','logo_source','color_coverage'],
        'purple':['palette','gradient','color_formulations'],
        'gray':['gray_opacity','gradient','transparency','contrast','color_dominance'],
        'shadow':['font_effects','font_family','tagline'],
        'gavel':['gavel_identity','identity','logo_source'],
        'recolor':['logo_source','logo_proportions','logo_clear_space','logo_overlap'],
        'conference':['conference','sponsor_placement','identity'],
        'fall':['conference','sponsor_placement'],
        'pathways':['logo_size','logo_clear_space','badge_relevance','logo_source'],
        'fakefont':['font_family','font_effects'],
        'jpeg':['logo_source','logo_proportions','logo_size'],
        'phrases':['tagline','marketing_phrases'],
        'radial':['gradient','palette','color_coverage'],
        'legacy':['logo_source','logo_effects','identity'],
        'ornate':['font_family','font_effects'],
        'faces':['face_overlap','logo_overlap','logo_clear_space'],
        'wordmark':['logo_source','logo_size','logo_proportions'],
        'missing':['identity','font_family','logo_source','color_coverage'],
    }
    labels={}
    coverage={}
    for round_number, cases in scenarios.items():
        round_dir=output/f'round{round_number}';round_dir.mkdir(exist_ok=True)
        samples=[]
        for neutral,case in cases:
            ident=f'r{round_number}-{neutral}'
            folder=round_dir/ident;folder.mkdir(exist_ok=True)
            width,height=(900,1200) if round_number==1 else (960,1280)
            bg='#004165';canvas=Image.new('RGB',(width,height),bg)
            draw=ImageDraw.Draw(canvas)
            spec=dict(format='tm-poster-brand-check/v2',rule_set='tm-poster-brand-2026-08-v1',
                context='ordinary-club',document_kind='poster',target_width_px=width,print_width_in=7.5,
                inventory_complete=True,color_formulations=[dict(hex='#004165',rgb=[0,65,101],cmyk=[100,43,12,56],pantone='302')],
                color_regions=[],exclusions=[],layers=[],logos=[],faces=[],text_runs=[],
                contrast_pairs=[dict(foreground='#FFFFFF',background=bg)],
                identity=dict(custom_logo=False,custom_theme=False,custom_tagline=False))
            true_log=[]
            opaque_rects=[]
            gradient_regions=[]

            def add_text(text,xy,size=32,role='body',font='SourceSans3',family='Source Sans 3',color='#FFFFFF',effects=None):
                f=ImageFont.truetype(str(assets/(font+'.ttf')),size)
                bounds=draw.textbbox(xy,text,font=f,anchor='lt')
                if effects:
                    draw.text((xy[0]+3,xy[1]+3),text,font=f,fill='black',anchor='lt')
                    bounds=(bounds[0],bounds[1],bounds[2]+3,bounds[3]+3)
                draw.text(xy,text,font=f,fill=color,anchor='lt')
                b=[bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]]
                layer_id='text-'+str(len(spec['text_runs']))
                reference=folder/(layer_id+'.png');canvas.crop(bounds).save(reference)
                recipe=dict(renderer='Pillow',font_file=str(assets/(font+'.ttf')),font_sha256=sha(assets/(font+'.ttf')),
                    font_size_px=size,origin=list(xy),anchor='lt',color=color,background=bg,
                    reference_image=str(reference),reference_sha256=sha(reference),effects=effects or [])
                true_log.append(dict(id=layer_id,text=text,bounds=b,font_family=family,**recipe))
                run=dict(text=text,bounds=b,role=role,font_role='headline' if role=='headline' else 'body',
                    language='en',script='latin',font_family=family,font_file=recipe['font_file'],font_sha256=recipe['font_sha256'],
                    font_size_px=size,origin=list(xy),anchor='lt',color=color,background=bg,effects=effects or [],render_evidence=recipe)
                spec['text_runs'].append(run);spec['layers'].append(dict(id=layer_id,kind='text',bounds=b))
                opaque_rects.append((b,'text','Rendered text and antialiasing'))
                return run

            def add_logo(kind='ti',xy=(65,65),size=180,variant='full-color',placement=None):
                source=sources[kind];original=Image.open(source).convert('RGBA')
                crop=original.getchannel('A').getbbox()
                original=original.crop(crop)
                w=size;h=round(size*original.height/original.width)
                if placement:
                    w,h=placement
                x,y=xy
                candidate=original.resize((w,h),Image.Resampling.LANCZOS)
                logo_bg='#FFFFFF' if kind in ('wordmark','gavel') else bg
                # Measurements taken from the inspected official source: TI
                # wordmark bar spans rows551–955; Pathways' main word295–520;
                # standalone wordmark alpha bounds contain all129 source rows.
                measured_x={'ti':405,'pathways':226,'wordmark':129}.get(kind)
                if logo_bg=='#FFFFFF':
                    margin=math.ceil((measured_x or 170)*w/original.width)
                    plate=[x-margin,y-margin,w+2*margin,h+2*margin]
                    draw.rectangle((plate[0],plate[1],plate[0]+plate[2]-1,plate[1]+plate[3]-1),fill=logo_bg)
                    opaque_rects.append((plate,'official-asset','Uniform backing and clear space for original logo'))
                underlay=Image.new('RGBA',(w,h),logo_bg);underlay.alpha_composite(candidate)
                canvas.paste(underlay.convert('RGB'),(x,y))
                lid='logo-'+str(len(spec['logos']))
                b=[x,y,w,h]
                entry=dict(kind='pathways-badge' if kind=='badge' else kind,variant=variant,layer_id=lid,bounds=b,
                    source=str(source),source_bounds=[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]],
                    source_sha256=sha(source),provenance=urls[kind],background=logo_bg,source_wordmark_height_px=measured_x,
                    source_wordmark_measurement={'ti':'Inspected official bar, fullwidth alpha rows551–955 inclusive','pathways':'Inspected main PATHWAYS word alpha rows295–520 inclusive','wordmark':'Standalone complete wordmark alpha height129'}.get(kind,'No standalone numeric X established for this asset'),
                    effects=[],transform=dict(rotation_deg=0,skew_x_deg=0,skew_y_deg=0,perspective=False))
                spec['logos'].append(entry);spec['layers'].append(dict(id=lid,kind='logo',bounds=b))
                opaque_rects.append((b,'official-asset','Official original derived at declared proportional size'))
                return entry

            logo_kind='gavel' if case=='gavel' else 'pathways' if case=='pathways' else 'wordmark' if case=='wordmark' else 'ti'
            logo_xy=(65,65) if round_number==1 else (width-260,65)
            visual_revision = revision >= 3
            if case=='missing' and visual_revision:
                logo_xy=(3,3)
            if case=='wordmark':
                # Black official wordmark has a white backing to preserve contrast.
                logo_xy=(65,65)
            logo=add_logo(logo_kind,logo_xy,40 if case=='missing' and visual_revision else 60 if case=='small' else 180,
                          'loyal-blue' if case=='gavel' else 'black' if case=='wordmark' else 'full-color',
                          (180,80) if case=='recolor' else None)
            heading='Practice Together' if round_number==1 else 'Confident Voices'
            add_text(heading,(65,300),44,'headline','Montserrat','Montserrat')
            add_text('A public speaking workshop',(65,380),30)
            add_text('Saturday | 19:00-21:00 | Online',(65,435),27)
            add_text('Where Leaders Are Made',(65,505),28,'tagline')
            if case=='ornate':
                spec['special_event']=True
                add_text('Club Anniversary',(65,590),60,'headline','Corinthia','Corinthia')
            else:
                add_text('Find Your Voice',(65,590),32,'marketing-phrase')
            if case=='corporate':
                spec['context']='corporate-club'
                b=[65,850,180,65];draw.rectangle((65,850,244,914),fill='#772432')
                draw.text((80,870),'ACME',font=ImageFont.truetype(str(assets/'Montserrat.ttf'),25),fill='white')
                spec['logos'].append(dict(kind='corporate',bounds=b));spec['layers'].append(dict(id='corp',kind='logo',bounds=b))
                opaque_rects.append((b,'official-asset','Synthetic corporation mark, not a club mark'))
            if case in ('conference','fall'):
                spec['context']='annual-district-conference';spec['identity']['custom_theme']=True
                spec.update(conference=dict(annual=True,date='2027-04-20' if case=='conference' else '2026-10-20',end_date='2027-04-21' if case=='conference' else '2026-10-21',district_number=85),as_of_date='2027-04-01' if case=='conference' else '2026-10-25')
                add_text('District 85 Annual Conference',(65,680),33,'headline','Montserrat','Montserrat')
                section=[550,850,280,180];spec['sponsor_sections']=[dict(bounds=section)]
                b=[590,900,170,50] if case=='conference' else [65,790,170,50]
                draw.rectangle((b[0],b[1],b[0]+b[2]-1,b[1]+b[3]-1),fill='#A9B2B1')
                spec['logos'].append(dict(kind='sponsor',bounds=b));spec['layers'].append(dict(id='sponsor',kind='logo',bounds=b))
                opaque_rects.append((b,'official-asset','Synthetic sponsor logo'))
            if case=='gavel':
                spec['context']='gavel-club'
            if case=='pathways':
                badge=add_logo('badge',(65,790),145,'official')
                badge.update(association='Presentation Mastery',decorative=False)
                add_text('Presentation Mastery: project practice',(250,825),27)
            if case in ('gray','purple','radial'):
                region=dict(bounds=[65,800,440,160],mode='gradient',colors=['#A9B2B1','#F5F5F5'] if case=='gray' else ['#004165','#006094'],geometry='radial' if case=='radial' else 'horizontal',tolerance=0)
                if case=='gray':region.update(opacity=.4,background=bg,overlay=dict(color='#004165',opacity=.7))
                if case=='radial':region.update(center=[285,880],radii=[220,80])
                if case=='purple':region['colors']=['#663399','#FF9900']
                start=tuple(int(region['colors'][0][i:i+2],16) for i in (1,3,5));end=tuple(int(region['colors'][1][i:i+2],16) for i in (1,3,5))
                for y in range(800,960):
                    for x in range(65,505):
                        t=min(1,math.hypot((x-285)/220,(y-880)/80)) if case=='radial' else (x-65)/439
                        values=[round(a+(b-a)*t) for a,b in zip(start,end)]
                        if case=='gray':
                            values=[round(v*.4+b*.6) for v,b in zip(values,(0,65,101))]
                            values=[round(v*.3+b*.7) for v,b in zip(values,(0,65,101))]
                        canvas.putpixel((x,y),tuple(values))
                gradient_regions.append(region)
                if case=='purple':
                    spec['color_formulations'][0]['cmyk']=[90,20,10,0]
            if case=='shadow':
                run=add_text('where leaders are made',(65,690),33,'tagline',effects=['drop-shadow'])
                run['effects']=[]
            if case=='fakefont':
                if not (assets/'DejaVuSerif.ttf').is_file():
                    raise ValueError('Supply DejaVuSerif.ttf in private assets for the different-font test')
                run=add_text('Leadership in action',(65,690),40,'headline','DejaVuSerif','DejaVu Serif')
                run.update(font_family='Montserrat',font_file=str(assets/'Montserrat.ttf'),font_sha256=sha(assets/'Montserrat.ttf'))
            if case=='phrases':
                add_text('Invest in a Brighter Future',(65,690),32,'marketing-phrase')
                add_text('WHERE leaders ARE made',(65,755),30,'tagline')
            if case=='recolor':
                x,y,w,h=logo['bounds']
                crop=canvas.crop((x,y,x+w,y+h))
                for cy in range(h):
                    for cx in range(w):
                        r,g,b=crop.getpixel((cx,cy))
                        if b>r+10 and b>g:
                            crop.putpixel((cx,cy),(235,110,20))
                canvas.paste(crop,(x,y))
                layer=[x-10,y+20,50,35];draw.rectangle((layer[0],layer[1],layer[0]+49,layer[1]+34),fill='#F2DF74')
                spec['layers'].append(dict(id='overlay',kind='text',bounds=layer));opaque_rects.append((layer,'text','Foreground label'))
            if case=='legacy':
                logo.update(era='pre-2011',experimental=True,effects=['patterned-glow'])
                spec['identity'].update(custom_logo=True,custom_tagline=True)
                if visual_revision:
                    logo.update(era='current',experimental=False)
                    x,y,w,h=logo['bounds']
                    for py in range(y-28,y+h+28):
                        for px in range(x-28,x+w+28):
                            if not (x<=px<x+w and y<=py<y+h) and (px+py)%12<5:
                                canvas.putpixel((px,py),(180,80,210))
                    patch=canvas.crop((x,y,x+w,y+h))
                    for py in range(h):
                        for px in range(w):
                            r,g,b=patch.getpixel((px,py))
                            if b>r+10 and b>g:
                                patch.putpixel((px,py),(235,110,20))
                    canvas.paste(patch,(x,y))
                draw.text((65,700),'THE UNSTOPPABLE CLUB',font=ImageFont.truetype(str(assets/'Montserrat.ttf'),34),fill='#F2DF74')
                opaque_rects.append(([65,700,520,50],'text','Organizational identity text'))
            if case=='faces':
                f=[logo['bounds'][0],logo['bounds'][1]+40,120,140]
                draw.ellipse((f[0],f[1],f[0]+120,f[1]+140),fill='#F2DF74')
                draw.ellipse((f[0]+25,f[1]+40,f[0]+35,f[1]+50),fill='black')
                draw.ellipse((f[0]+80,f[1]+40,f[0]+90,f[1]+50),fill='black')
                spec['faces']=[dict(bounds=f)]
                spec['layers'].append(dict(id='portrait',kind='photo',bounds=f));opaque_rects.append((f,'photo','Synthetic diagram face'))
            # Partition exposed design fill into disjoint rectangles rather than
            # pretending a few favorable swatches establish whole-image coverage.
            occupied=[b for b,k,r in opaque_rects]+[r['bounds'] for r in gradient_regions]
            xs=sorted({0,width}|{v for b in occupied for v in (b[0],b[0]+b[2])})
            ys=sorted({0,height}|{v for b in occupied for v in (b[1],b[1]+b[3])})
            for x0,x1 in zip(xs,xs[1:]):
                for y0,y1 in zip(ys,ys[1:]):
                    if not any(max(x0,b[0])<min(x1,b[0]+b[2]) and max(y0,b[1])<min(y1,b[1]+b[3]) for b in occupied):
                        spec['color_regions'].append(dict(bounds=[x0,y0,x1-x0,y1-y0],mode='solid',color=bg))
            spec['color_regions']+=gradient_regions
            spec['exclusions']=[dict(bounds=b,kind=k,reason=r) for b,k,r in opaque_rects]
            source_artifact=folder/'renderer-log.json';save_json(source_artifact,dict(renderer='Pillow',canvas=[width,height],background=bg,text_runs=true_log))
            for run in spec['text_runs']:
                run['render_evidence']['source_artifact']=str(source_artifact)
            image_path=folder/('poster.jpg' if case=='jpeg' else 'poster.png')
            canvas.save(image_path,quality=73) if case=='jpeg' else canvas.save(image_path)
            spec['candidate_sha256']=sha(image_path)
            if case=='missing' and not visual_revision:
                spec['inventory_complete']=False;spec['logos'][0].pop('source_sha256')
                spec['text_runs'][0].pop('font_file');spec['text_runs'][0].pop('render_evidence')
                spec['exclusions']=[]
            spec_path=folder/'spec.json';save_json(spec_path,spec)
            evidence=dict(renderer_log=str(source_artifact),font_sources=[str(assets/'Montserrat.ttf'),str(assets/'SourceSans3.ttf')],logo_source=str(sources[logo_kind]),source_url=urls[logo_kind],manual_path=str(assets/'manual.pdf'))
            selected_targets=['logo_size','logo_clear_space','logo_source'] if case=='missing' and visual_revision else targets[case]
            samples.append(dict(id=ident,image=str(image_path),spec=str(spec_path),target_checks=selected_targets,evidence=evidence,
                scope='Only listed objective feature checks with supplied actual pixels and source evidence; not whole-brand or release approval'))
            labels[ident]=dict(intended='positive' if case in intended_positive else 'negative',scenario=case,checks=selected_targets)
            for feature in selected_targets:coverage.setdefault(feature,[]).append(ident)
        manifest=dict(round=round_number,manual=dict(path=str(assets/'manual.pdf'),url='https://content.toastmasters.org/image/upload/02330-001-0001-brand-manual.pdf',sha256=sha(assets/'manual.pdf')),samples=samples)
        save_json(round_dir/'manifest.json',manifest)
        thumbs=[]
        for sample in samples:
            im=Image.open(sample['image']).convert('RGB');im.thumbnail((270,360))
            tile=Image.new('RGB',(300,400),'white');tile.paste(im,((300-im.width)//2,20));ImageDraw.Draw(tile).text((10,380),sample['id'],fill='black');thumbs.append(tile)
        sheet=Image.new('RGB',(1500,800),'#CCCCCC')
        for i,tile in enumerate(thumbs):sheet.paste(tile,((i%5)*300,(i//5)*400))
        sheet.save(round_dir/'contact-sheet.jpg')
    save_json(output/'intended-labels-private.json',labels)
    save_json(output/'feature-coverage.json',dict(features=coverage,limitations=['Scopes are objective feature checks, not blanket whole-brand approval','Unmeasurable semantic/approval questions require separate reviewer intelligence','Legacy/experimental statuses are contextual source evidence, not inferred from an intentionally fabricated historical logo','No third-party public poster is claimed an official positive example']))
    inventory={str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file() and p.name not in ('sha256-inventory.json',)}
    save_json(output/'sha256-inventory.json',inventory)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--revision',type=int,choices=(2,3),default=3,
                        help='3 uses demonstrable pixel defects; 2 retains earlier evidence-negative cases')
    args=parser.parse_args();build(args.assets.resolve(),args.output.resolve(),args.revision)
