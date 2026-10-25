"""Fresh round4 boundary/generalization stimuli, without reading checker outputs."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(assets,output,clear_space_inset=15):
    if output.exists() and any(output.iterdir()):raise ValueError('Fresh output directory required')
    output.mkdir(parents=True,exist_ok=True)
    # Actual standard-weight font instances, with inspectable originals and
    # derived files. The production renderer must read actual font bytes.
    fonts={}
    for key,name,weight in [('heading','Montserrat',600),('body','SourceSans3',400)]:
        path=output/(name+'-'+str(weight)+'.ttf')
        with TTFont(assets/(name+'.ttf')) as source:
            instantiated=instantiateVariableFont(source,{'wght':weight},inplace=False)
            instantiated.save(path)
        fonts[key]=path
    cases=[('e18','jpeg'),('f72','copy'),('g35','boundary'),('h06','clearspace'),
           ('i49','reverse'),('j83','shadow'),('k27','types'),('l64','font'),
           ('m91','nearest'),('n53','endpoints')]
    positive={'jpeg','boundary','reverse','types','nearest'}
    targets={
        'jpeg':['logo_source','logo_proportions','logo_size'],
        'copy':['tagline','font_family'],
        'boundary':['logo_source','logo_clear_space','logo_size'],
        'clearspace':['logo_clear_space'],
        'reverse':['gradient','gray_opacity','transparency'],
        'shadow':['font_effects','font_family'],
        'types':['font_family','font_effects','tagline','marketing_phrases'],
        'font':['font_family'],
        'nearest':['logo_source','logo_proportions','logo_transform'],
        'endpoints':['gradient','palette'],
    }
    manifests=[];labels={}
    for index,(neutral,case) in enumerate(cases):
        ident='r4-'+neutral;folder=output/ident;folder.mkdir()
        width,height=1100,1440;bg='#004165'
        image=Image.new('RGB',(width,height),bg);draw=ImageDraw.Draw(image)
        spec=dict(format='tm-poster-brand-check/v2',rule_set='tm-poster-brand-2026-08-v1',context='ordinary-club',document_kind='poster',
            target_width_px=width,print_width_in=8.5,inventory_complete=True,identity=dict(custom_logo=False,custom_theme=False,custom_tagline=False),
            color_formulations=[dict(hex='#004165',rgb=[0,65,101],cmyk=[100,43,12,56],pantone='302')],
            color_regions=[],exclusions=[],layers=[],logos=[],faces=[],text_runs=[],contrast_pairs=[dict(foreground='#FFFFFF',background=bg)])
        true_runs=[];occupied=[];rendered_gradient=[]

        def add_text(value,xy,size=34,role='body',font_key='body',family='Source Sans 3',shadow=False,declared=None):
            font_file=fonts[font_key] if font_key in fonts else assets/'DejaVuSerif.ttf'
            font=ImageFont.truetype(str(font_file),size)
            bounds=draw.textbbox(xy,value,font=font,anchor='lt')
            if shadow:
                draw.text((xy[0]+5,xy[1]+5),value,font=font,anchor='lt',fill='#111111')
                bounds=(bounds[0],bounds[1],bounds[2]+5,bounds[3]+5)
            draw.text(xy,value,font=font,anchor='lt',fill='white')
            b=[bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]]
            lid='text-'+str(len(spec['text_runs']));reference=folder/(lid+'.png');image.crop(bounds).save(reference)
            recipe=dict(renderer='Pillow',font_file=str(font_file),font_sha256=sha(font_file),font_size_px=size,origin=list(xy),anchor='lt',color='#FFFFFF',background=bg,
                        reference_image=str(reference),reference_sha256=sha(reference),effects=['drop-shadow'] if shadow else [])
            true_runs.append(dict(id=lid,text=value,bounds=b,font_family=family,**recipe))
            run=dict(text=declared or value,bounds=b,role=role,font_role='headline' if role=='headline' else 'body',font_family=family,
                     script='latin',language='en',font_file=str(font_file),font_sha256=sha(font_file),font_size_px=size,origin=list(xy),anchor='lt',color='#FFFFFF',background=bg,
                     effects=[],render_evidence=recipe)
            if font_key=='other':
                run.update(font_family='Montserrat',font_file=str(fonts['heading']),font_sha256=sha(fonts['heading']))
            spec['text_runs'].append(run);spec['layers'].append(dict(id=lid,kind='text',bounds=b));occupied.append(dict(bounds=b,kind='text',reason='Actual rendered text/effects'))
            return run

        source=assets/('white.png' if case=='boundary' else 'ti.png')
        original=Image.open(source).convert('RGBA');alpha_crop=original.getchannel('A').getbbox();tight=original.crop(alpha_crop)
        logo_w=225 if case!='nearest' else 181;logo_h=round(logo_w*tight.height/tight.width)
        measured_x=417 if case=='boundary' else 405
        margin=math.ceil(measured_x*logo_w/tight.width)
        x,y=(85,margin) if case=='boundary' else (85,margin-clear_space_inset) if case=='clearspace' else (width-340,85)
        resampler=Image.Resampling.NEAREST if case=='nearest' else Image.Resampling.BICUBIC if case=='jpeg' else Image.Resampling.LANCZOS
        scaled=tight.resize((logo_w,logo_h),resampler);plate=Image.new('RGBA',scaled.size,bg);plate.alpha_composite(scaled);image.paste(plate.convert('RGB'),(x,y))
        logo=dict(kind='ti',variant='white' if case=='boundary' else 'full-color',layer_id='logo',bounds=[x,y,logo_w,logo_h],source=str(source),source_sha256=sha(source),
                  source_bounds=[alpha_crop[0],alpha_crop[1],alpha_crop[2]-alpha_crop[0],alpha_crop[3]-alpha_crop[1]],provenance='https://ccdn.toastmasters.org/content/toastmasters-logo.zip',
                  background=bg,source_wordmark_height_px=measured_x,effects=[],transform=dict(rotation_deg=0,skew_x_deg=0,skew_y_deg=0,perspective=False))
        logo['source_wordmark_measurement']='Inspected fullwidth alpha-bar source span; manualX scaled conservatively and rounded upward'
        spec['logos'].append(logo);spec['layers'].append(dict(id='logo',kind='logo',bounds=logo['bounds']));occupied.append(dict(bounds=logo['bounds'],kind='official-asset',reason='Official original rendered at known size'))
        titles=['Speak with Purpose','Lead through Listening','A Confident Beginning','Practice and Progress','Discover Your Voice','Ideas into Action','Learn by Speaking','Stories that Connect','Build Speaking Habits','A Shared Learning Journey']
        add_text(titles[index],(85,390),55,'headline','heading','Montserrat')
        add_text('A club workshop for thoughtful communication',(85,490),34)
        add_text('Thursday 18:30-20:00 | Open online session',(85,555),31)
        if case=='copy':
            add_text('Where Leaders Are Changed',(85,665),40,'tagline',declared='Where Leaders Are Made')
        else:
            add_text('WHERE LEADERS ARE MADE' if case=='types' else 'Where Leaders Are Made',(85,665),36,'tagline')
        add_text('Find Your Voice',(85,750),36,'marketing-phrase')
        if case=='shadow':
            add_text('Connect. Practice. Grow.',(85,910),45,'headline','heading','Montserrat',shadow=True)
        elif case=='font':
            add_text('A new perspective',(85,910),46,'headline','other','DejaVu Serif')
        elif case=='types':
            add_text('One voice can make a difference',(85,910),40,'headline','heading','Montserrat')
            add_text('Listen with care and share your story.',(85,990),33)
        if case in ('reverse','endpoints'):
            region=dict(bounds=[85,970,810,210],mode='gradient',colors=['#F5F5F5','#A9B2B1'] if case=='reverse' else ['#330066','#FF8800'],
                        geometry='vertical' if case=='reverse' else 'horizontal',opacity=.6 if case=='reverse' else 1,background=bg,tolerance=1)
            if case=='reverse':region['overlay']=dict(color='#004165',opacity=.5)
            starts=[int(region['colors'][0][i:i+2],16) for i in (1,3,5)];ends=[int(region['colors'][1][i:i+2],16) for i in (1,3,5)]
            for yy in range(970,1180):
                for xx in range(85,895):
                    t=(yy-970)/209 if case=='reverse' else (xx-85)/809
                    values=[round(a+(b-a)*t) for a,b in zip(starts,ends)]
                    if case=='reverse':
                        values=[round(v*.6+b*.4) for v,b in zip(values,(0,65,101))]
                        values=[round(v*.5+b*.5) for v,b in zip(values,(0,65,101))]
                    image.putpixel((xx,yy),tuple(values))
            rendered_gradient.append(region)
        cutouts=[e['bounds'] for e in occupied]+[r['bounds'] for r in rendered_gradient]
        xs=sorted({0,width}|{v for b in cutouts for v in (b[0],b[0]+b[2])});ys=sorted({0,height}|{v for b in cutouts for v in (b[1],b[1]+b[3])})
        for x0,x1 in zip(xs,xs[1:]):
            for y0,y1 in zip(ys,ys[1:]):
                if not any(max(x0,b[0])<min(x1,b[0]+b[2]) and max(y0,b[1])<min(y1,b[1]+b[3]) for b in cutouts):
                    spec['color_regions'].append(dict(bounds=[x0,y0,x1-x0,y1-y0],mode='solid',color=bg,tolerance=1))
        spec['color_regions']+=rendered_gradient;spec['exclusions']=occupied
        log=folder/'renderer-log.json';write(log,dict(renderer='Pillow',canvas=[width,height],background=bg,text_runs=true_runs,
                    logo_render=dict(source=str(source),bounds=logo['bounds'],source_crop=list(alpha_crop),resampling=int(resampler))))
        for run in spec['text_runs']:run['render_evidence']['source_artifact']=str(log)
        path=folder/('poster.jpg' if case=='jpeg' else 'poster.png');image.save(path,quality=61,subsampling=2) if case=='jpeg' else image.save(path)
        spec['candidate_sha256']=sha(path);spec_path=folder/'spec.json';write(spec_path,spec)
        selectors={key:dict(logo=0) for key in targets[case] if key.startswith('logo_')}
        manifests.append(dict(id=ident,image=str(path),spec=str(spec_path),target_checks=targets[case],target_selectors=selectors,
            evidence=dict(renderer_log=str(log),logo_source=str(source),source_url='https://ccdn.toastmasters.org/content/toastmasters-logo.zip',manual_path=str(assets/'manual.pdf')),
            scope='Only named objective features and selected entities; actual pixels/source evidence required, not whole-brand or release approval'))
        labels[ident]=dict(intended='positive' if case in positive else 'negative',construction=case,checks=targets[case])
    hashes=[sha(sample['image']) for sample in manifests]
    if len(set(hashes))!=10:raise ValueError('Require ten distinct image stimuli')
    write(output/'manifest.json',dict(round=4,manual=dict(path=str(assets/'manual.pdf'),url='https://content.toastmasters.org/image/upload/02330-001-0001-brand-manual.pdf',sha256=sha(assets/'manual.pdf')),samples=manifests))
    write(output/'intended-labels-private.json',labels)
    sheet=Image.new('RGB',(1500,820),'#CCCCCC')
    for i,sample in enumerate(manifests):
        im=Image.open(sample['image']).convert('RGB');im.thumbnail((280,370));tile=Image.new('RGB',(300,410),'white');tile.paste(im,((300-im.width)//2,10));ImageDraw.Draw(tile).text((10,390),sample['id'],fill='black');sheet.paste(tile,((i%5)*300,(i//5)*410))
    sheet.save(output/'contact-sheet.jpg')
    write(output/'sha256-inventory.json',{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--clear-space-inset',type=int,default=15,choices=(1,15),help='1 reproduces the earlier ambiguous rounding control; 15 makes a substantive clear-space deficit')
    args=parser.parse_args();build(args.assets.resolve(),args.output.resolve(),args.clear_space_inset)
