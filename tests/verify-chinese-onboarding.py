#!/usr/bin/env python3
"""Protect the approved Chinese A/B layout, working links and B1 showcase."""
from pathlib import Path
import hashlib
import re
import struct

root = Path(__file__).resolve().parents[1]
cn = (root / "README.zh-CN.md").read_text()
assert (root / "README.md").read_bytes() == (root / "README.en.md").read_bytes()
assert "# 火柴人动画画风库" in cn
assert "[**简体中文**](README.zh-CN.md)" in cn
assert "自动制作带配音、字幕与微动画的完整视频" in cn
assert "汇总全网热门的火柴人画风，持续更新与开源" in cn
assert "本系列持续更新，欢迎点个 Star，更多热门画风陆续上线。" in cn
assert "想做不露脸的 YouTube 频道，探索内容变现？" in cn
assert "我是烤妹儿，专注不出镜视频与自动化工作流" in cn

sections = ("## 你想怎么做？", "## 开始使用", "## A · 导演模式画风一览",
            "## B · 自动成片画风一览", "## 使用小贴士", "## 最近更新")
assert [cn.index(s) for s in sections] == sorted(cn.index(s) for s in sections)
assert "一次安装，按需选择" in cn
assert "不需要另装第二个 Skill" in cn
assert "**10 分钟及以上**" in cn and "连续故事短剧" in cn
assert "Codex、Claude Code" in cn and "Google Flow" in cn
assert "A、B 画风独立编号、分别展示，不共用画面" in cn
assert "给故事脚本和风格 → 检查配音和生图配置 → 确认 20s 样片效果 → 自动制作长视频 → 拿到完整成片" in cn
for label in ("A1：经典黑白风", "A2：现代潮酷风", "A3：史前洞穴风",
              "A4：治愈故事风", "A5：历史卡通风", "B1：极简手绘风", "B2：待更新…"):
    assert f"### {label}\n" in cn, label
hero = cn.split('<table width="100%">', 1)[1].split("</table>", 1)[0]
style_names = ("经典黑白风", "现代潮酷风", "史前洞穴风", "治愈故事风", "历史卡通风")
assert re.findall(r"<strong>([^<]+)</strong><br>", hero) == list(style_names)
for number, name in enumerate(style_names, 1):
    assert f"### A{number}：{name}\n" in cn, "Keep preview and detail names aligned"
assert "史前黑色幽默" not in cn and "史前手绘 / 黑色幽默" not in cn
assert "用 A3「史前洞穴风」" in cn and "A3 史前洞穴风 · 30 秒" in cn
for variant in ("A1.1", "A1.2", "A2.1", "A2.2"):
    assert variant in cn, variant

storyboard = cn.split('<a id="storyboard-example"></a>', 1)[1].split("</details>", 1)[0]
assert "<details>" in storyboard and "<summary>" in storyboard
approved_voiceover = (
    "Ten thousand years ago, one man finally solved all his problems. He shut them outside.",
    "Then someone offered him food… in exchange for a small favor. Congratulations. Employment was invented.",
    "The reward got smaller. The workload got bigger. And somehow… they called that progress.",
)
for voiceover in approved_voiceover:
    rows = [line for line in storyboard.splitlines() if voiceover in line]
    assert len(rows) == 1 and rows[0].count("|") == 4
assert cn.index('<a id="storyboard-example">') < cn.index('<a id="autopilot-start">')

assert cn.count("<details>") == cn.count("</details>")
assert cn.count('<div align="center">') == cn.count("</div>")
assert cn.count("<table") == cn.count("</table>")
assert cn.count("<td ") == cn.count("</td>")
ids = re.findall(r'<a id="([^"]+)"></a>', cn)
assert len(ids) == len(set(ids)), "Duplicate explicit anchors"
for anchor in re.findall(r'\]\(#([^)]+)\)|href="#([^"]+)"', cn):
    assert next(part for part in anchor if part) in ids, anchor
for link in re.findall(r"\]\(([^)]+)\)", cn):
    if "://" not in link and not link.startswith("#"):
        assert (root / link.split("#")[0]).is_file(), link

previews = sorted(set(re.findall(r'src="https://cdn\.jsdelivr\.net/gh/kaomei/stickman-video-director@[0-9a-f]{40}/(assets/readme/previews/[^" ]+\.gif)"', cn)))
assert len(previews) == 12, "Keep all existing lightweight A previews and the B1 preview"
for preview in previews:
    file = root / preview
    header = file.read_bytes()[:10]
    assert header[:6] in (b"GIF87a", b"GIF89a")
    width, height = struct.unpack("<HH", header[6:10])
    assert width <= 640 and height <= 360
    assert file.stat().st_size < 4_000_000
b1 = cn.split('<a id="b1"></a>', 1)[1].split('<a id="b2"></a>', 1)[0]
fields = ("- **画面特点**：", "- **适合内容**：", "- **怎么选**：")
assert all(b1.count(field) == 1 for field in fields), "Use the same introduction fields as A styles"
assert [b1.index(field) for field in fields] == sorted(b1.index(field) for field in fields)
rows = [line for line in b1.splitlines() if line.startswith("|")]
assert len(rows) == 4 and all(row.count("|") == 3 for row in rows), "Match A's two-column sample table"
assert rows[1] == "|:---:|:---:|" and "待更新" in rows[2]
assert "播放有声样片" not in b1 and "画风与制作说明" not in b1, "Do not restore the removed redundant link row"
assert re.search(r'<img src="https://cdn\.jsdelivr\.net/gh/kaomei/stickman-video-director@[0-9a-f]{40}/assets/readme/previews/b1-minimal-handdrawn\.gif"[^>]+width="360">', b1), "Keep the immutable B1 preview route and match A's preview width"
sample = root / "assets/readme/b1-minimal-handdrawn.mp4"
assert hashlib.sha256(sample.read_bytes()).hexdigest() == "9d2a1789eec25ad3b825631ee3d1ea3cb7417aafb0a5c223ccce08434cedcc3a", "Publish the approved V15, not the runtime fixture"
assert "https://github.com/leksautomate" in cn
assert "api.star-history.com/svg" in cn
license_targets = {"LICENSE", "https://github.com/kaomei/stickman-video-director/blob/main/LICENSE"}
assert any("MIT" in label and target in license_targets
           for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", cn)), "Link the repository's MIT license"
print("Chinese A/B layout, approved narration/CTA, links and exact B1 V15 showcase passed.")
