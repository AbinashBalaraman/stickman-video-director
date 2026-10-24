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

sections = ("## 两种视频制作模式", "## 开始使用", "## A · 导演模式画风一览",
            "## B · 自动成片画风一览", "## 常见问题", "## Star 增长曲线", "## 许可证")
assert [cn.index(s) for s in sections] == sorted(cn.index(s) for s in sections)
assert "## 接下来做什么" not in cn, "Keep the removed next-steps heading out of the footer"
footer = cn.split("## Star 增长曲线", 1)[1].split("## 许可证", 1)[0]
footer_items = ("⭐ **想做不露脸的 YouTube 频道", "🔔 **关注", '<a id="whats-next"></a>',
                "🎨 **更多画风（计划中）**：", "💬 **建议与投稿**：", '<div align="center">')
assert [footer.index(s) for s in footer_items] == sorted(footer.index(s) for s in footer_items), "Place icon-led contribution paragraphs after the creator introduction and before the Star chart"
mode_comparison = cn.split('<a id="creation-modes"></a>', 1)[1].split('<a id="quick-start"></a>', 1)[0]
mode_rows = [line for line in mode_comparison.splitlines() if line.startswith("|")]
assert mode_rows[0] == '|  | <div align="center">A · 导演模式 · Director</div> | <div align="center">B · 自动成片 · Autopilot</div> |', "Center only the mode headings"
assert mode_rows[1] == "|:---:|:---|:---|", "Keep explanatory columns left-aligned"
assert mode_rows[-1] == '| **开始** | <div align="center"><a href="#director-start">使用 Director</a></div> | <div align="center"><a href="#autopilot-start">使用 Autopilot</a></div> |', "Center the two start links"
assert all('align="center"' not in row for row in mode_rows[2:-1]), "Do not center the explanatory body text"
assert "一次安装，按需选择" in cn
assert "[查看画风一览 ↓]" not in cn, "Do not restore the removed per-mode shortcut links"
assert "[A 画风](#a-styles) · [B 画风](#b-styles)" in cn, "Keep the top style navigation"
navigation = next(line for line in cn.splitlines() if line.startswith("[开始使用](#quick-start)"))
assert navigation.endswith("[常见问题](#faq)"), "Replace only the tutorial shortcut with the FAQ anchor"
assert "[最近更新]" not in navigation, "Keep the removed updates shortcut out of the navigation"
assert '<a id="recent-updates"></a>' not in cn, "Do not restore the removed updates anchor"
assert "## 最近更新" not in cn, "Do not restore the removed updates section"
assert "完整制作教程" not in navigation
assert "[完整制作教程](https://x.com/CrazyKaomei/status/2102311241046008268)" in cn, "Keep the tutorial in the Director instructions"
assert "## 使用小贴士" not in cn
faq = cn.split('<a id="faq"></a>', 1)[1].split('<!-- readme:contribute -->', 1)[0]
faq_questions = (
    "没有脚本，也能做视频吗？",
    "不会画画、不会做动画，也能用吗？",
    "一定要用 Codex 吗？",
    "怎么把文章或参考内容，变成更有吸引力的视频？",
    "可以自定义画幅、语言和配音吗？",
    "使用需要付费吗？",
    "画面或配音不满意，需要全部重做吗？",
    "安装好了，接下来做什么？",
    "做出来的视频可以发 YouTube、用于商业项目吗？",
)
assert re.findall(r"^### Q(\d+)\. (.+)$", faq, re.M) == [
    (str(number), question) for number, question in enumerate(faq_questions, 1)
], "Keep Q1-Q9 directly visible with the nine approved questions in order"
assert "<details" not in faq and "</details>" not in faq and "<summary" not in faq, "Do not collapse the FAQ answers"
for requirement in ("目标观众、发布平台和期望时长", "开场钩子、叙事推进和结尾引导",
                    "具体音色取决于所用配音服务", "不一定包含它的 API 调用额度",
                    "复用已经确认的配音和素材", "缺什么、怎么补、下一步做什么",
                    "自动成片先确认脚本和 20 秒有声样片，再制作整片",
                    "第三方图片、音乐、音效及配音服务", "以平台审核为准"):
    assert requirement in faq, requirement
assert "不需要另装第二个 Skill" in cn
assert "**10 分钟及以上**" in cn and "连续故事短剧" in cn
assert "Codex、Claude Code" in cn and "Google Flow" in cn
assert "A、B 画风独立编号、分别展示，不共用画面" in cn
assert "给故事脚本和需求 → 检查配音和生图配置 → 确认 20s 样片效果 → 自动制作长视频 → 拿到完整成片" in cn
autopilot_start = cn.split('<a id="autopilot-start"></a>', 1)[1].split('<a id="style-gallery"></a>', 1)[0]
for requirement in ("把这个文章/帖子/新闻...做成在 YouTube 上有吸引力的视频", "需求：5～10 分钟", "B1「极简手绘风」", "旁白、字幕和音效", "20 秒有声样片", "画面跟随配音节奏", "交付完整视频文件"):
    assert requirement in autopilot_start, requirement
for label in ("A1：经典黑白风", "A2：现代潮酷风", "A3：史前洞穴风",
              "A4：治愈故事风", "A5：历史卡通风", "B1：极简手绘风", "B2：待更新…"):
    assert f"### {label}\n" in cn, label
hero = cn.split('<table width="100%">', 1)[1].split("</table>", 1)[0]
style_names = ("经典黑白风", "现代潮酷风", "史前洞穴风", "治愈故事风", "历史卡通风")
b_style_names = [name for name in re.findall(r"^### B\d+：([^\n]+)$", cn, re.M)
                 if not name.startswith("待更新")]
assert re.findall(r"<strong>([^<]+)</strong><br>", hero) == list(style_names) + b_style_names, "Sync every published B style into the top preview grid, using its style name without A/B prefixes"
assert "<strong>极简手绘风</strong><br>" in hero, "Use the approved B1 preview in the sixth cell"
assert f"**{len(style_names) + len(b_style_names)} 大画风 · {len(style_names) + 2 + len(b_style_names)} 种视觉方案 · 实测样片 · 免费开源**" in cn
assert re.search(r'<a href="#b1"><img src="([^"]+/b1-minimal-handdrawn-2026-10-23\.gif)"[^>]+width="90%"></a>', hero), "Link the latest top B1 preview to its detail section"
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
assert len(previews) == 13, "Keep all existing lightweight A previews and both B1 short previews"
for preview in previews:
    file = root / preview
    header = file.read_bytes()[:10]
    assert header[:6] in (b"GIF87a", b"GIF89a")
    width, height = struct.unpack("<HH", header[6:10])
    assert width <= 640 and height <= 360
    assert file.stat().st_size < 4_000_000
b1 = cn.split('<a id="b1"></a>', 1)[1].split('<a id="b2"></a>', 1)[0]
assert re.search(r'src="([^"]+/b1-minimal-handdrawn-2026-10-23\.gif)"', hero).group(1) == re.search(r'src="([^"]+/b1-minimal-handdrawn-2026-10-23\.gif)"', b1).group(1), "Reuse the same immutable B1 preview in the hero and detail section"
fields = ("- **画面特点**：", "- **适合内容**：", "- **怎么选**：")
assert all(b1.count(field) == 1 for field in fields), "Use the same introduction fields as A styles"
assert [b1.index(field) for field in fields] == sorted(b1.index(field) for field in fields)
table = re.search(r'<table width="100%">(.*?)</table>', b1, re.S).group(1)
rows = re.findall(r"<tr>(.*?)</tr>", table, re.S)
assert len(rows) == 3, "Keep two B1 short cases with a heading, preview and caption row"
assert re.findall(r'<th width="50%" align="center">(.*?)</th>', rows[0]) == [
    "案例 1：不露脸做 YouTube", "案例 2：为什么没人看？"
], "Use concise B1 case titles while preserving the original and later sample order"
cells = re.findall(r'<td width="50%" align="center">(.*?)</td>', rows[1], re.S)
assert len(cells) == 2, "Keep both preview columns equally sized and centered"
assert 'href="assets/readme/b1-minimal-handdrawn.mp4"' in cells[0] and "/b1-minimal-handdrawn.gif\"" in cells[0]
assert 'href="skills/directing-stickman-videos/assets/b1/approved-2026-10-23.mp4"' in cells[1] and "/b1-minimal-handdrawn-2026-10-23.gif\"" in cells[1]
assert all('width="360"' in cell for cell in cells), "Match A's lightweight preview width"
assert len(re.findall(r'<td align="center">.*?</td>', rows[2])) == 2
assert "待更新" not in table, "Both short cases already exist"
assert re.findall(r'href="([^"]+\.mp4)"', b1) == [
    "assets/readme/b1-minimal-handdrawn.mp4", "skills/directing-stickman-videos/assets/b1/approved-2026-10-23.mp4"
], "Show only the two approved short samples, not the new longform film"
assert "播放有声样片" not in b1 and "画风与制作说明" not in b1, "Do not restore the removed redundant link row"
assert re.search(r'<img src="https://cdn\.jsdelivr\.net/gh/kaomei/stickman-video-director@[0-9a-f]{40}/assets/readme/previews/b1-minimal-handdrawn-2026-10-23\.gif"[^>]+width="360">', b1), "Keep the immutable B1 preview route and match A's preview width"
assert 'href="skills/directing-stickman-videos/assets/b1/approved-2026-10-23.mp4"' in b1, "Click the preview to view/download the approved sample with sound"
assert "点击查看或下载 Bodi 有声样片" in b1, "GitHub MP4 blob links must not promise inline playback"
current_sample = root / "skills/directing-stickman-videos/assets/b1/approved-2026-10-23.mp4"
assert hashlib.sha256(current_sample.read_bytes()).hexdigest() == "111c241a836a0c26b27df2cbff3ba5697b97460dbb873b68dd2f6eda2383b3fc", "Publish the accepted Ryan V4, not the runtime fixture"
sample = root / "assets/readme/b1-minimal-handdrawn.mp4"
assert hashlib.sha256(sample.read_bytes()).hexdigest() == "9d2a1789eec25ad3b825631ee3d1ea3cb7417aafb0a5c223ccce08434cedcc3a", "Restore the original V15 sample without regenerating it"
assert "https://github.com/leksautomate" in cn
assert "api.star-history.com/svg" in cn
license_targets = {"LICENSE", "https://github.com/kaomei/stickman-video-director/blob/main/LICENSE"}
assert any("MIT" in label and target in license_targets
           for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", cn)), "Link the repository's MIT license"
print("Chinese A/B layout, approved narration/CTA, links, restored V15 case 1 and Ryan V4 case 2 passed.")
