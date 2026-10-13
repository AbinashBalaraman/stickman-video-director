#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
root = Path('skills/directing-stickman-videos')
catalog = (root / 'references/style-catalog.md').read_text()
contract = (root / 'references/omni-flash-prompt-contract.md').read_text()
skill = (root / 'SKILL.md').read_text()
assert 'One classic white line stickman on black.' in catalog
assert 'All five body lines remain connected during movement.' in catalog
assert 'without separate hand or foot shapes' in catalog
assert 'Occasional simple line expressions are allowed by default.' in catalog
assert 'Light-polarity adaptation and unrelated-story regression remain unverified' in catalog
assert 'repeat the full frozen character anchor' in contract
assert 'no facial features, no hair, no clothing, no filled body, stable proportions, uniform medium line weight' not in contract
assert 'For Style 1, freeze the full character anchor' in skill
assert not (root / 'references/continuity-lock.md').exists(), 'Unrelated draft continuity changes included'
print('Classic character instruction regression passed.')
PY
