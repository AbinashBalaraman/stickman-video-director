#!/usr/bin/env python3
"""Style 5 routing and source-anchor regression; not a provider quality score."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
skill = root / "skills/directing-stickman-videos"
ref = (skill / "references/historical-cartoon.md").read_text()
anchor = (
    "Polished 2D cel-shaded cartoon animation with thick clean black outlines and soft metallic shading. "
    "Stick-figure characters with smooth white filled round heads, simple black oval eyes, expressive brows and mouths, "
    "no nose, and thin black stick limbs, in the described costume. Exactly two arms and two legs, each shown only in its "
    "current pose. Clean, sunlit, painterly landscapes."
)
assert anchor in ref, "Preserve the contributor's complete drawing anchor"
for token in (
    "https://github.com/leksautomate", "/pull/41",
    "repeat its **full description**", "two visible non-color differences",
    "no style-specific character-count cap", "voice-continuity.md",
    "default when no other voice is requested", "opening/action/ending states",
    "Backgrounds are full-color", "do not rewrite Styles 1–4",
):
    assert token in ref, token
for filename in (
    "SKILL.md", "references/style-catalog.md",
    "references/storyboard-template.md", "references/omni-flash-prompt-contract.md",
):
    assert "historical-cartoon.md" in (skill / filename).read_text(), filename

# Existing specialist contracts must not be rewritten for this addition.
baseline = {
    "prehistoric-dark-comedy.md": "1a3a58a22b392cc087a0aa645b3f8478a3136e7e7f35d086ddb588ac091df860",
    "cozy-storytelling.md": "a0b3f5890857582bb1e7bfa819cefcc7ffd55af72ab8997e1b286b7ad27f1419",
    "voice-continuity.md": "24014bc599e237644c743f033a0b62c556ba4ed8689d382d08b1bcdce1967de2",
}
for filename, fingerprint in baseline.items():
    path = skill / "references" / filename
    content = path.read_bytes()
    if filename == "voice-continuity.md":
        # Only the exact A/B scope notice may precede the unchanged A contract.
        heading = b"# Shared voice continuity \xe2\x80\x94 all visual styles\n\n"
        notice = (
            b"Scope: **A \xc2\xb7 Director text-to-video prompts only**. B \xc2\xb7 Autopilot uses named TTS voices under `autopilot.md`; "
            b"do not copy this document's descriptive voice profiles into any B-style TTS request.\n\n"
        )
        assert content.startswith(heading + notice), "Missing exact A-only voice scope"
        content = heading + content[len(heading + notice):]
    assert hashlib.sha256(content).hexdigest() == fingerprint, filename
print("Style 5 source anchor, routing, scope and unchanged specialist contracts passed.")
