#!/usr/bin/env python3
"""Check Chinese-only onboarding, section layout, and preview budgets."""
from pathlib import Path
import re
import struct

root = Path(__file__).resolve().parents[1]
cn = (root / "README.md").read_text()
assert cn == (root / "README.zh-CN.md").read_text()
assert "## 你的作品，也可以成为下一个案例" not in cn
assert "## 下一种火柴人，你来点" in cn
assert cn.index("也欢迎在 [Issues]") > cn.index("## 下一种火柴人，你来点")
assert "## 从文案到视频，五步走" not in cn
assert "## 你会拿到什么" not in cn
assert "## 它帮你做什么" in cn and "## 开始使用" in cn
install = cn.split("### 1. 安装 Skill", 1)[1].split("<!-- readme:workflow -->", 1)[0]
assert "帮我安装这个 Skill：\nhttps://github.com/kaomei/stickman-video-director" in install
assert len(install.strip()) < 130, "Keep the installation entry short"
for unnecessary in ("$skill-installer", "重启", "官方安装说明", "<details>", "WorkBuddy", "git clone", "references"):
    assert unnecessary not in install, unnecessary
topic = cn.split("### 2. 给一个话题", 1)[1].split("### 3.", 1)[0]
assert "把话题、文案或文章直接发给 AI" in topic
assert "帮我做一个关于“为什么越晚，越舍不得睡”的火柴人视频。" in topic
for preset in ("$directing", "16:9", "美式男声", "先给我导演提案", "想换个画风"):
    assert preset not in topic, "Topic entry must not require a prefilled production request"
assert "### 3. 跟着引导，确认提案" in cn
assert "Skill 会主动询问；时长可指定，默认 60 秒" in cn
assert "你确认后，它才输出最终分段提示词" in cn
assert "### 4. 生成视频，剪辑成片" in cn
assert "## 最近更新" in cn and "CHANGELOG.zh-CN.md" in cn
assert "## Star 增长曲线" in cn and "[MIT License](LICENSE)" in cn
assert cn.count("<details>") == cn.count("</details>")
assert cn.count('<div align="center">') == cn.count("</div>")

for removed in ("样片同款主题，直接试", "example-overthinking", "展开看已有导演预案节选", "你给的内容："):
    assert removed not in cn, "Removed example must not leave text or dangling links"
assert (root / "skills/directing-stickman-videos/references/examples.md").exists()
assert cn.index("## 使用小贴士") < cn.index("选横屏还是竖屏？查看平台、比例与内容建议") < cn.index("## 最近更新")

for link in re.findall(r"\]\(([^)]+)\)", cn):
    if "://" not in link and not link.startswith("#"):
        assert (root / link.split("#")[0]).exists(), link

previews = sorted(set(re.findall(r'src="(assets/readme/previews/[^" ]+\.gif)"', cn)))
assert len(previews) == 8
old_bytes = new_bytes = 0
for preview in previews:
    optimized = root / preview
    original = root / "assets/readme" / optimized.name
    assert optimized.exists()
    header = optimized.read_bytes()[:10]
    assert header[:6] in (b"GIF87a", b"GIF89a")
    assert struct.unpack("<HH", header[6:10]) == (400, 225)
    assert optimized.stat().st_size < original.stat().st_size
    old_bytes += original.stat().st_size
    new_bytes += optimized.stat().st_size
assert new_bytes < old_bytes * 0.6, "Preview total should shrink by at least 40%"

for lang in ("en", "ja", "ko", "pt-BR"):
    text = (root / f"README.{lang}.md").read_text()
    assert "assets/readme/previews/" not in text, "No multilingual sync in this change"

print(f"Chinese onboarding passed; previews {old_bytes:,} -> {new_bytes:,} bytes ({1-new_bytes/old_bytes:.1%} smaller).")
