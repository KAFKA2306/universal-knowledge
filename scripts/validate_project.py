#!/usr/bin/env python3
"""Offline schema-oriented validation; intentionally uses Python stdlib only."""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ukl import CORE_ACTIONS, load_settings

HIGH_REVIEW = {'manufacturing_process', 'semiconductor_capex', 'equity_research', 'scientific_intelligence', 'software_factory', 'local_ai_agents', 'security_posture', 'career_intelligence'}
TIER_VALUES = {'core', 'active'}
REPO_RE = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')


def validate() -> list[str]:
    errors = []
    p = ROOT / 'config' / 'pipeline.json'
    try:
        config = load_settings(p)
        if config['default_domain'] not in {x.stem for x in (ROOT / 'domain_packs').glob('*.json')}:
            errors.append('default_domain is missing')
    except (ValueError, OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        errors.append(f'{p}: {e}')
    for schema_path in sorted((ROOT / 'schemas').glob('*.json')):
        try:
            json.loads(schema_path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as e:
            errors.append(f'{schema_path.name}: invalid schema JSON: {e}')
    paths = sorted((ROOT / 'domain_packs').glob('*.json'))
    if not paths: errors.append('No domain packs defined')
    for p in paths:
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
            if set(d) != {'id','version','description','actions','requires_review'}: raise ValueError('Unexpected or missing keys')
            if d['id'] != p.stem or not re.fullmatch(r'[a-z][a-z0-9_-]*', d['id']): raise ValueError('Invalid domain ID')
            if not re.fullmatch(r'\d+\.\d+\.\d+', d['version']): raise ValueError('Version must be semver X.Y.Z')
            if not isinstance(d['description'],str) or not d['description'].strip(): raise ValueError('Empty description')
            if not isinstance(d['requires_review'],bool): raise ValueError('requires_review must be boolean')
            if not isinstance(d['actions'],dict) or not d['actions']: raise ValueError('No actions')
            if set(d['actions']) & set(CORE_ACTIONS): raise ValueError('Cannot redefine core actions')
            for k, v in d['actions'].items():
                if not isinstance(k,str) or not re.fullmatch(r'[a-z][a-z0-9_]*',k): raise ValueError('Invalid action label')
                if not isinstance(v,str) or len(v.strip()) < 5 or ' in ' in v: raise ValueError(f'Invalid action definition: {k}')
            if d['id'] in HIGH_REVIEW and not d['requires_review']:
                raise ValueError('High-stakes domain must require review')
        except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as e:
            errors.append(f'{p.name}: {e}')
    # The domain registry is the canonical routing / prioritization plan. It must
    # reference exactly the same IDs as the versioned domain packs.
    try:
        registry = json.loads((ROOT / 'config' / 'domain_registry.json').read_text(encoding='utf-8'))
        if set(registry) != {'schema_version', 'mission', 'release_data_policy', 'routing_policy', 'domains'}:
            raise ValueError('Unexpected registry layout')
        if registry['schema_version'] != '1' or registry['release_data_policy'] != 'public_config_and_synthetic_examples_only':
            raise ValueError('Unsupported registry policy')
        if registry['routing_policy'] != 'manual_or_configured_default_no_auto_detection':
            raise ValueError('Domain selection cannot silently auto-route')
        if not isinstance(registry['mission'], str) or not registry['mission'].strip():
            raise ValueError('Registry mission is required')
        if not isinstance(registry['domains'], list):
            raise ValueError('Registry domains must be a list')
        registry_ids = []
        for item in registry['domains']:
            if not isinstance(item, dict) or set(item) != {'id','tier','goal','routes','sources','public_repos','links','guardrails'}:
                raise ValueError('Unexpected domain registry entry')
            id_ = item['id']
            if not isinstance(id_, str):
                raise ValueError('Invalid registry ID')
            registry_ids.append(id_)
            if item['tier'] not in TIER_VALUES:
                raise ValueError(f'Unknown domain tier: {id_}')
            if not isinstance(item['goal'], str) or not item['goal'].strip():
                raise ValueError(f'Missing goal: {id_}')
            for key in ('routes','sources','guardrails'):
                values = item[key]
                if not isinstance(values, list) or not values or any(not isinstance(v,str) or not v.strip() for v in values):
                    raise ValueError(f'Invalid {key}: {id_}')
            if not isinstance(item['public_repos'],list) or any(not isinstance(v,str) or not REPO_RE.fullmatch(v) for v in item['public_repos']):
                raise ValueError(f'Invalid public_repos: {id_}')
            if not isinstance(item['links'],list) or id_ in item['links'] or len(item['links']) != len(set(item['links'])):
                raise ValueError(f'Invalid cross-domain links: {id_}')
        if len(registry_ids) != len(set(registry_ids)) or set(registry_ids) != {p.stem for p in paths}:
            raise ValueError('Registry and pack IDs differ or contain duplicates')
        for item in registry['domains']:
            if any(v not in registry_ids for v in item['links']):
                raise ValueError(f'Unknown cross-domain target: {item["id"]}')
            fixture = ROOT / 'examples' / 'domain_samples' / f'{item["id"]}.txt'
            model = fixture.with_suffix('.model.json')
            if not fixture.is_file() or not model.is_file():
                raise ValueError(f'Missing synthetic sample/model: {item["id"]}')
            parsed = json.loads(model.read_text(encoding='utf-8'))
            if not isinstance(parsed,dict) or not isinstance(parsed.get('records'),list) or not parsed['records']:
                raise ValueError(f'Invalid synthetic model: {item["id"]}')
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
        errors.append(f'domain_registry: {e}')
    return errors


if __name__ == '__main__':
    errors = validate()
    for error in errors: print('ERROR:', error, file=sys.stderr)
    print('FAILED' if errors else 'PASS: pipeline + domain packs valid')
    sys.exit(1 if errors else 0)
