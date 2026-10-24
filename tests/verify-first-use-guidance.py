#!/usr/bin/env python3
"""Check onboarding wiring and package integrity, not model behavior."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = root / "skills/directing-stickman-videos"
entry = (skill / "SKILL.md").read_text()
guide = skill / "references/getting-started.md"
guide_text = guide.read_text()

# The new shared entry must reach the guide in the installed package.
assert "(references/getting-started.md)" in entry and guide.is_file()
for source in (skill / "SKILL.md", guide):
    for target in re.findall(r"\]\(([^)]+\.md)(?:#[^)]*)?\)", source.read_text()):
        if not target.startswith(("https://", "http://")):
            assert (source.parent / target).is_file(), f"Broken reference: {source}: {target}"

# Keep the existing Director production contract byte-for-byte unchanged.
legacy = "## A · Director\n" + entry.split("## A · Director\n", 1)[1]
assert hashlib.sha256(legacy.encode()).hexdigest() == "f710612be73c952fb130d891b0650388ec5ae89469cae95eda8e147eec18b73e"
assert len(entry.encode()) <= 14000, "Keep the new workflow detail in references"
frontmatter = entry.split("---\n", 2)[1]
name = re.search(r"^name: (.+)$", frontmatter, re.M).group(1)
description = json.loads(re.search(r"^description: (.+)$", frontmatter, re.M).group(1))
assert name == "directing-stickman-videos" and description

# The UI starter invokes that same Skill; it is not a new mode/package.
interface = dict(re.findall(r"^  (\w+): (.+)$", (skill / "agents/openai.yaml").read_text(), re.M))
assert f"${name}" in json.loads(interface["default_prompt"])
assert json.loads(interface["display_name"]) == "Stickman Video Director"
entries = [p for p in root.rglob("SKILL.md")
           if not {"node_modules", ".git"}.intersection(p.relative_to(root).parts)]
assert entries == [skill / "SKILL.md"], "Do not add a second discoverable Skill"
scripts = json.loads((skill / "package.json").read_text())["scripts"]
assert not {"preinstall", "install", "postinstall"}.intersection(scripts), "Welcome is not an install-time executable hook"

# Installation instructions ask the installing assistant to load the real entry.
cn = (root / "README.zh-CN.md").read_text()
catalog_base = "https://github.com/kaomei/stickman-video-director/blob/main/README.zh-CN.md"
public_links = set(re.findall(r"\]\((https://[^)]+)\)", guide.read_text()))
for catalog in ("a-styles", "b-styles"):
    assert f"{catalog_base}#{catalog}" in public_links, f"Missing public style catalog: {catalog}"
    assert f'<a id="{catalog}"></a>' in cn, f"Broken public style anchor: {catalog}"
install = cn.split("```text\n", 1)[1].split("```", 1)[0]
assert "https://github.com/kaomei/stickman-video-director" in install
assert "已安装的 SKILL.md" in install
assert (root / "tests/scenarios/first-use-guidance.md").is_file()

# Chinese-facing welcome uses Chinese mode names, not internal routing labels.
welcome = guide_text.split("### 欢迎使用火柴人视频 Skill\n", 1)[1].split("### Adapt instead of replaying the README", 1)[0]
assert "#### A · 导演模式：" in welcome and "#### B · 全自动模式：" in welcome
assert not re.search(r"\b(?:Director|Autopilot)\b|自动成片", welcome)
assert "A 模式的旁白和声音设计沿用原有规则" in welcome
assert "稳定男声默认" not in welcome, "Do not misstate A's source-appropriate voice selection"

# Optional A references are reachable without changing the frozen Director body.
reference_heading = "Optional A character references"
assert reference_heading in entry
a_reference = guide_text.split(f"### {reference_heading}\n", 1)[1].split("## B · Autopilot handoffs", 1)[0]
for requirement in ("not a new setup requirement", "front, side and back views",
                    "Reuse suitable user-approved references", "every generated clip",
                    "when the chosen tool supports reference images", "not a consistency guarantee",
                    "not replace, shorten or globally rewrite", "fixed character anchor"):
    assert requirement in a_reference, requirement
assert "按需确认人物三视图" in welcome and "三视图（正面、侧面、背面）" in welcome

# Per-style defaults stay inside one installation; B1 is not all of B.
autopilot = (skill / "references/autopilot.md").read_text()
b1 = (skill / "references/b1-minimal-handdrawn.md").read_text()
priority = "explicit user choice → selected B-style default → B common fallback"
assert priority in autopilot and priority in guide.read_text()
assert "visuals, captions, voice, pacing and SFX" in entry
assert "caption font/size/placement" in autopilot
assert "B1 defaults, not requirements for other B styles" in b1
assert "Google Gemini **Bodi**" in b1 and "original **Sadaltager** recording" in b1
assert "without added style/direction instructions" in b1
print("First-use reference wiring, single-Skill identity and unchanged Director contract passed.")
print("Independent B-style settings, defaults precedence and unchanged demo-voice policy passed.")
print("Static checks only; fresh-host conversational acceptance remains a separate test.")
