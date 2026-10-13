#!/usr/bin/env python3
"""Explicit local downloads; preserve baselines and quarantine changed versions.

No extraction or installation is performed. Downloads are never evidence of a
license. Use --id repeatedly; no IDs means list sources without network access.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import time
import urllib.request
import zipfile


class RangeZip(io.RawIOBase):
    """Seekable reader for selected members of large HTTP archives."""
    def __init__(self, size, read_range, max_bytes=150*1024*1024):
        self.size, self.read_range, self.position = size, read_range, 0
        self.max_bytes, self.bytes_read = max_bytes, 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if whence not in (0, 1, 2) or position < 0:
            raise ValueError('Invalid seek')
        self.position = position
        return position

    def read(self, size=-1):
        count = max(0, self.size - self.position) if size < 0 else min(size, max(0, self.size-self.position))
        if count > 32*1024*1024:
            raise ValueError('Range read exceeds 32 MiB; use a full archive download for larger members')
        if self.bytes_read + count > self.max_bytes:
            raise ValueError('Aggregate archive reads exceed byte budget')
        if not count:
            return b''
        data = self.read_range(self.position, count)
        if len(data) != count:
            raise ValueError('Incomplete archive range')
        self.position += count
        self.bytes_read += count
        return data


def open_remote_zip(url, max_bytes=150*1024*1024, deadline_seconds=60):
    deadline = time.monotonic() + deadline_seconds
    def remaining():
        value = deadline - time.monotonic()
        if value <= 0:
            raise TimeoutError('Selective archive access exceeded time budget')
        return min(15, value)
    with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=remaining()) as response:
        size = int(response.headers['Content-Length'])
    def read_range(start, count):
        request = urllib.request.Request(url, headers={'Range':f'bytes={start}-{start+count-1}'})
        with urllib.request.urlopen(request, timeout=remaining()) as response:
            expected = f'bytes {start}-{start+count-1}/{size}'
            if response.status != 206 or response.headers.get('Content-Range') != expected:
                raise ValueError('Source does not honor precise HTTP range requests')
            data = bytearray()
            while len(data) < count:
                remaining()
                chunk = response.read(min(65536, count-len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            remaining()
            return bytes(data)
    return zipfile.ZipFile(RangeZip(size, read_range, max_bytes=max_bytes)), size


def usable_members(archive):
    files = []
    for item in archive.infolist():
        path = PurePosixPath(item.filename)
        if path.is_absolute() or '..' in path.parts or '\\' in item.filename:
            raise ValueError('Unsafe archive member: ' + item.filename)
        if item.is_dir() or '__MACOSX' in path.parts or path.name in {'.DS_Store', 'Thumbs.db'} or path.name.startswith('._'):
            continue
        files.append(item.filename)
    return files


def archive_files(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return usable_members(archive)


def store_download(root, asset_id, url, data, expected_sha256=None):
    if not asset_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in asset_id):
        raise ValueError('Invalid asset ID')
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    manifest = root / (asset_id + '.json')
    previous = json.loads(manifest.read_text()) if manifest.exists() else None
    result = {'id':asset_id, 'url':url, 'retrieved_at':datetime.now(timezone.utc).isoformat(),
              'sha256':digest, 'bytes':len(data), 'redistribution':'Not established; private cache only.'}
    suffix = PurePosixPath(url.split('?', 1)[0]).suffix or '.html'
    baseline_digest = previous['sha256'] if previous else expected_sha256
    if (baseline_digest and baseline_digest != digest) or (previous and previous['url'] != url):
        candidate = root / (asset_id + '.candidate-' + digest[:16] + suffix)
        candidate.write_bytes(data)
        result.update(status='changed-review-required', path=previous['path'] if previous else None, candidate_path=str(candidate.resolve()), baseline_sha256=baseline_digest)
        (root / (asset_id + '.change.json')).write_text(json.dumps(result, indent=2)+'\n')
    else:
        target = root / (asset_id + suffix)
        target.write_bytes(data)
        result.update(status='unchanged' if previous else 'downloaded', path=str(target.resolve()))
        manifest.write_text(json.dumps(result, indent=2)+'\n')
    return result


def fetch(url, max_bytes=150*1024*1024, deadline_seconds=60):
    start=time.monotonic()
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'D85-Brand-Asset-Inspector/1.0'}), timeout=15) as response:
        final_url=response.url
        if 'login.toastmasters.org' in final_url:
            raise PermissionError('Official source requires sign-in; use an authorized browser session or supplied file.')
        data=bytearray()
        while True:
            if time.monotonic()-start > deadline_seconds: raise TimeoutError('Download exceeded time budget')
            chunk=response.read(65536)
            if not chunk: break
            data.extend(chunk)
            if len(data)>max_bytes: raise ValueError('Download exceeded size limit')
        return bytes(data), final_url, response.headers.get('Content-Type','')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', action='append', default=[])
    parser.add_argument('--cache', type=Path, default=Path.home()/'.cache/d85-toastmasters-brand')
    parser.add_argument('--list-members', action='store_true', help='Inspect a large ZIP using range reads')
    parser.add_argument('--member', action='append', default=[], help='Fetch an exact ZIP member, not the whole archive')
    parser.add_argument('--deadline-seconds', type=int, default=60)
    parser.add_argument('--max-mib', type=int, default=150)
    args=parser.parse_args()
    sources=json.loads((Path(__file__).resolve().parents[1]/'references/asset-sources.json').read_text())['links']
    by_id={x['id']:x for x in sources}
    if not args.id:
        if args.list_members or args.member:
            parser.error('Selective archive access requires a ZIP source ID')
        for item in sources: print(item['id'], item['kind'], item['url'])
        return 0
    unknown=set(args.id)-set(by_id)
    if unknown: parser.error('Unknown IDs: '+', '.join(sorted(unknown)))
    if (args.list_members or args.member) and (len(args.id) != 1 or not by_id[args.id[0]]['url'].endswith('.zip')):
        parser.error('Selective archive access requires exactly one ZIP source ID')
    if args.deadline_seconds <= 0 or args.max_mib <= 0:
        parser.error('Download limits must be positive')
    failed=False
    for asset_id in args.id:
        source=by_id[asset_id]
        try:
            if args.list_members or args.member:
                archive, archive_size = open_remote_zip(source['url'],max_bytes=args.max_mib*1024*1024,deadline_seconds=args.deadline_seconds)
                with archive:
                    members = usable_members(archive)
                    missing = set(args.member)-set(members)
                    if missing: raise ValueError('Unknown/non-usable archive member: '+', '.join(sorted(missing)))
                    result = {'id':asset_id,'url':source['url'],'status':'range-inspected','archive_bytes':archive_size,'files':members,'full_archive_sha256':None,'retrieved_at':datetime.now(timezone.utc).isoformat(),'selected_members':[],'redistribution':'Not established; private cache only.'}
                    output_bytes = 0
                    for member in args.member:
                        info = archive.getinfo(member)
                        if info.file_size > 32*1024*1024: raise ValueError('Selected member exceeds 32 MiB')
                        output_bytes += info.file_size
                        if output_bytes > args.max_mib*1024*1024:
                            raise ValueError('Selected output exceeds aggregate byte budget')
                        data = archive.read(member)
                        member_id = asset_id+'-member-'+hashlib.sha256(member.encode()).hexdigest()[:16]
                        expected = next((x['sha256'] for x in source.get('selected_members', []) if x['member'] == member), None)
                        saved = store_download(args.cache,member_id,source['url']+'#'+member,data,expected_sha256=expected)
                        saved['archive_url'] = source['url']
                        saved['member'] = member
                        saved['format'] = PurePosixPath(member).suffix.lstrip('.')
                        result['selected_members'].append(saved)
                        if saved['status'] == 'changed-review-required':
                            result['status'] = 'changed-review-required'
                args.cache.mkdir(parents=True,exist_ok=True)
                (args.cache/(asset_id+'.range-inspection.json')).write_text(json.dumps(result,indent=2)+'\n')
                print(json.dumps(result),flush=True)
                continue
            data, resolved, content_type=fetch(source['url'],max_bytes=args.max_mib*1024*1024,deadline_seconds=args.deadline_seconds)
            members=archive_files(data) if source['url'].endswith('.zip') else []
            if source['url'].endswith('.pdf') and not data.startswith(b'%PDF-'): raise ValueError('Expected PDF, got another format')
            result=store_download(args.cache,asset_id,source['url'],data,expected_sha256=source.get('sha256'))
            result.update(resolved_url=resolved,content_type=content_type,files=members,formats=sorted({PurePosixPath(x).suffix.lstrip('.') for x in members}) or [content_type])
            if asset_id=='brand-manual':
                result['version_check']='Compare cover revision with Version 2.0 Rev. 08/2026; changed checksum requires review, never automatic rule replacement.'
            (args.cache/(asset_id+'.inspection.json')).write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps(result),flush=True)
        except Exception as exc:
            failed=True
            args.cache.mkdir(parents=True,exist_ok=True)
            result={'id':asset_id,'url':source['url'],'status':'unavailable','retrieved_at':datetime.now(timezone.utc).isoformat(),'error':str(exc)}
            (args.cache/(asset_id+'.failure.json')).write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps(result),flush=True)
    return 1 if failed else 0

if __name__=='__main__': raise SystemExit(main())
