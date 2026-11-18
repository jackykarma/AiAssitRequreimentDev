# Midoo AI 页面抓取图（仅 com.midoo.ai）

包名：`com.midoo.ai` · 版本：1.5.27 · 入口：`MainActivity` · 设备：PMA110

## 有效页

| 文件 | 说明 |
| --- | --- |
| `00_home` / `110_tab_课程` | 课程 Plan：阶段进度 + 讲解/练习/情景对话卡 + 步骤列表 |
| `120_tab_对话` | Chat：角色大卡轮播（Ella）+「去聊聊」 |
| `130_tab_趣玩` | Play：分类 pill + 双列瀑布空态卡 |
| `140_tab_我的` | 我的：头像/统计 + VIP 卡 + 学习概览 |

底栏 5 Tab：**课程 / 对话 / Midoo(中心品牌) / 趣玩 / 我的**。  
中心「Midoo」在自动发现时易与内容区按钮混淆；本图鉴以人工点选四角 Tab + 截图确认为准。

## 早期误抓 / 需隔离

| 文件 | 说明 |
| --- | --- |
| `100_tab_课程` | 与 home 同 hash，重复 |
| `200_00_0` / `200_01_Midoo` | 爬虫误点后的子页；焦点曾丢桌面，分析以四 Tab 主屏为准 |

## 未覆盖（深层）

- 课程「开始」后的讲解/练习会话流
- 对话进入后的实时聊天页
- 趣玩具体玩法页、设置页
- 中心 Midoo 品牌入口落地页

深层页：请在 App 内手动打开后  
`python .../capture_app_ui.py --package com.midoo.ai --out research/midoo-ui --once <name>`

## 抓取约束

1. 每次 tap 前焦点须含 `com.midoo.ai`
2. 禁止点系统手势条 / 通知栏
3. 通知栏打开时先 BACK 再继续
