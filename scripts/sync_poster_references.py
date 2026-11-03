#!/usr/bin/env python3
"""Bundle canonical poster references for independently installable skills."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
# Poster production packages are retired; retain the official-link index only.
SKILLS=()


def materials_index(sources):
    sections = [
        '# Toastmasters poster materials | 头马海报素材',
        '',
        'Start here; you do not need to reopen the Brand Manual or run a script to find materials. Use existing [local files](local/) first, or click an official link below and download with your browser. The poster maker and reviewer are retired; use official resources and templates for brand guidance.',
        '',
        '从这里开始，无须重新打开品牌手册，也无须执行脚本查找素材。优先使用已有[本地文件](local/)，或点击下方官方链接通过浏览器下载。海报制作与评审技能已退役；品牌指导请使用官方资源与模板。',
        '',
        'The local folder is private and Git-ignored; it may be absent in a fresh clone. This repository saves the complete [URL catalog](sources.json), source pages, inspection status, formats and checksums. Original Toastmasters assets are not covered by the repository MIT license and are not publicly rehosted here.',
        '',
        '本地目录保持私有并被 Git 忽略，新克隆可能没有本地文件。仓库保存完整[链接目录](sources.json)、来源页码、检查状态、格式及校验值。官方素材不适用仓库 MIT 许可，不在此公开重托管。',
        '',
        'Baseline / 基准: '+sources['baseline']+'. This index and sources.json are generated from the canonical source inventory; run `python3 scripts/sync_poster_references.py` from the repository root after changing it.',
        '',
    ]
    groups = [('poster-asset','Logos, badges and photographs | 标志、徽章与照片'),('font-source','Fonts | 字体'),('supporting-guidance','Photography guidance | 摄影指南'),('baseline-manual','Manual for rule updates | 规则更新时查阅的手册'),('permissions-or-discovery','Permissions and official resources | 许可与官方资源'),('outside-poster-scope','Other links from the manual | 手册中的其他链接')]
    for kind, heading in groups:
        sections.extend(['## '+heading,'','| Material / 素材 | Official link / 官方链接 | Formats / 格式 | Manual page / 手册页码 |','|---|---|---|---|'])
        for item in sources['links']:
            if item['kind'] == kind:
                sections.append('| '+item['id']+' | [Open / 打开]('+item['url']+') | '+', '.join(item.get('formats',[]))+' | '+', '.join(map(str,item['manual_pages']))+' |')
        sections.append('')
    sections.extend(['## Local reuse and optional tools | 本地复用与可选工具','','Already downloaded originals can be stored under `local/<asset-id>/`; keep an inventory of source URLs, filenames and hashes in `local/inventory.json`. Do not download again when suitable verified local files already exist. Provided assets and ordinary browser downloads are also supported.','','已下载原件可放在`local/<asset-id>/`，并在`local/inventory.json`记录来源链接、文件名及哈希。有合适且已核实的本地文件时不要重复下载；用户提供的素材和普通浏览器下载同样可用。','','The photo archive is about 503 MB. Reuse authorized local files or obtain the needed assets through the official links; downloading the entire archive is unnecessary. Font links are official source pages; obtain actual font files and their licenses rather than treating HTML as installed fonts. The Brand Portal may require sign-in.','','照片压缩包约503 MB，可复用有权使用的本地文件，或从官方链接获取所需素材，不必下载整个包。字体链接是官方来源页面，需取得实际字体及许可，不能把网页当作已安装字体。品牌门户可能需要登录。','','Canonical inventory / 规范来源目录: [asset-sources.json](../../references/toastmasters-brand/asset-sources.json).',''])
    return '\n'.join(sections)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    mismatches=[]
    canonical = ROOT/'references/toastmasters-brand/asset-sources.json'
    material_dir = ROOT/'materials/toastmasters-brand'
    material_outputs = {
        material_dir/'sources.json': canonical.read_bytes(),
        material_dir/'README.md': materials_index(json.loads(canonical.read_text())).encode('utf-8'),
    }
    for target, content in material_outputs.items():
        if args.check:
            if not target.exists() or target.read_bytes()!=content:
                mismatches.append(str(target.relative_to(ROOT)))
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(content)
    for source in sorted((ROOT/'references/toastmasters-brand').glob('*')):
        if source.suffix not in {'.md','.json'}: continue
        for skill in SKILLS:
            target=ROOT/'skills'/skill/'references'/source.name
            if args.check:
                if not target.exists() or target.read_bytes()!=source.read_bytes(): mismatches.append(str(target.relative_to(ROOT)))
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(source.read_bytes())
    if mismatches:
        print('Out-of-sync references: '+', '.join(mismatches))
        return 1
    print('Poster reference bundles synchronized' if not args.check else 'Poster reference bundles match canonical sources')
    return 0

if __name__=='__main__': raise SystemExit(main())
