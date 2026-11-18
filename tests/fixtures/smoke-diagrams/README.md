# 烟测真图夹具（Archify finalize）

本目录 `out/*.html` + `out/*.png` 由 Archify **正式 finalize** 生成，对标无痛单词「今日复习」需求。

重新生成：

```bash
node .agents/skills/archify/bin/archify.mjs finalize <type> candidates/<stem>.json out/<stem>.html --quality showcase --json
node plugins/aiassitrequreimentdev/scripts/export_diagram_png.mjs out/<stem>.html
```

禁止用手写空壳 HTML/小 PNG 替换 `out/` 冒充过门禁。
