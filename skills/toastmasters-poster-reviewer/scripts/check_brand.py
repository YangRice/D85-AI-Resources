#!/usr/bin/env python3
"""Measure poster logo, color and model-read copy evidence offline."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def review_module():
    path = Path(__file__).with_name('vision_review.py')
    spec = importlib.util.spec_from_file_location('tm_vision_review', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect(candidate, observations, root):
    from PIL import Image
    review = review_module()
    if not isinstance(observations, dict) or observations.get('format') != review.FORMAT:
        raise ValueError('Expected ' + review.FORMAT + ' observations')
    with Image.open(candidate) as opened:
        input_format = opened.format
        if input_format not in ('PNG', 'JPEG'):
            raise ValueError('Only PNG and JPEG exports are supported')
        rgba = opened.convert('RGBA')
    if rgba.getextrema()[3] != (255, 255):
        raise ValueError('Final candidate must be opaque; flatten against intended background first')
    result = review.inspect(rgba.convert('RGB'), observations, root, candidate)
    result['input_format'] = input_format
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--observations', type=Path, help='Model-read regions and copy bound to the candidate')
    export = parser.add_mutually_exclusive_group()
    export.add_argument('--template', action='store_true', help='Print incomplete observations to fill from actual image inspection')
    export.add_argument('--rules', action='store_true', help='Print manual identity and measurement rule data')
    args = parser.parse_args()
    if args.template or args.rules:
        module = review_module()
        print(json.dumps(module.template() if args.template else module.RULES, indent=2))
        return 0
    if args.candidate is None or args.observations is None:
        parser.error('--candidate and --observations are required unless exporting a template/rules')
    try:
        observations = json.loads(args.observations.read_text(encoding='utf-8'))
        result = inspect(args.candidate, observations, args.observations.resolve().parent)
    except (ImportError, OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json.dumps(dict(scoped_verdict='BLOCKED', error=str(error))))
        return 2
    print(json.dumps(result, indent=2))
    return {'PASS': 0, 'REVISE': 1, 'BLOCKED': 2}[result['scoped_verdict']]


if __name__ == '__main__':
    sys.exit(main())
