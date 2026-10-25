"""Separate unscored capability controls; never count these as wrong posters."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(assets,output,cjk_font):
    if output.exists() and any(output.iterdir()):raise ValueError('Fresh output directory required')
    output.mkdir(parents=True,exist_ok=True)
    samples=[]
    for ident in ('control-a','control-b'):
        folder=output/ident;folder.mkdir();image=Image.new('RGB',(600,800),'#004165')
        spec=dict(format='tm-poster-brand-check/v2',rule_set='tm-poster-brand-2026-08-v1',context='ordinary-club',document_kind='poster',
            target_width_px=600,inventory_complete=True,identity=dict(custom_logo=False,custom_theme=False,custom_tagline=False),
            color_formulations=[],color_regions=[],exclusions=[],layers=[],logos=[],faces=[],text_runs=[],contrast_pairs=[])
        if ident=='control-a':
            # Actual Han glyphs and original font artifact, no invented Chinese
            # approved-font whitelist. This is an uncertainty/capability probe.
            local=folder/'cjk-source.ttc';local.write_bytes(cjk_font.read_bytes())
            font=ImageFont.truetype(str(local),48,index=2);draw=ImageDraw.Draw(image)
            origin=(50,200);value='沟通与领导力';box=draw.textbbox(origin,value,font=font,anchor='lt');draw.text(origin,value,font=font,anchor='lt',fill='white')
            bounds=[box[0],box[1],box[2]-box[0],box[3]-box[1]]
            reference=folder/'glyphs.png';image.crop(box).save(reference)
            recipe=dict(renderer='Pillow',font_file=str(local),font_sha256=sha(local),font_index=2,font_size_px=48,origin=list(origin),anchor='lt',color='#FFFFFF',background='#004165',reference_image=str(reference),reference_sha256=sha(reference),effects=[])
            log=folder/'renderer-log.json';write(log,dict(text_runs=[dict(text=value,font_family='Noto Sans CJK SC',bounds=bounds,**recipe)]))
            recipe['source_artifact']=str(log)
            spec['text_runs']=[dict(text=value,bounds=bounds,role='headline',font_role='headline',font_family='Noto Sans CJK SC',script='han',language='zh',effects=[],render_evidence=recipe,font_file=str(local),font_sha256=sha(local),font_index=2)]
            spec['layers']=[dict(id='text',kind='text',bounds=bounds)];spec['exclusions']=[dict(bounds=bounds,kind='text',reason='Actual Han text')]
            spec['color_regions']=[dict(bounds=[0,0,600,190],color='#004165')]
            targets=['font_family']
        else:
            for y in range(800):
                for x in range(600):
                    t=(x+y)/(599+799);image.putpixel((x,y),tuple(round(a+(b-a)*t) for a,b in zip((0,65,101),(0,96,148))))
            spec['color_regions']=[dict(bounds=[0,0,600,800],mode='gradient',colors=['#004165','#006094'],geometry='diagonal',tolerance=1)]
            targets=['gradient']
        path=folder/'poster.png';image.save(path);spec['candidate_sha256']=sha(path)
        spec_path=folder/'spec.json';write(spec_path,spec)
        samples.append(dict(id=ident,image=str(path),spec=str(spec_path),target_checks=targets,
            scope='Supplementary uncertainty/capability control; excluded from five-positive/five-negative round counts',
            evidence=dict(manual_path=str(assets/'manual.pdf'))))
    write(output/'manifest.json',dict(round='supplemental-uncertainty',samples=samples))
    write(output/'sha256-inventory.json',{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assets',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--cjk-font',type=Path,required=True)
    args=parser.parse_args();build(args.assets.resolve(),args.output.resolve(),args.cjk_font.resolve())
