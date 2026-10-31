"""Install a checked KotobaFlow resource profile without copying private content."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
FORBIDDEN = re.compile(r'XinBian|新编|新編|(?:^|/)(?:user_progress|credentials?|secrets?|private|backup)(?:[._/]|$)|\.(?:apk|jks|keystore|pem|key|log|bak|wav)$', re.I)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def safe_resource_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not isinstance(value, str) or '\\' in value or path.is_absolute() or any(part in {'', '.', '..'} or part.startswith('.') for part in value.split('/')) or path.parts[0] not in {'data', 'image'} or FORBIDDEN.search(value):
        raise ValueError('Forbidden resource path: ' + str(value))
    return path


def load_profile(profile: str) -> dict:
    if profile not in {'web-2026-10-31', 'web-2026-10-31-r2', 'android-0.4.2'}:
        raise ValueError('Unknown resource profile')
    manifest = json.loads((ROOT / 'profiles' / profile / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['schema'] != 1 or manifest['profile'] != profile:
        raise ValueError('Invalid profile manifest')
    seen = set()
    for entry in manifest['files']:
        safe_resource_path(entry['path'])
        if entry['path'] in seen or not re.fullmatch('[a-f0-9]{64}', entry['sha256']) or entry['storage'] not in {'git', 'release'} or not isinstance(entry['bytes'], int) or entry['bytes'] < 1:
            raise ValueError('Invalid resource entry: ' + entry['path'])
        seen.add(entry['path'])
    return manifest


def checked_destination(root: Path, relative: str) -> Path:
    rel = safe_resource_path(relative)
    for parent in [root, *[root.joinpath(*rel.parts[:i]) for i in range(1, len(rel.parts) + 1)]]:
        if parent.is_symlink() or parent.is_junction():
            raise ValueError('Refusing linked destination: ' + str(parent))
    target = root.joinpath(*rel.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Destination escapes requested root')
    return target


def verify_git_files(manifest: dict) -> int:
    count = 0
    base = ROOT / 'profiles' / manifest['profile'] / 'files'
    for entry in manifest['files']:
        if entry['storage'] == 'git':
            source = checked_destination(base, entry['path'])
            if source.stat().st_size != entry['bytes'] or digest(source) != entry['sha256']:
                raise ValueError('Resource mismatch: ' + entry['path'])
            count += 1
    return count


def checked_archive(path: Path, release: dict) -> zipfile.ZipFile:
    if path.stat().st_size != release['bytes'] or digest(path) != release['sha256']:
        raise ValueError('Media archive size or SHA-256 mismatch')
    archive = zipfile.ZipFile(path)
    if len(archive.namelist()) != len(set(archive.namelist())):
        archive.close()
        raise ValueError('Duplicate archive entry')
    if any(not re.fullmatch(r'objects/[a-f0-9]{64}', name) for name in archive.namelist()):
        archive.close()
        raise ValueError('Unexpected archive path')
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, choices=['web-2026-10-31', 'web-2026-10-31-r2', 'android-0.4.2'])
    parser.add_argument('--target', type=Path)
    parser.add_argument('--media-archive', type=Path)
    parser.add_argument('--metadata-only', action='store_true')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--configure-public', action='store_true', help='Offer the four public books in the target source configuration')
    args = parser.parse_args()
    manifest = load_profile(args.profile)
    text_count = verify_git_files(manifest)
    if not args.verify_only and args.target is None:
        parser.error('--target is required to install resources')
    target = args.target.absolute() if args.target else None
    if target is not None:
        if target.is_symlink() or target.is_junction():
            raise ValueError('Refusing a linked target root')
        for entry in manifest['files']:
            checked_destination(target, entry['path'])
    release = json.loads((ROOT / 'media-release.json').read_text(encoding='utf-8'))
    archive = None
    if not args.metadata_only:
        archive_path = args.media_archive
        if archive_path is None:
            cache = ROOT / '.downloads'
            cache.mkdir(exist_ok=True)
            archive_path = cache / release['filename']
            if not archive_path.exists():
                url = release['url']
                if not url.startswith('https://github.com/greyindex/kotobaflow-resources/releases/download/'):
                    raise ValueError('Unexpected media download origin')
                print('Downloading checked media archive:', url, flush=True)
                partial = archive_path.with_suffix('.partial')
                urllib.request.urlretrieve(url, partial)
                if partial.stat().st_size != release['bytes'] or digest(partial) != release['sha256']:
                    raise ValueError('Downloaded media archive mismatch')
                partial.replace(archive_path)
        archive = checked_archive(archive_path, release)
    media_count = 0
    try:
        for entry in manifest['files']:
            if entry['storage'] == 'release':
                if archive is None:
                    continue
                body = archive.read('objects/' + entry['sha256'])
                if len(body) != entry['bytes'] or hashlib.sha256(body).hexdigest() != entry['sha256']:
                    raise ValueError('Media object mismatch: ' + entry['path'])
                media_count += 1
            else:
                body = (ROOT / 'profiles' / args.profile / 'files' / entry['path']).read_bytes()
            if target is not None and not args.verify_only:
                destination = checked_destination(target, entry['path'])
                if destination.exists() and digest(destination) == entry['sha256']:
                    continue
                if destination.exists():
                    raise ValueError('Existing different resource; choose a fresh source checkout: ' + str(destination))
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(body)
    finally:
        if archive is not None:
            archive.close()
    if args.configure_public and not args.verify_only:
        config = target / 'js' / 'content-config.js'
        if config.is_symlink() or config.is_junction():
            raise ValueError('Refusing linked configuration')
        text = config.read_text(encoding='utf-8')
        replacement = 'var offered = ["KotobaFlow1","KotobaFlow2","KotobaFlow3","KotobaFlow4"]; // public resources'
        changed, count = re.subn(r'var offered = null;[^\n]*', replacement, text)
        if count != 1:
            if not re.search(r'var offered = \["KotobaFlow1","KotobaFlow2","KotobaFlow3","KotobaFlow4"\]', text):
                raise ValueError('Unexpected content configuration; configure the four public books manually')
        elif changed != text:
            config.write_bytes(changed.encode('utf-8'))
        print('Public four-book content configuration ready')
    print(json.dumps({'profile':args.profile, 'metadata_files_verified':text_count, 'media_files_verified':media_count, 'installed':not args.verify_only, 'metadata_only':args.metadata_only}))


if __name__ == '__main__':
    main()
