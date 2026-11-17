"""Validate an analysis record: no TODO placeholders; status from allowed set."""
from __future__ import annotations
import sys
from pathlib import Path
ALLOWED = {'NEW', 'ANALYZED', 'REVIEWED', 'BASELINED', 'CHANGED', 'DEFERRED'}

def validate(path: str) -> list[str]:
    errors: list[str] = []
    text = Path(path).read_text(encoding='utf-8')
    if 'TODO' in text:
        errors.append('record contains TODO placeholders')
    for line in text.splitlines():
        if line.strip().startswith('- status:'):
            val = line.split(':', 1)[1].strip()
            if val not in ALLOWED:
                errors.append('invalid status: ' + val)
    return errors

if __name__ == '__main__':
    errs = validate(sys.argv[1])
    print('VALID' if not errs else errs)
    raise SystemExit(1 if errs else 0)
