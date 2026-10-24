#!/usr/bin/env python3
"""Byte-level A1-A5 preservation during the independent B runtime correction.

This checks preserved instructions, not provider-backed visual/audio quality.
The voice reference baseline includes the pre-existing local A-only scope notice.
"""
import hashlib
from pathlib import Path

skill = Path(__file__).resolve().parents[1] / "skills/directing-stickman-videos"
expected = {
    "style-catalog.md": "0c75bdb6fefab28ac6f0dc61f6fa151a0793667479e23ae2696f4964fd4ea01d",
    "prehistoric-dark-comedy.md": "1a3a58a22b392cc087a0aa645b3f8478a3136e7e7f35d086ddb588ac091df860",
    "cozy-storytelling.md": "a0b3f5890857582bb1e7bfa819cefcc7ffd55af72ab8997e1b286b7ad27f1419",
    "historical-cartoon.md": "360f374c7b521353f5fbb9cb546b6f9f70a098973b99281c28d04ce28e77b01d",
    "voice-continuity.md": "ac14fce4f8e4176815d05260de8eeea22345c0920d8e3e2b3911a380affe2ed3",
    "storyboard-template.md": "486338e79397c73443fb390ff03883e5712834b1ddf542c3af54a8dbf6cb870b",
    "omni-flash-prompt-contract.md": "2ef4527750d10c20274f89f86cca9d6483430cef489722c4afb9893ae1d8fbe5",
    "examples.md": "c183e159304eb6dc12f9ad0b06f037a3f880282bc0b75bf06a2863705ddf00f4"
}
entry = (skill / "SKILL.md").read_bytes()
director = b"## A \xc2\xb7 Director\n" + entry.split(b"## A \xc2\xb7 Director\n", 1)[1]
assert hashlib.sha256(director).hexdigest() == "f710612be73c952fb130d891b0650388ec5ae89469cae95eda8e147eec18b73e", "A Director contract changed"
for name, digest in expected.items():
    assert hashlib.sha256((skill / "references" / name).read_bytes()).hexdigest() == digest, f"A reference changed: {name}"
print("A1-A5 Director body, style references, prompts and voice rules are byte-identical to the pre-B-correction baseline.")
print("No live generation or visual-quality guarantee is implied.")
