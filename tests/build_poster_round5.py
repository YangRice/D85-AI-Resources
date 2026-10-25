"""Fresh final validation batches; no checker/prediction imports or oracle reads."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(assets,output,round_number=5):
    if output.exists() and any(output.iterdir()):raise ValueError('Fresh output directory required')
    output.mkdir(parents=True,exist_ok=True)
    fonts={}
    variations=[('headline','Montserrat',700),('body','SourceSans3',500)] if round_number==5 else [('headline','Montserrat',500),('body','SourceSans3',400)]
    for key,name,weight in variations:
        path=output/(name+'-'+str(weight)+'.ttf')
        with TTFont(assets/(name+'.ttf')) as source:instantiateVariableFont(source,{'wght':weight},inplace=False).save(path)
        fonts[key]=path
    cases=[('p38','quantized'),('q74','tagline'),('r19','jpeg-a'),('s62','narrow'),('t45','font'),
           ('u03','gray'),('v87','shadow'),('w26','typography'),('x51','space'),('y90','jpeg-b')]
    if round_number==6:
        cases=[('b73','jpeg-a'),('c18','space'),('d64','gray'),('e92','tagline'),('f37','typography'),
               ('g05','font'),('h81','quantized'),('i46','narrow'),('j29','shadow'),('k58','jpeg-b')]
    positives={'quantized','jpeg-a','gray','typography','jpeg-b'}
    target_map={
        'quantized':['logo_source','logo_proportions'],
        'tagline':['tagline'],
        'jpeg-a':['logo_source','logo_proportions','logo_size'],
        'narrow':['logo_size'],
        'font':['font_family'],
        'gray':['logo_source','logo_clear_space','logo_size'],
        'shadow':['font_effects'],
        'typography':['font_family','font_effects','tagline','marketing_phrases'],
        'space':['logo_clear_space'],
        'jpeg-b':['logo_source','logo_proportions','logo_size'],
    }
    titles=['Clarity in Conversation','Let Every Voice Matter','Better Questions First','Practice a New Skill','Ideas Worth Sharing',
            'Listen, Reflect, Speak','Find Your Speaking Pace','Growing with Feedback','Speak with Confidence','Small Steps, Real Growth']
    if round_number==6:
        titles=['Make Your Ideas Clear','A New Learning Journey','Discover a New Perspective','Listen with Curiosity','Develop Your Own Voice',
                'Learn Something Together','Turn Listening into Action','One Step toward Confidence','Stories Bring Us Together','Build Skills through Practice']
    samples=[];labels={}
    for case_index,(neutral,case) in enumerate(cases):
        ident='r'+str(round_number)+'-'+neutral;folder=output/ident;folder.mkdir()
        width,height=(1000,1500) if round_number==5 else (1200,1600);bg='#772432' if round_number==5 else '#004165'
        image=Image.new('RGB',(width,height),bg);draw=ImageDraw.Draw(image)
        spec=dict(format='tm-poster-brand-check/v2',rule_set='tm-poster-brand-2026-08-v1',context='ordinary-club',document_kind='poster',
            target_width_px=width,print_width_in=8.0,inventory_complete=True,identity=dict(custom_logo=False,custom_theme=False,custom_tagline=False),
            color_formulations=[dict(hex='#772432',rgb=[119,36,50],cmyk=[12,95,59,54],pantone='188')] if round_number==5 else [dict(hex='#004165',rgb=[0,65,101],cmyk=[100,43,12,56],pantone='302')],
            color_regions=[],exclusions=[],layers=[],logos=[],faces=[],text_runs=[],contrast_pairs=[dict(foreground='#FFFFFF',background=bg)])
        occupied=[];render_log=[]

        def add_text(actual,origin,size,role='body',family='Source Sans 3',font_path=None,declared_text=None,declared_font=None,shadow_offset=None,declared_family=None):
            actual_font=font_path or fonts['headline' if role=='headline' else 'body']
            font=ImageFont.truetype(str(actual_font),size);bounds=draw.textbbox(origin,actual,font=font,anchor='lt')
            if shadow_offset:
                dx,dy=shadow_offset;draw.text((origin[0]+dx,origin[1]+dy),actual,font=font,anchor='lt',fill='#101010')
                bounds=(min(bounds[0],bounds[0]+dx),min(bounds[1],bounds[1]+dy),max(bounds[2],bounds[2]+dx),max(bounds[3],bounds[3]+dy))
            draw.text(origin,actual,font=font,anchor='lt',fill='white')
            b=[bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]];lid='run-'+str(len(spec['text_runs']))
            reference=folder/(lid+'.png');image.crop(bounds).save(reference)
            recipe=dict(renderer='Pillow',font_file=str(actual_font),font_sha256=sha(actual_font),font_size_px=size,origin=list(origin),anchor='lt',color='#FFFFFF',background=bg,
                        reference_image=str(reference),reference_sha256=sha(reference),effects=['drop-shadow'] if shadow_offset else [],shadow_offset=list(shadow_offset) if shadow_offset else None)
            render_log.append(dict(id=lid,text=actual,font_family=family,bounds=b,**recipe))
            declared_path=declared_font or actual_font
            run=dict(text=declared_text or actual,bounds=b,role=role,font_role='headline' if role=='headline' else 'body',language='en',script='latin',
                     font_family=declared_family or ('Montserrat' if declared_font else family),font_file=str(declared_path),font_sha256=sha(declared_path),font_size_px=size,origin=list(origin),anchor='lt',
                     color='#FFFFFF',background=bg,effects=[],render_evidence=recipe)
            spec['text_runs'].append(run);spec['layers'].append(dict(id=lid,kind='text',bounds=b));occupied.append(dict(bounds=b,kind='text',reason='Actual rendered text including antialiasing/effects'))
        source=assets/('white.png' if case=='quantized' else 'gray.png' if case=='gray' else 'ti.png')
        original=Image.open(source).convert('RGBA');crop=original.getchannel('A').getbbox();tight=original.crop(crop)
        logo_w=58 if case=='narrow' else 205 if case not in ('jpeg-a','jpeg-b') else 193 if case=='jpeg-a' else 217
        logo_h=round(logo_w*tight.height/tight.width);x,y=(62,15) if case=='space' else (62,96)
        method=Image.Resampling.BILINEAR if case=='jpeg-a' else Image.Resampling.BICUBIC if case=='jpeg-b' else Image.Resampling.LANCZOS
        if round_number==6:
            logo_w=45 if case=='narrow' else 196 if case=='jpeg-a' else 229 if case=='jpeg-b' else 238 if case=='quantized' else 224 if case=='gray' else 216
            logo_h=round(logo_w*tight.height/tight.width);x,y=(86,20) if case=='space' else (86,118)
            method=Image.Resampling.LANCZOS if case=='jpeg-a' else Image.Resampling.BILINEAR if case=='jpeg-b' else Image.Resampling.BICUBIC
        scaled=tight.resize((logo_w,logo_h),method);plate=Image.new('RGBA',scaled.size,bg);plate.alpha_composite(scaled);image.paste(plate.convert('RGB'),(x,y))
        source_x=417 if case=='quantized' else 292 if case=='gray' else 405
        variant='white' if case=='quantized' else 'grayscale' if case=='gray' else 'full-color'
        logo=dict(kind='ti',variant=variant,layer_id='logo',bounds=[x,y,logo_w,logo_h],source=str(source),source_sha256=sha(source),
                  source_bounds=[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]],provenance='https://ccdn.toastmasters.org/content/toastmasters-logo.zip',background=bg,
                  source_wordmark_height_px=source_x,source_wordmark_measurement='Previously independently inspected official alpha-bar span; scaled margin retained without subpixel deficit',
                  effects=[],transform=dict(rotation_deg=0,skew_x_deg=0,skew_y_deg=0,perspective=False))
        spec['logos'].append(logo);spec['layers'].append(dict(id='logo',kind='logo',bounds=logo['bounds']));occupied.append(dict(bounds=logo['bounds'],kind='official-asset',reason='Official source variant artwork'))
        # Different visual hierarchy from the previous centered single-column
        # rounds: logo and short identifying text share the top header; the main
        # title/body begin below, with tagline and invitation in a lower panel.
        left=62 if round_number==5 else 88
        add_text('SPEAKING LAB' if round_number==5 else 'COMMUNICATION STUDIO',(350,112) if round_number==5 else (420,145),38 if round_number==5 else 46,'headline','Montserrat')
        add_text('Practice. Learn. Connect.' if round_number==5 else 'Share ideas. Grow together.',(350,180) if round_number==5 else (420,225),28 if round_number==5 else 32)
        add_text(titles[case_index],(left,440 if round_number==5 else 470),49 if round_number==5 else 57,'headline','Montserrat')
        add_text('A welcoming space to develop your voice.' if round_number==5 else 'Join a supportive community of speakers.',(left,535 if round_number==5 else 590),33 if round_number==5 else 37)
        add_text('Tuesday | 18:45-20:15 | Online' if round_number==5 else 'Wednesday | 19:15-20:45 | Hybrid',(left,605 if round_number==5 else 675),31 if round_number==5 else 35)
        add_text('Prepared speaking and thoughtful feedback' if round_number==5 else 'Practice prepared speeches and give useful feedback.',(left,675 if round_number==5 else 750),30 if round_number==5 else 32)
        if case=='tagline':
            add_text('WHERE LEADERS ARE REMADE' if round_number==5 else 'Where Leaders Are Lost',(left,1080 if round_number==5 else 1170),37 if round_number==5 else 42,'tagline',declared_text='WHERE LEADERS ARE MADE' if round_number==5 else 'Where Leaders Are Made')
        else:
            add_text('WHERE LEADERS ARE MADE' if case=='typography' else 'Where Leaders Are Made',(left,1080 if round_number==5 else 1170),35 if round_number==5 else 39,'tagline')
        add_text('Find your confidence' if round_number==5 else 'Invest in a Brighter Future',(left,1170 if round_number==5 else 1270),35 if round_number==5 else 38,'marketing-phrase')
        if case=='font':
            if round_number==5:
                add_text('Stories open possibilities',(62,830),42,'headline','DejaVu Serif',assets/'DejaVuSerif.ttf',declared_font=fonts['headline'])
            else:
                add_text('Every speech is a chance to practice.',(left,920),36,'body','Montserrat',fonts['headline'],declared_font=fonts['body'],declared_family='Source Sans 3')
        elif case=='shadow':
            add_text('Share a story. Start a conversation.' if round_number==5 else 'A clear voice makes a difference.',(left,830 if round_number==5 else 920),40 if round_number==5 else 46,'headline','Montserrat',shadow_offset=(7,6) if round_number==5 else (9,4))
        elif case=='typography':
            add_text('Build a lasting habit' if round_number==5 else 'Your next idea starts here',(left,825 if round_number==5 else 915),40 if round_number==5 else 46,'headline','Montserrat')
            add_text('Your next speech begins with one idea.' if round_number==5 else 'Try one new skill at your next meeting.',(left,905 if round_number==5 else 1010),30 if round_number==5 else 34)
        xs=sorted({0,width}|{v for e in occupied for v in (e['bounds'][0],e['bounds'][0]+e['bounds'][2])});ys=sorted({0,height}|{v for e in occupied for v in (e['bounds'][1],e['bounds'][1]+e['bounds'][3])})
        for x0,x1 in zip(xs,xs[1:]):
            for y0,y1 in zip(ys,ys[1:]):
                if not any(max(x0,e['bounds'][0])<min(x1,e['bounds'][0]+e['bounds'][2]) and max(y0,e['bounds'][1])<min(y1,e['bounds'][1]+e['bounds'][3]) for e in occupied):
                    spec['color_regions'].append(dict(bounds=[x0,y0,x1-x0,y1-y0],mode='solid',color=bg,tolerance=1))
        spec['exclusions']=occupied
        log=folder/'renderer-log.json';write(log,dict(renderer='Pillow',canvas=[width,height],background=bg,text_runs=render_log,
                    logo_render=dict(source=str(source),source_crop=list(crop),bounds=logo['bounds'],resampling=int(method))))
        for run in spec['text_runs']:run['render_evidence']['source_artifact']=str(log)
        path=folder/('poster.jpg' if case in ('jpeg-a','jpeg-b') else 'poster.png')
        if case=='jpeg-a':image.save(path,quality=52 if round_number==5 else 79,subsampling=2 if round_number==5 else 0)
        elif case=='jpeg-b':image.save(path,quality=88 if round_number==5 else 58,subsampling=0 if round_number==5 else 2)
        elif case=='quantized' and round_number==5:image.quantize(colors=256,method=Image.Quantize.MEDIANCUT).save(path)
        elif case=='quantized':image.save(path,optimize=True)
        else:image.save(path)
        spec['candidate_sha256']=sha(path);spec_path=folder/'spec.json';write(spec_path,spec)
        selectors={key:dict(logo=0) for key in target_map[case] if key.startswith('logo_')}
        samples.append(dict(id=ident,image=str(path),spec=str(spec_path),target_checks=target_map[case],target_selectors=selectors,
            evidence=dict(renderer_log=str(log),logo_source=str(source),source_url='https://ccdn.toastmasters.org/content/toastmasters-logo.zip',manual_path=str(assets/'manual.pdf')),
            scope='Listed objective features with selected applicable entities and actual image/source evidence; not whole-brand or release approval'))
        labels[ident]=dict(intended='positive' if case in positives else 'negative',construction=case,checks=target_map[case])
    if len({sha(s['image']) for s in samples})!=10:raise ValueError('Require ten unique image stimuli')
    write(output/'manifest.json',dict(round=round_number,manual=dict(path=str(assets/'manual.pdf'),url='https://content.toastmasters.org/image/upload/02330-001-0001-brand-manual.pdf',sha256=sha(assets/'manual.pdf')),samples=samples))
    write(output/'intended-labels-private.json',labels)
    sheet=Image.new('RGB',(1500,820),'#CCCCCC')
    for i,s in enumerate(samples):
        im=Image.open(s['image']).convert('RGB');im.thumbnail((260,370));tile=Image.new('RGB',(300,410),'white');tile.paste(im,((300-im.width)//2,10));ImageDraw.Draw(tile).text((10,390),s['id'],fill='black');sheet.paste(tile,((i%5)*300,(i//5)*410))
    sheet.save(output/'contact-sheet.jpg');write(output/'sha256-inventory.json',{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--round',dest='round_number',type=int,choices=(5,6),default=5)
    args=parser.parse_args();build(args.assets.resolve(),args.output.resolve(),args.round_number)
