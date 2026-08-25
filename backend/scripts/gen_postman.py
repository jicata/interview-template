"""Generate the repo-owned Postman collection from the FastAPI app's OpenAPI schema.

The collection is the *executable* wire contract: unlike prose docs it rots
silently, because code compiles and tests pass whether or not it is true.
Generating it from `app.openapi()` (not a running server) keeps it honest and
makes drift a check rather than a habit.

    python scripts/gen_postman.py            # write the collection
    python scripts/gen_postman.py --check     # exit 1 if it is stale
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent.parent / 'postman' / 'interview-template.postman_collection.json'
SCHEMA = 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'


def _example(schema: dict, spec: dict) -> object:
    """Best-effort example value for a JSON schema node."""
    if '$ref' in schema:
        name = schema['$ref'].rsplit('/', 1)[-1]
        schema = spec.get('components', {}).get('schemas', {}).get(name, {})
    match schema.get('type'):
        case 'object':
            return {k: _example(v, spec) for k, v in schema.get('properties', {}).items()}
        case 'array':
            return [_example(schema.get('items', {}), spec)]
        case 'integer':
            return schema.get('example', 0)
        case 'number':
            return schema.get('example', 0.0)
        case 'boolean':
            return schema.get('example', False)
        case _:
            return schema.get('default', schema.get('example', ''))


def build() -> dict:
    spec = app.openapi()
    items = []
    for path, methods in sorted(spec.get('paths', {}).items()):
        for method, op in sorted(methods.items()):
            params = [p for p in op.get('parameters', []) if p.get('in') == 'query']
            query = [
                {
                    'key': p['name'],
                    'value': str(p.get('schema', {}).get('default', '')),
                    'description': p.get('description', ''),
                    'disabled': not p.get('required', False)
                    and p.get('schema', {}).get('default') is None,
                }
                for p in params
            ]
            segments = [s for s in path.split('/') if s]
            raw = '{{baseUrl}}' + path
            if query:
                raw += '?' + '&'.join(f"{q['key']}={q['value']}" for q in query if not q['disabled'])
            request: dict = {
                'method': method.upper(),
                'header': [],
                'url': {'raw': raw, 'host': ['{{baseUrl}}'], 'path': segments},
                'description': op.get('description') or op.get('summary', ''),
            }
            if query:
                request['url']['query'] = query
            body_spec = op.get('requestBody', {}).get('content', {}).get('application/json', {})
            if body_spec:
                request['header'].append({'key': 'Content-Type', 'value': 'application/json'})
                request['body'] = {
                    'mode': 'raw',
                    'raw': json.dumps(_example(body_spec.get('schema', {}), spec), indent=2),
                    'options': {'raw': {'language': 'json'}},
                }
            items.append(
                {
                    'name': f"{method.upper()} {path}",
                    'request': request,
                    'response': [],
                }
            )
    return {
        'info': {
            'name': spec['info']['title'],
            'description': (
                'GENERATED from the FastAPI OpenAPI schema by '
                '`backend/scripts/gen_postman.py`. Do not hand-edit — regenerate. '
                'This is the repo-owned executable wire contract; a route change '
                'without a matching delta here is a review finding.'
            ),
            'schema': SCHEMA,
        },
        'variable': [{'key': 'baseUrl', 'value': 'http://localhost:8000', 'type': 'string'}],
        'item': items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='exit 1 if the collection is stale')
    args = parser.parse_args()

    rendered = json.dumps(build(), indent=2) + '\n'
    if args.check:
        if not OUT.exists():
            print(f'MISSING: {OUT} — run `python scripts/gen_postman.py`', file=sys.stderr)
            return 1
        if OUT.read_text(encoding='utf-8') != rendered:
            print(
                f'STALE: {OUT} does not match the current OpenAPI schema.\n'
                'A route or schema changed without regenerating the wire contract.\n'
                'Run `python scripts/gen_postman.py`.',
                file=sys.stderr,
            )
            return 1
        print(f'{OUT.name} is up to date')
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding='utf-8')
    print(f'wrote {OUT} ({len(build()["item"])} request(s))')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
