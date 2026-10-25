"""Fresh private round3: ten source-backed samples, independent labels withheld.

Uses only local official assets prepared by build_poster_benchmark.py. No
production checker import or predictions are used to construct this dataset.
"""
import argparse
import copy
import hashlib
import json
import math
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(assets,output):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Fresh output directory required')
    output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(assets/'logo.zip') as archive:
        for key,member in [('gray','ToastmastersLogo/Grayscale/ToastmastersLogoGrayscale.png'),('white','ToastmastersLogo/White/ToastmastersLogoWhite.png')]:
            (assets/(key+'.png')).write_bytes(archive.read(member))
    # Neutral order; do not expose these construction intents to the reviewer.
    cases=[('u71','gray'),('v14','perspective'),('w62','roles'),('x39','gavel'),
           ('y08','white-jpeg'),('z53','opacity'),('a26','crop-padding'),
           ('b81','badge'),('c47','corporate'),('d95','corporate-overlap')]
    positives={'gray','roles','white-jpeg','crop-padding','corporate'}
    targets={
        'gray':['logo_source','logo_size','logo_clear_space'],
        'perspective':['logo_transform','logo_source'],
        'roles':['font_family','font_effects'],
        'gavel':['gavel_identity'],
        'white-jpeg':['logo_source','logo_size','logo_proportions'],
        'opacity':['gray_opacity','gradient','font_family'],
        'crop-padding':['logo_source','logo_proportions','logo_size'],
        'badge':['badge_relevance'],
        'corporate':['corporate_placement','logo_source'],
        'corporate-overlap':['corporate_placement','logo_overlap','color_coverage'],
    }
    samples=[];intended={}
    for neutral,case in cases:
        ident='r3-'+neutral;folder=output/ident;folder.mkdir()
        width,height=1024,1366;bg='#772432'
        image=Image.new('RGB',(width,height),bg);draw=ImageDraw.Draw(image)
        spec=dict(format='tm-poster-brand-check/v2',rule_set='tm-poster-brand-2026-08-v1',
            context='ordinary-club',document_kind='poster',candidate_sha256=None,
            target_width_px=width,print_width_in=8.5,inventory_complete=True,
            identity=dict(custom_logo=False,custom_theme=False,custom_tagline=False),
            color_formulations=[dict(hex='#772432',rgb=[119,36,50],cmyk=[12,95,59,54],pantone='188')],
            color_regions=[],exclusions=[],layers=[],logos=[],faces=[],text_runs=[],
            contrast_pairs=[dict(foreground='#FFFFFF',background=bg)])
        exclusions=[];recipes=[]

        def text(value,origin,size,role,family,file):
            font=ImageFont.truetype(str(assets/file),size)
            bounds=draw.textbbox(origin,value,font=font,anchor='lt');draw.text(origin,value,font=font,anchor='lt',fill='white')
            b=[bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]]
            index=len(spec['text_runs']);lid='text-'+str(index)
            reference=folder/(lid+'.png');image.crop(bounds).save(reference)
            recipe=dict(renderer='Pillow',font_file=str(assets/file),font_sha256=sha(assets/file),
                font_size_px=size,origin=list(origin),anchor='lt',color='#FFFFFF',background=bg,
                reference_image=str(reference),reference_sha256=sha(reference),effects=[])
            run=dict(text=value,bounds=b,role=role,font_role=role,script='latin',language='en',
                font_family=family,font_file=recipe['font_file'],font_sha256=recipe['font_sha256'],
                font_size_px=size,origin=list(origin),anchor='lt',color='#FFFFFF',background=bg,
                effects=[],render_evidence=recipe)
            spec['text_runs'].append(run);spec['layers'].append(dict(id=lid,kind='text',bounds=b))
            exclusions.append(dict(bounds=b,kind='text',reason='Actual rendered text and antialiasing'))
            recipes.append(dict(id=lid,text=value,font_family=family,bounds=b,**recipe))
            return run

        source=assets/('gray.png' if case in ('gray','crop-padding') else 'white.png' if case=='white-jpeg' else 'ti.png')
        source_image=Image.open(source).convert('RGBA');crop=source_image.getchannel('A').getbbox();tight=source_image.crop(crop)
        logo_w=210;logo_h=round(logo_w*tight.height/tight.width);x,y=105,105
        if case=='crop-padding':
            x=width-315
        logo_render=tight.resize((logo_w,logo_h),Image.Resampling.LANCZOS)
        if case=='perspective':
            logo_render=logo_render.transform(logo_render.size,Image.Transform.PERSPECTIVE,
                (1,.28,-24,0,1,0,.0008,0),resample=Image.Resampling.BICUBIC)
        composite=Image.new('RGBA',logo_render.size,bg);composite.alpha_composite(logo_render);image.paste(composite.convert('RGB'),(x,y))
        variant='grayscale' if case in ('gray','crop-padding') else 'white' if case=='white-jpeg' else 'full-color'
        source_x=292 if variant=='grayscale' else 417 if variant=='white' else 405
        logo=dict(kind='ti',variant=variant,bounds=[x,y,logo_w,logo_h],layer_id='ti-logo',source=str(source),
            source_sha256=sha(source),source_bounds=[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]],
            provenance='https://ccdn.toastmasters.org/content/toastmasters-logo.zip',background=bg,
            source_wordmark_height_px=source_x,effects=[],transform=dict(rotation_deg=0,skew_x_deg=0,skew_y_deg=0,perspective=case=='perspective'))
        logo['source_wordmark_measurement']='Measured fullwidth alpha-bar band from independently inspectable official variant; clear margin105px exceeds its scaled height'
        spec['logos'].append(logo);spec['layers'].append(dict(id='ti-logo',kind='logo',bounds=logo['bounds']))
        exclusions.append(dict(bounds=logo['bounds'],kind='official-asset',reason='Official source variant rendered to declared size'))

        text('A Better Speaking Habit',(105,390),48,'headline','Montserrat','Montserrat.ttf')
        text('Weekly practice for confident communication',(105,485),31,'body','Source Sans 3','SourceSans3.ttf')
        text('Open workshop | Thursday | 18:30-20:00',(105,545),29,'body','Source Sans 3','SourceSans3.ttf')
        text('Where Leaders Are Made',(105,620),32,'tagline','Source Sans 3','SourceSans3.ttf')
        if case=='roles':
            text('Build one skill at a time',(105,780),39,'headline','Montserrat','Montserrat.ttf')
            text('Practice, listen, and try again.',(105,850),30,'body','Source Sans 3','SourceSans3.ttf')
        if case=='opacity':
            # An actually rendered30% gray gradient, not a metadata-only defect.
            region=dict(bounds=[105,830,700,190],mode='gradient',colors=['#A9B2B1','#F5F5F5'],geometry='vertical',opacity=.3,background=bg,tolerance=1)
            for yy in range(830,1020):
                for xx in range(105,805):
                    t=(yy-830)/189
                    base=[a+(b-a)*t for a,b in zip((169,178,177),(245,245,245))]
                    image.putpixel((xx,yy),tuple(round(v*.3+b*.7) for v,b in zip(base,(119,36,50))))
            spec['color_regions'].append(region)
            text('Notice this headline',(105,740),39,'headline','Source Sans 3','SourceSans3.ttf')
            text('This is explanatory body copy.',(105,1085),30,'body','Montserrat','Montserrat.ttf')
        if case=='gavel':
            spec['context']='gavel-club';text('Gavel Club Practice',(105,800),40,'headline','Montserrat','Montserrat.ttf')
        if case=='badge':
            source_badge=assets/'badge.png';badge=Image.open(source_badge).convert('RGBA');badge=badge.crop(badge.getchannel('A').getbbox())
            for i,(bx,by) in enumerate(((350,870),(500,870),(300,1010),(425,1080),(550,1010))):
                bw=110;bh=round(bw*badge.height/badge.width);render=badge.resize((bw,bh),Image.Resampling.LANCZOS)
                tile=Image.new('RGBA',render.size,bg);tile.alpha_composite(render);image.paste(tile.convert('RGB'),(bx,by))
                bounds=[bx,by,bw,bh];bid='badge-'+str(i)
                spec['logos'].append(dict(kind='pathways-badge',variant='official',layer_id=bid,bounds=bounds,
                    source=str(source_badge),source_sha256=sha(source_badge),provenance='https://ccdn.toastmasters.org/content/pathways-badge.zip',
                    background=bg,effects=[],transform=dict(rotation_deg=0,skew_x_deg=0,skew_y_deg=0,perspective=False),
                    association=None,decorative=True))
                spec['layers'].append(dict(id=bid,kind='logo',bounds=bounds));exclusions.append(dict(bounds=bounds,kind='official-asset',reason='Official badge displayed in invitation artwork'))
            text('Club Social Evening',(105,740),40,'headline','Montserrat','Montserrat.ttf')
        if case in ('corporate','corporate-overlap'):
            spec['context']='corporate-club';b=[610,1060,240,90] if case=='corporate' else [x+60,y+55,210,100]
            draw.rectangle((b[0],b[1],b[0]+b[2]-1,b[1]+b[3]-1),fill='#A9B2B1')
            draw.text((b[0]+15,b[1]+25),'ACME',font=ImageFont.truetype(str(assets/'Montserrat.ttf'),32),fill='#004165')
            spec['logos'].append(dict(kind='corporate',bounds=b));spec['layers'].append(dict(id='corporation',kind='logo',bounds=b))
            exclusions.append(dict(bounds=b,kind='official-asset',reason='Synthetic corporation identity mark'))
        occupied=[e['bounds'] for e in exclusions]+[r['bounds'] for r in spec['color_regions']]
        xs=sorted({0,width}|{v for b in occupied for v in (b[0],b[0]+b[2])});ys=sorted({0,height}|{v for b in occupied for v in (b[1],b[1]+b[3])})
        for x0,x1 in zip(xs,xs[1:]):
            for y0,y1 in zip(ys,ys[1:]):
                if not any(max(x0,b[0])<min(x1,b[0]+b[2]) and max(y0,b[1])<min(y1,b[1]+b[3]) for b in occupied):
                    spec['color_regions'].append(dict(bounds=[x0,y0,x1-x0,y1-y0],mode='solid',color=bg,tolerance=1))
        spec['exclusions']=exclusions
        if case=='corporate-overlap':
            # Omit a known area from the assessment inventory as a separate
            # coverage failure; this is not intended to prove visual color drift.
            spec['color_regions']=[r for r in spec['color_regions'] if r['bounds'][1]!=0]
        log=folder/'renderer-log.json';write(log,dict(renderer='Pillow',canvas=[width,height],background=bg,text_runs=recipes,
            logo_render=dict(source=str(source),source_sha256=sha(source),crop=list(crop),perspective=case=='perspective')))
        for run in spec['text_runs']:run['render_evidence']['source_artifact']=str(log)
        path=folder/('poster.jpg' if case=='white-jpeg' else 'poster.png')
        image.save(path,quality=47) if case=='white-jpeg' else image.save(path)
        spec['candidate_sha256']=sha(path);spec_path=folder/'spec.json';write(spec_path,spec)
        selectors=[]
        selector_map={}
        for key in targets[case]:
            selector=dict(check=key)
            if key.startswith('logo_'):
                selector['logo']=0
                selector_map[key]=dict(logo=0)
            if key=='badge_relevance':selector['logos']=list(range(1,6))
            selectors.append(selector)
        samples.append(dict(id=ident,image=str(path),spec=str(spec_path),target_checks=targets[case],target_entities=selectors,target_selectors=selector_map,
            evidence=dict(renderer_log=str(log),logo_source=str(source),source_url='https://ccdn.toastmasters.org/content/toastmasters-logo.zip',manual_path=str(assets/'manual.pdf')),
            scope='Listed objective feature checks with explicit applicable entities; actual image/source evidence required. No full brand or release verdict.'))
        intended[ident]=dict(intended='positive' if case in positives else 'negative',construction=case,checks=targets[case])
    image_hashes=[sha(sample['image']) for sample in samples]
    if len(set(image_hashes))!=len(image_hashes):
        raise ValueError('Duplicate rendered image stimuli: revise construction before freezing this round')
    write(output/'manifest.json',dict(round=3,manual=dict(path=str(assets/'manual.pdf'),url='https://content.toastmasters.org/image/upload/02330-001-0001-brand-manual.pdf',sha256=sha(assets/'manual.pdf')),samples=samples))
    write(output/'intended-labels-private.json',intended)
    sheet=Image.new('RGB',(1500,820),'#CCCCCC')
    for i,sample in enumerate(samples):
        im=Image.open(sample['image']).convert('RGB');im.thumbnail((280,370));tile=Image.new('RGB',(300,410),'white');tile.paste(im,((300-im.width)//2,10));ImageDraw.Draw(tile).text((10,390),sample['id'],fill='black');sheet.paste(tile,((i%5)*300,(i//5)*410))
    sheet.save(output/'contact-sheet.jpg')
    inventory={str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()}
    write(output/'sha256-inventory.json',inventory)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();build(args.assets.resolve(),args.output.resolve())
