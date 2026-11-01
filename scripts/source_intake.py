#!/usr/bin/env python3
"""Review-first source metadata intake. Never stores article bodies or abstracts."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / 'config' / 'source_registry.json'
ATOM = '{http://www.w3.org/2005/Atom}'
MAX_BYTES = 1_000_000


def https_host(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port or p.fragment:
        raise ValueError('Only plain HTTPS URLs without credentials/ports/fragments are allowed')
    return p.hostname.lower()


def validate(catalog, domain_ids):
    if set(catalog) != {'schema_version','publication_policy','sources','feeds','candidates'}:
        raise ValueError('Unexpected source registry layout')
    if catalog['schema_version'] != 1 or catalog['publication_policy'] != 'public_links_and_metadata_only':
        raise ValueError('Unsupported source registry version or policy')
    if not all(isinstance(catalog[k],list) for k in ('sources','feeds','candidates')):
        raise ValueError('Expected lists')
    ids, urls = set(), set()
    for entry in catalog['sources']:
        if set(entry) != {'id','domain','title','url','type','review'} or entry['review'] != 'source_verified':
            raise ValueError('Invalid reviewed source entry')
        if not all(isinstance(entry[k],str) and entry[k].strip() for k in entry):
            raise ValueError('Empty source field')
        if entry['id'] in ids or entry['url'] in urls: raise ValueError('Duplicate source')
        if entry['domain'] not in domain_ids: raise ValueError('Unknown source domain')
        https_host(entry['url']); ids.add(entry['id']); urls.add(entry['url'])
    feed_ids = set()
    for feed in catalog['feeds']:
        if set(feed) != {'id','domain','url','allowed_host','link_host','limit'}:
            raise ValueError('Invalid feed structure')
        if feed['id'] in feed_ids or feed['domain'] not in domain_ids: raise ValueError('Invalid feed ID or domain')
        if not isinstance(feed['limit'],int) or not 1 <= feed['limit'] <= 10:
            raise ValueError('Feed size must be 1..10')
        if https_host(feed['url']) != feed['allowed_host']:
            raise ValueError('Feed host mismatch')
        if not re.fullmatch(r'[a-z0-9.-]+',feed['link_host']): raise ValueError('Invalid link host')
        feed_ids.add(feed['id'])
    for entry in catalog['candidates']:
        if set(entry) != {'id','domain','feed_id','title','url','published','review'} or entry['review'] != 'unreviewed':
            raise ValueError('Invalid unreviewed candidate entry')
        if not all(isinstance(entry[k],str) for k in entry): raise ValueError('Invalid candidate field')
        if entry['domain'] not in domain_ids or entry['feed_id'] not in feed_ids:
            raise ValueError('Unknown candidate domain or feed')
        if not entry['title'] or len(entry['title']) > 160: raise ValueError('Invalid candidate title')
        feed = next(f for f in catalog['feeds'] if f['id'] == entry['feed_id'])
        if https_host(entry['url']) != feed['link_host']:
            raise ValueError('Candidate URL host is not allowed')
        if entry['id'] != hashlib.sha256(entry['url'].encode('utf-8')).hexdigest()[:16]:
            raise ValueError('Candidate ID mismatch')
        if entry['id'] in ids or entry['url'] in urls: raise ValueError('Duplicate candidate')
        ids.add(entry['id']); urls.add(entry['url'])
    return catalog


def collect_feed(feed, fetch=None):
    if fetch is None:
        def fetch(url):
            req = urllib.request.Request(url, headers={'User-Agent': 'UniversalKnowledgeLab/0.4 (public metadata intake)'})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw = response.read(MAX_BYTES+1)
                if len(raw) > MAX_BYTES: raise ValueError('Feed too large')
                return raw
    data = fetch(feed['url'])
    if len(data) > MAX_BYTES: raise ValueError('Feed too large')
    root = ET.fromstring(data)
    if root.tag != ATOM+'feed': raise ValueError('Only Atom feeds are supported')
    result = []
    for item in root.findall(ATOM+'entry'):
        link = next((x.get('href') for x in item.findall(ATOM+'link') if x.get('rel','alternate') == 'alternate'),None)
        if not link or https_host(link) != feed['link_host']: continue
        title = ' '.join((item.findtext(ATOM+'title') or '').split())[:160]
        if not title: continue
        published = item.findtext(ATOM+'published') or item.findtext(ATOM+'updated') or ''
        result.append({'id':hashlib.sha256(link.encode('utf-8')).hexdigest()[:16],
                       'domain':feed['domain'], 'feed_id':feed['id'], 'title':title,
                       'url':link, 'published':published, 'review':'unreviewed'})
        if len(result) >= feed['limit']: break
    return result


def intake(catalog, fetch=None):
    existing_urls = {x['url'] for x in catalog['sources']+catalog['candidates']}
    errors = []
    success = 0
    for feed in catalog['feeds']:
        try:
            records = collect_feed(feed,fetch)
            success += 1
            for record in records:
                if record['url'] not in existing_urls:
                    catalog['candidates'].append(record)
                    existing_urls.add(record['url'])
        except (OSError,ValueError,ET.ParseError) as exc:
            errors.append(f'{feed["id"]}: {exc}')
    if success == 0:
        raise RuntimeError('All feeds failed: '+'; '.join(errors))
    catalog['candidates'].sort(key=lambda x: (x['domain'],x['feed_id'],x['url']))
    for err in errors: print('WARNING:',err,file=sys.stderr)
    return catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--online',action='store_true',help='Fetch configured Atom feeds (normally runs in Actions)')
    args = parser.parse_args()
    catalog = json.loads(FILE.read_text(encoding='utf-8'))
    domain_ids = {x['id'] for x in json.loads((ROOT/'config/domain_registry.json').read_text(encoding='utf-8'))['domains']}
    validate(catalog,domain_ids)
    if args.online:
        intake(catalog)
        validate(catalog,domain_ids)
        FILE.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(catalog["sources"])} reviewed source URLs; {len(catalog["candidates"])} candidates')

if __name__ == '__main__': main()
