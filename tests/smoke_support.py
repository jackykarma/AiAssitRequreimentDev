"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - smoke_support.py
 ** Description: 插件烟测落盘：在仓库 smoke/ 写出可人工打开的各阶段产物
 ** Version: 1.0
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT
 *********************************************************************************/
"""

from __future__ import annotations

import json
import shutil
import struct
import zlib
from pathlib import Path

import yaml

from aiassitrequreimentdev.board import adopt_role, set_path
from aiassitrequreimentdev.gates import init_feature, init_requirement
from aiassitrequreimentdev.progress import accept_gate
from aiassitrequreimentdev.split import evaluate_requirement
from aiassitrequreimentdev.tasks_scaffold import scaffold_tasks
from aiassitrequreimentdev.template_headings import (
    REQ_ARCH_EXPAND_FILES,
    REQ_ARCH_H2,
    REQ_PRD_H2,
)
from tests.test_gates import (
    valid_deploy,
    valid_evidence,
    valid_review,
    valid_spec,
    valid_tech,
    write_yaml,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_ROOT = REPO_ROOT / "smoke"

SCENARIO_SMALL_LIGHT = "01-small-light"
SCENARIO_SMALL_LIGHT_AUTO = "02-small-light-auto"
SCENARIO_LARGE_REQ = "03-large-req"

FEATURE_SMALL_LIGHT = "FEAT-901-smoke-light"
FEATURE_SMALL_LIGHT_AUTO = "FEAT-902-smoke-light-auto"
# 大需求：无痛学环（3 Feature）— 定义见 smoke_english_multi
REQ_LARGE = "REQ-920-painless-study-loop-20261118"
FEATURE_LARGE_FAVORITE = "FEAT-920-notebook-favorite"
FEATURE_LARGE_REVIEW = "FEAT-921-daily-review-queue"
FEATURE_LARGE_STREAK = "FEAT-922-study-streak"
FEATURE_LARGE_ALL = (
    FEATURE_LARGE_FAVORITE,
    FEATURE_LARGE_REVIEW,
    FEATURE_LARGE_STREAK,
)
FEATURE_LARGE = FEATURE_LARGE_REVIEW  # 兼容旧引用：主交付切片


def smoke_root() -> Path:
    SMOKE_ROOT.mkdir(parents=True, exist_ok=True)
    return SMOKE_ROOT


def reset_scenario(name: str) -> Path:
    """清空并创建单个场景根目录（其下可有 features/、requirements/）。"""
    root = smoke_root() / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    return root


def write_archify_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """<!DOCTYPE html>
<html lang="en" data-theme="dark" data-preset="classic">
<head>
  <meta charset="UTF-8">
  <meta name="generator" content="archify 3.2.0">
  <meta name="archify-reader-contract" content="declared-wide-v1">
  <title>smoke diagram</title>
  <style id="archify-fonts"></style>
</head>
<body>
  <main class="diagram">
    <h1>Smoke Archify stub</h1>
    <p>正式评审请用 Archify finalize 替换本桩；本文件满足 G2T/check-req 溯源合同。</p>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_preview_png(path: Path, *, w: int = 640, h: int = 400) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[bytes] = []
    for y in range(h):
        row = bytearray(1 + w * 3)
        row[0] = 0
        for x in range(w):
            i = 1 + x * 3
            row[i] = (x + y) & 0xFF
            row[i + 1] = (x * 3 + y * 5) & 0xFF
            row[i + 2] = (255 - ((x + y) & 0xFF)) & 0xFF
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 6))
        + chunk(b"IEND", b"")
    )


def write_feature_prd(path: Path, *, feature_id: str, requirement_id: str | None, path_name: str) -> None:
    req_line = requirement_id or "—（小需求捷径，无 requirements/）"
    path.write_text(
        f"""# Feature：支付回调幂等（插件烟测）

> **一套事实源**：本文与同目录 `spec.yaml` 同源同编号。  
> 本文件由烟测自动生成，供人工打开核对各阶段产物是否齐全、章节是否可审。

| 字段 | 值 |
| --- | --- |
| Feature ID | {feature_id} |
| 关联需求 | {req_line} |
| 状态 | 冻结 |
| 有无 UI | 无（回调链路无用户界面；`uiRequired=false`） |
| path | {path_name} |

## 背景与目标

- **问题**：支付渠道可能重放同一通知，订单会被推进两次，造成重复履约风险。
- **目标**：相同 `notificationId` 只产生一次支付成功副作用；迟到通知不改变已支付订单。
- **价值**：保证账务一致，降低客服与资损排查成本。

## 范围与非目标

- **In Scope**：回调入口幂等去重、迟到通知短路 ack、可重试失败语义。
- **Out of Scope / 非目标**：不改支付渠道协议；不做后台轮询补单；无新增用户可见 UI。
- **约束**：须与现有订单状态机兼容；写库失败须可安全重试。

## 核心用户旅程（UJ*）

| ID | 角色 | 入口 | 步骤（1…n） | 成功结果 |
| --- | --- | --- | --- | --- |
| UJ1 | 已下单用户 | 支付渠道回调 | 1. 收到通知 2. 幂等校验 3. 更新订单为已支付 | 订单已支付且重复通知不二次推进 |

## 功能需求（FR*）

| ID | 描述（系统必须… / 用户必须能够…） | 关联 UJ/E |
| --- | --- | --- |
| FR1 | 相同通知只推进一次订单状态 | UJ1 / S1 |
| FR2 | 迟到通知不改变已支付订单 | UJ1 / E1 |

## 非功能需求（NFR*）

| ID | 类别 | 要求 | 度量 |
| --- | --- | --- | --- |
| NFR1 | stability | 写库失败可安全重试 | 失败后状态保持待支付且可再次回调 |

## 边界与异常（E*）

| ID | 触发 | 期望 | 用户可见 |
| --- | --- | --- | --- |
| E1 | 已支付后迟到通知到达 | 返回已处理且状态不变 | 订单详情仍显示已支付 |

## 验收标准（A*）

| ID | Given | When | Then | verify |
| --- | --- | --- | --- | --- |
| A1 | 订单处于待支付 | 相同通知投递两次 | 状态只迁移一次 | CallbackIdempotencyTest |
| A2 | 订单处于已支付 | 迟到通知到达 | 响应为已处理且状态不变 | LateCallbackTest |

## 产品原型

无 UI：本切片为支付回调幂等，不提供 `prototype/index.html` 交互原型；见 `spec.uiRequired=false`。

## 补充场景（S*，可选）

| ID | 触发 | 结果 | 失败 |
| --- | --- | --- | --- |
| S1 | 同一通知到达两次 | 订单仍为已支付 | 写库失败时保持未支付 |

## 开放问题

无。烟测场景开放问题已全部闭合。
""",
        encoding="utf-8",
    )


def write_feature_tech_docs(
    feature_dir: Path,
    *,
    feature_id: str,
    requirement_id: str | None,
    path_name: str,
) -> None:
    """写出可审阅的薄 tech.md + tech-spec.md，并登记 diagrams 桩（兼任 Epic 时出图）。"""
    diagrams = feature_dir / "diagrams"
    arch_html = diagrams / "smoke.L1.architecture.html"
    arch_png = diagrams / "smoke.L1.architecture.png"
    write_archify_html(arch_html)
    write_preview_png(arch_png)

    if requirement_id:
        epic_line = f"`requirements/{requirement_id}/architecture/architecture.md`"
        epic_ref = (
            f"| L0/L1 | {epic_line} §四/§五 | 本切片仅改 CallbackHandler / IdempotencyStore |\n"
            f"| KD | Epic KD-001 | 本刀落地 notificationId 唯一键 |\n"
            f"| 接口/数据/埋点 | Epic §九～§十一 | 本刀新增去重表字段见 tech.yaml |\n"
            f"| 风险/NFR | Epic §六/§八 | 并发双写缓解落到本切片 |"
        )
        arch_section = (
            "相对 Epic：改动落在订单回调模块，不新增对外系统边界；"
            "依赖方向仍为 ChannelGateway → CallbackHandler → DB。"
        )
        layer_gaps = (
            f"L0/L1 总图见 Epic Design（requirements/{requirement_id}/architecture/）；"
            "本切片仅登记增量 L1 模块图。"
        )
    else:
        epic_line = "本文件兼任 Epic"
        epic_ref = (
            "| L0/L1 | 本文件兼任 Epic | 见 §四 与 diagrams/smoke.L1.architecture.* |\n"
            "| KD | 本文件 KD-F01 | 无独立 REQ architecture/ |\n"
            "| 接口/数据/埋点 | 本切片 tech.yaml | 完整合同在本目录 |\n"
            "| 风险/NFR | 本切片 §六 | 无 Epic 总册 |"
        )
        arch_section = (
            "无 requirements/：本薄 tech 兼任整需求上下文。"
            "外部系统为支付渠道网关；信任边界在回调入口鉴权之后。"
        )
        layer_gaps = (
            "小需求捷径：本切片兼任 L0 文字说明；"
            "L1 见图 diagrams/smoke.L1.architecture.png。"
        )

    (feature_dir / "tech.md").write_text(
        f"""# 切片技术方案（薄合同）：{feature_id}

> **定位**：Feature 交付切片技术落点合同。烟测生成，供人工核对 G2T 产物。

**Feature**：{feature_id}  
**关联需求**：{requirement_id or "单 feature 捷径"}  
**Epic Design**：{epic_line}  
**Version**：v0.1.0  
**日期**：2026-11-18  
**path**：{path_name}

---

## 变更记录

| 版本 | 日期 | 摘要 | 影响 |
| --- | --- | --- | --- |
| v0.1.0 | 2026-11-18 | 烟测初版 | — |

---

## 设计前置检查

- [x] 已读本切片 `prd.md` / `spec.yaml`
- [x] 已读 `tech-spec.md`
- [x] 若有 `requirementId`：已读 Epic Design 与 `split.yaml`
- [x] P0 `A*` 均有落点（§二 + `tech.yaml` acceptance）
- [x] 未重复开写 Epic 已定契约

---

## 一、简介与交付范围

| 项 | 内容 |
| --- | --- |
| 问题 | 重复支付回调会把订单推进两次 |
| 本切片交付 | A1/A2 可独立验收；Feature 对 G4 负责 |
| 非目标 | 不改支付渠道协议；无 UI |
| path | {path_name} |
| Story | 未启用 |

---

## 二、验收追溯

| ID | 摘要 | 技术落点（Epic 章节 / 本切片 § / Story / 接口） |
| --- | --- | --- |
| UJ1 / FR1 / A1 | 相同通知只推进一次 | §五 KD-F01 / POST /payments/callback |
| UJ1 / FR2 / A2 | 迟到通知不改变已支付 | §五 KD-F01 短路分支 / 同上 |

---

## 三、Epic 引用与本切片增量

| 类型 | 引用（Epic / 其它 Feature） | 本切片增量（只写差异） |
| --- | --- | --- |
{epic_ref}

---

## 四、本切片架构增量

### 4.1 相对 Epic 的架构说明

{arch_section}

### 4.2 本切片架构图（增量或引用内嵌）

![本切片架构 L1](diagrams/smoke.L1.architecture.png)

交互探索：`diagrams/smoke.L1.architecture.html`（Archify 合同桩，可替换为 finalize 真图）。

### 4.3 模块改动面

| 模块 | 本切片改动 | 说明 |
| --- | --- | --- |
| CallbackHandler | 修改 | 幂等短路 + 可重试失败 |
| IdempotencyStore | 新增 | notificationId 去重存储 |

---

## 五、本切片关键设计

| KD | 标题 | 相对 Epic | mustFollow 摘要 |
| --- | --- | --- | --- |
| KD-F01 | 回调幂等 | 新增/落地 | 以 notificationId 做幂等键 |

### KD-F01：回调幂等

- **问题**：渠道可能重放同一 notificationId，存在并发双写窗口。
- **决策**：DB 唯一键 + 事务内读改写。
- **核心链路**：回调进入 Handler → 按 notificationId 查重 → 命中则成功 ack；未命中则同事务写去重行并推进已支付。
- **必须遵守**：以 notificationId 为幂等键，命中则短路成功 ack。
- **坑**：不要用订单金额哈希替代 notificationId。

---

## 六、本切片约束与风险增量

| 维度 | 增量结论 | tech.yaml 字段 |
| --- | --- | --- |
| 风险 | 并发双写：DB 唯一键 + 事务 | `risks` |
| NFR | 稳定可重试；无常驻轮询 | `nfr` |
| 接口 | POST /payments/callback | `interfaces` |
| 数据 | t_payment_notification | `dataDesign` |
| 埋点 | pay_callback_success / callback_idempotent_hit | `tracking` |

architectureLayerGaps：{layer_gaps}

---

## 七、Story 与任务指引

| Story / 任务 | 写集 | 覆盖 A* | 说明 |
| --- | --- | --- | --- |
| （无 Story）T1 | app/src/order/callback/ | A1, A2 | G2T 后 scaffold 单任务 |

---

## 附录：与 tech.yaml / Epic / Story 对应

| 本文 | 下游 |
| --- | --- |
| §二 | `tech.yaml` acceptance → evidence / G4 |
| §三 / §四 | Epic `architecture/`；`diagrams` |
| §五 | `keyDesigns` / `aiConstraints` |
| §六 | `risks` / `nfr` / `interfaces` / `dataDesign` / `tracking` |
| §七 | `tasks.yaml` |
""",
        encoding="utf-8",
    )

    (feature_dir / "tech-spec.md").write_text(
        f"""# 技术约束（Tech Spec）：{feature_id}

> 本切片工程/边界约束。烟测生成。

## Tech Spec 前置检查

- [x] 与 `tech.md` / `tech.yaml` 一致
- [x] 未把 Epic 总册整份塞入本文

## 变更记录

| 版本 | 日期 | 摘要 |
| --- | --- | --- |
| v0.1.0 | 2026-11-18 | 烟测初版 |

## 一、工程与运行时约束

- 回调处理须在请求线程内完成幂等判定；禁止引入后台轮询补单。
- 写库失败返回可重试码，订单保持待支付。

## 二、模块边界与依赖

- **提供**：`CallbackHandler`（支付回调入口）
- **依赖**：订单状态机、DB 唯一约束
- **禁止**：跨模块直写订单金额哈希当幂等键

## 三、数据与存储约束

- 表 `t_payment_notification` 以 `notificationId` 为主键。
- 去重写入与订单状态推进须同事务。

## 四、安全与合规约束

- 不新增敏感字段落盘；回调鉴权沿用现网网关。

## 五、共享能力与外部依赖

- 外部：支付渠道网关（ChannelGateway）
- 无新增三方 SDK
""",
        encoding="utf-8",
    )

    tech = yaml.safe_load(valid_tech())
    assert isinstance(tech, dict)
    tech["diagrams"] = [
        {
            "id": "D-SMOKE-L1",
            "type": "architecture",
            "layer": 1,
            "title": "本切片 L1 增量",
            "scope": "CallbackHandler / IdempotencyStore",
            "tool": "archify",
            "html": "diagrams/smoke.L1.architecture.html",
            "png": "diagrams/smoke.L1.architecture.png",
        }
    ]
    tech["diagramsNoneReason"] = ""
    tech["architectureLayerGaps"] = layer_gaps
    write_yaml(feature_dir / "tech.yaml", yaml.safe_dump(tech, allow_unicode=True, sort_keys=False))


def write_requirement_prd(path: Path, *, req_id: str, feature_id: str) -> None:
    # 确保 REQ_PRD_H2 标题齐全且有可读正文
    body_by_title = {
        "背景与目标": (
            "- **问题**：支付渠道重放导致订单重复推进。\n"
            "- **目标**：整需求下回调幂等成立，可拆为单 Feature 交付。\n"
            "- **价值**：账务一致、降低资损风险。"
        ),
        "范围与非目标": (
            "- **In Scope**：回调幂等与迟到通知短路。\n"
            "- **Out of Scope**：渠道协议改造、UI、轮询补单。\n"
            "- **约束与假设**：现有订单状态机可用。"
        ),
        "核心用户旅程总览": (
            "| 旅程 | 角色 | 端到端成功结果 | 建议落入 feature |\n"
            "| --- | --- | --- | --- |\n"
            f"| 回调幂等主路径 | 已下单用户 | 重复通知不二次推进 | {feature_id} |"
        ),
        "功能与非功能总览": (
            "- **功能要点**：相同 notificationId 只成功一次；迟到通知 ack。\n"
            "- **非功能要点**：写库失败可重试；无常驻任务。\n"
            "- **明确无 / 延后**：无 UI。"
        ),
        "边界与异常总览": "- 已支付后迟到通知：状态不变并返回已处理。",
        "验收总览": (
            "| 验收 | 摘要 | Feature |\n"
            "| --- | --- | --- |\n"
            f"| A1/A2 | 幂等与迟到短路 | {feature_id} |"
        ),
        "Feature 拆分依据": (
            f"单一切片即可独立 G4；见 `split.yaml` decision=single，feature=`{feature_id}`。"
        ),
        "整需求架构": (
            "见同目录 `architecture/architecture.md`（Epic Design，check-req 硬门槛）。"
        ),
        "开放问题": "无。",
    }
    lines = [
        f"# 需求：支付回调幂等（插件大需求烟测）",
        "",
        "> 烟测生成的需求级 PRD，供人工打开核对。",
        "",
        "| 字段 | 值 |",
        "| --- | --- |",
        f"| Requirement ID | {req_id} |",
        "| 状态 | 可拆分 |",
        "| 建议 path | light |",
        "",
    ]
    for title in REQ_PRD_H2:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(body_by_title[title])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_req_architecture_expands(
    arch: Path,
    *,
    req_id: str,
    feature_ids: list[str] | tuple[str, ...],
    domain: str = "english-learning",
) -> None:
    """按 templates/design/ 落盘 Epic §八～§十一强制展开件（烟测写满可审内容）。"""
    arch.mkdir(parents=True, exist_ok=True)
    feats = list(feature_ids)
    owner = feats[0] if feats else "FEAT-unknown"
    feat_list = " / ".join(feats) if feats else owner

    if domain == "english-learning":
        nfr = f"""# NFR 技术评估：{req_id}

> **定位**：无痛学环整需求快稳省量化展开件；摘要见 `architecture.md` §八。  
> **关联 Feature**：{feat_list}  
> **日期**：2026-11-18

---

### 8.1 算法评估（如适用）

N/A：本需求无推荐/检测/生成类 ML 算法；复习队列为确定性日快照 + 本地规则，不引入模型指标。

### 8.2 功耗评估（必须量化，基于场景）

| 场景 | 平均电流增量 (mA) | 时长 (s) | 单次 (mAh) | 日频次 | 日增量 (mAh) |
| --- | --- | --- | --- | --- | --- |
| 打开今日复习并打卡 20 词 | ≤8 | ≤180 | ≤0.4 | 1 | ≤0.4 |
| 收藏/取消收藏 | ≤3 | ≤2 | ≤0.002 | ≤10 | ≤0.02 |
| 打开连续进度页 | ≤4 | ≤15 | ≤0.017 | 1 | ≤0.017 |

- **Top 5% 模型**：日打卡 3 轮 × 20 词；日增量仍 ≪ 5 mAh。
- **降级**：无后台轮询；弱设备仅延后非关键动效。

### 8.3 性能评估（必须量化，基于场景）

| 场景 | 设备基线 | 目标 | 测量点 |
| --- | --- | --- | --- |
| 复习首词可见 | 中端 Android | p95 ≤500ms（冷启动放宽 1s） | QueueStore 读快照 → UI bind |
| 打卡推进下一词 | 同上 | p95 ≤120ms | CheckIn 写盘 + 游标推进 |
| 收藏幂等写 | 同上 | p95 ≤80ms | Notebook UNIQUE 命中/插入 |
| 连续天数读取 | 同上 | p95 ≤100ms | Streak 缓存表或按日聚合 |

#### 验收标准汇总

| 指标 | 门槛 |
| --- | --- |
| 首词可见 | ≤500ms（暖） |
| 打卡写成功反馈 | ≤120ms |
| 无 ANR / 主线程磁盘大扫 | 必须 |

#### 降级策略（必须）

| 触发 | 策略 |
| --- | --- |
| 队列 >200 | 分页/分批 bind，禁止一次 inflate 全部卡片 |
| 磁盘写失败 | 提示可重试；不推进游标 |

### 8.4 内存评估（必须量化，基于场景）

| 场景 | 增量 RSS 目标 | 说明 |
| --- | --- | --- |
| 复习会话 20 词 | ≤15 MB | 仅当前卡 + 邻卡预取 |
| 生词本列表 500 条 | ≤25 MB | RecyclerView + Diff |

### 8.5 安全评估（如适用）

| 项 | 结论 |
| --- | --- |
| 用户数据 | 词本/打卡本地库；无明文上传证件类敏感字段 |
| 权限 | 不新增敏感权限 |
| 埋点 | wordId 非 PII；禁止上报整句用户笔记 |

### 8.6 兼容性评估（必须）

| 项 | 要求 |
| --- | --- |
| minSdk | 不降低；Room/SQLite 迁移向前兼容 |
| 多进程 | 单进程写；无跨进程脏读假设 |
| 备份 | 跟随应用默认备份策略；表结构变更走 Migration |

### 8.7 RomSize 增量评估（必须）

| 项 | 估算 |
| --- | --- |
| 代码 + 资源 | ≤80 KB |
| 空库 schema | ≤16 KB |
| 合计 | ≤100 KB |
"""
        interface = f"""# 接口设计：{req_id}

> **定位**：整需求跨 Feature / 模块 API 展开件；摘要见 `architecture.md` §九。  
> **关联 Feature**：{feat_list}  
> **日期**：2026-11-18

---

### 9.1 对外提供的接口

#### 9.1.1 接口清单

| 接口ID | 接口名称 | 接口类型 | 所属模块/Feature | 消费方 | 规约位置 |
| --- | --- | --- | --- | --- | --- |
| API-F1 | favorite | 函数调用 | {feats[0] if len(feats) > 0 else owner} | 词卡 UI | Owner tech.yaml interfaces |
| API-R1 | getTodayQueue | 函数调用 | {feats[1] if len(feats) > 1 else owner} | 复习 UI | Owner tech.yaml |
| API-R2 | checkIn | 函数调用 | {feats[1] if len(feats) > 1 else owner} | 复习 UI | Owner tech.yaml |
| API-S1 | getStreak | 函数调用 | {feats[2] if len(feats) > 2 else owner} | 进度 UI | Owner tech.yaml |

#### 9.1.2 关键接口详述

##### API-R1：getTodayQueue

- **接口类型**：函数调用
- **所属模块**：DailyReview
- **消费方**：今日复习页
- **接口描述**：返回当日队列快照；当日不重排。
- **请求/调用**：

```
getTodayQueue(day: LocalDate = today): QueueSnapshot
参数：
  - day：LocalDate — 自然日；默认今天
```

- **响应/返回值**：

```
QueueSnapshot
字段：
  - day：LocalDate
  - wordIds：List<String>
  - cursor：Int
```

- **错误码/异常**：

| 错误码 | 含义 | 处理建议 |
| --- | --- | --- |
| EMPTY | 无到期词 | 展示空态，不进会话 |
| IO | 读库失败 | Toast + 可重试 |

- **并发/幂等/版本约束**：同日多次调用返回同一快照；禁止中途重算顺序。
- **能力边界来源**：→ Owner `tech-spec.md` §三

### 9.2 依赖的外部接口

#### 9.2.1 外部接口清单

| 接口ID | 接口名称 | 接口类型 | 提供方 | 所属 Feature | 规约位置 |
| --- | --- | --- | --- | --- | --- |
| — | N/A | — | — | — | 本需求无云端/第三方接口 |

#### 9.2.2 关键外部接口详述

N/A。

### 9.3 接口一致性自检

- §9.1 均可追溯到对应 Feature `tech.yaml` → `interfaces`
- 无外部接口依赖，与 architecture 外部依赖清单一致（无）
- 打卡/收藏幂等错误语义已在风险与 E* 覆盖
- 版本兼容：本地 API，随 App 版本发布，无独立接口版本号
"""
        database = f"""# 数据库设计：{req_id}

> **定位**：整需求库表展开件；摘要见 `architecture.md` §十。  
> **关联 Feature**：{feat_list}  
> **日期**：2026-11-18

---

### 10.1 数据库概览

#### 10.1.1 数据存储清单

| 存储ID | 存储名称 | 存储类型 | 所属 Feature | 表/集合数量 | 规约位置 |
| --- | --- | --- | --- | --- | --- |
| DB-001 | study_local | Room/SQLite | 多 Feature 共享库 | 4 | 各 Owner tech-spec §四 |

#### 10.1.2 数据库 ER 图（推荐）

> 表关系：NotebookEntry(wordId) ←供词— ReviewQueueDay / CheckIn；CheckIn 活跃日 → StudyStreak。  
> 正式 ER 图可按需补 Archify `erd`；本烟测以字段详表为准。

### 10.2 数据表详细设计

#### 10.2.1 t_notebook_entry

- **所属模块**：Notebook
- **所属 Feature**：{feats[0] if feats else owner}
- **用途描述**：生词本收藏；`wordId` 唯一。

##### 字段设计

| 字段名 | 类型 | 是否必填 | 默认值 | 说明 | 约束 |
| --- | --- | --- | --- | --- | --- |
| `id` | INTEGER | 是 | 自增 | 主键 | PRIMARY KEY |
| `wordId` | TEXT | 是 | — | 词条 ID | UNIQUE NOT NULL |
| `createdAt` | INTEGER | 是 | — | epoch ms | NOT NULL |

##### 索引设计

| 索引名 | 索引字段 | 索引类型 | 用途说明 |
| --- | --- | --- | --- |
| `uidx_notebook_word` | wordId | UNIQUE | 收藏幂等 |

##### 版本迁移

| 版本号 | 变更内容 | 迁移策略 |
| --- | --- | --- |
| v1 | 初始建表 | CREATE |

#### 10.2.2 t_review_queue_day

- **所属模块**：DailyReview
- **所属 Feature**：{feats[1] if len(feats) > 1 else owner}
- **用途描述**：自然日队列快照。

##### 字段设计

| 字段名 | 类型 | 是否必填 | 默认值 | 说明 | 约束 |
| --- | --- | --- | --- | --- | --- |
| `day` | TEXT | 是 | — | yyyy-MM-dd | PRIMARY KEY |
| `wordIdsJson` | TEXT | 是 | — | 有序 wordId 列表 | NOT NULL |
| `cursor` | INTEGER | 是 | 0 | 当前进度 | NOT NULL |

##### 索引设计

| 索引名 | 索引字段 | 索引类型 | 用途说明 |
| --- | --- | --- | --- |
| — | day | PK | 按日读取 |

##### 版本迁移

| 版本号 | 变更内容 | 迁移策略 |
| --- | --- | --- |
| v1 | 初始建表 | CREATE |

#### 10.2.3 t_review_checkin

- **所属模块**：DailyReview
- **所属 Feature**：{feats[1] if len(feats) > 1 else owner}
- **用途描述**：打卡幂等记录。

##### 字段设计

| 字段名 | 类型 | 是否必填 | 默认值 | 说明 | 约束 |
| --- | --- | --- | --- | --- | --- |
| `day` | TEXT | 是 | — | 自然日 | PK 组合 |
| `wordId` | TEXT | 是 | — | 词条 | PK 组合 |
| `result` | TEXT | 是 | — | known/unknown | NOT NULL |
| `updatedAt` | INTEGER | 是 | — | epoch ms | NOT NULL |

##### 索引设计

| 索引名 | 索引字段 | 索引类型 | 用途说明 |
| --- | --- | --- | --- |
| `pk_checkin` | day, wordId | UNIQUE | 幂等键 |

##### 版本迁移

| 版本号 | 变更内容 | 迁移策略 |
| --- | --- | --- |
| v1 | 初始建表 | CREATE |

#### 10.2.4 t_study_streak

- **所属模块**：Streak
- **所属 Feature**：{feats[2] if len(feats) > 2 else owner}
- **用途描述**：连续天数缓存，可自打卡表重建。

##### 字段设计

| 字段名 | 类型 | 是否必填 | 默认值 | 说明 | 约束 |
| --- | --- | --- | --- | --- | --- |
| `id` | INTEGER | 是 | 1 | 单行缓存 | PRIMARY KEY |
| `currentStreak` | INTEGER | 是 | 0 | 连续天数 | NOT NULL |
| `lastActiveDay` | TEXT | 否 | — | 最近活跃日 | — |

##### 索引设计

| 索引名 | 索引字段 | 索引类型 | 用途说明 |
| --- | --- | --- | --- |
| — | id | PK | 单行 |

##### 版本迁移

| 版本号 | 变更内容 | 迁移策略 |
| --- | --- | --- |
| v1 | 初始建表 | CREATE |

### 10.3 数据设计说明

- **数据一致性**：本地 Single Source of Truth；Streak 可从 CheckIn 重建
- **缓存策略**：日队列快照当日有效；跨日重建
- **数据生命周期**：用户清除数据时级联清空四表
- **数据迁移策略**：Room Migration 递增；禁止破坏性 DROP 无备份
- **敏感数据处理**：无 PII 字段；埋点仅 wordId

### 10.4 数据库设计一致性自检

- 四表均可追溯到各 Feature `tech-spec` / `tech.yaml` dataDesign
- 与领域概念 Notebook / Queue / CheckIn / Streak 一致
- UNIQUE 幂等键已标注
- 迁移与 nfr.md §8.6 一致
- 无敏感明文字段
"""
        tracking = f"""# 埋点技术方案：{req_id}

> **定位**：整需求埋点展开件；摘要见 `architecture.md` §十一。  
> **关联 Feature**：{feat_list}  
> **日期**：2026-11-18

---

### 11.1 埋点事件与字段规约

| 埋点需求来源 | app_id | event_id | 事件名称描述 | 字段 ID | 字段描述 | 值数据类型 | 字段值范围 | 字段长度 | 字段示例 | 触发条件/机制 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 产品 | 2006 | notebook_favorite | 收藏成功或已存在 | wordId | 词条 ID | String | 非空 | 64 | w_1001 | 收藏写库成功回调 |
| 产品 | 2006 | review_session_start | 进入非空复习会话 | queueSize | 队列长度 | Int | ≥1 | — | 20 | 首词可见且队列非空 |
| 产品 | 2006 | review_checkin_write | 打卡落盘 | wordId | 词条 ID | String | 非空 | 64 | w_1001 | CheckIn UNIQUE 写入成功 |
| 产品 | 2006 | study_streak_view | 打开连续进度 | currentStreak | 连续天数 | Int | ≥0 | — | 7 | 进度页 onResume |

### 11.2 埋点一致性自检（推荐）

- 与各 Feature spec / tech.yaml tracking 无冲突
- 无笔记正文等敏感字段上报
- 采样率默认 100%；与 nfr 功耗评估一致（事件极少）
"""
    else:
        # 通用占位：仍须齐标题
        nfr = f"# NFR：{req_id}\n\n" + "\n".join(
            f"### {h}\n\nN/A。\n" for h in REQ_ARCH_EXPAND_FILES["nfr.md"]
        )
        interface = f"# 接口：{req_id}\n\n" + "\n".join(
            f"### {h}\n\nN/A。\n" for h in REQ_ARCH_EXPAND_FILES["interface-design.md"]
        )
        database = f"# 库表：{req_id}\n\n" + "\n".join(
            f"### {h}\n\nN/A。\n" for h in REQ_ARCH_EXPAND_FILES["database-design.md"]
        )
        tracking = f"# 埋点：{req_id}\n\n" + "\n".join(
            f"### {h}\n\nN/A。\n" for h in REQ_ARCH_EXPAND_FILES["analytics-tracking.md"]
        )

    (arch / "nfr.md").write_text(nfr, encoding="utf-8")
    (arch / "interface-design.md").write_text(interface, encoding="utf-8")
    (arch / "database-design.md").write_text(database, encoding="utf-8")
    (arch / "analytics-tracking.md").write_text(tracking, encoding="utf-8")


def write_requirement_architecture(req_dir: Path, *, req_id: str, feature_id: str) -> None:
    arch = req_dir / "architecture"
    diagrams = arch / "diagrams"
    write_archify_html(diagrams / "req.L0.architecture.html")
    write_preview_png(diagrams / "req.L0.architecture.png")
    write_archify_html(diagrams / "req.L1.architecture.html")
    write_preview_png(diagrams / "req.L1.architecture.png")

    sections: dict[str, str] = {
        "变更记录（增量变更）": (
            "| 版本 | 日期 | 变更范围 | 摘要 | 影响模块 | 是否回滚设计 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| v0.1.0 | 2026-11-18 | REQ | 烟测初版 | 回调模块 | 否 |"
        ),
        "设计前置检查": (
            "- [x] 已读需求级 prd / split\n"
            "- [x] 跨 Feature 共享能力：本需求仅单 Feature\n"
            "- [x] P0 A1/A2 由 KD-001 与 L1 覆盖"
        ),
        "一、简介": "整需求技术方案总册：支付回调幂等。不对 G4 负责；交付在 Feature。",
        "二、需求概述": "渠道重放 → 订单侧以 notificationId 去重 → 可重试失败语义。",
        "三、领域模型": "订单、支付通知（notificationId）、回调会话。",
        "四、零层架构（L0）": (
            "外部：支付渠道网关。本系统：订单服务回调入口。\n\n"
            "![L0](diagrams/req.L0.architecture.png)"
        ),
        "五、一层架构（L1）": (
            "模块：CallbackHandler、IdempotencyStore、OrderStateMachine。\n\n"
            "![L1](diagrams/req.L1.architecture.png)"
        ),
        "六、技术风险与边界场景": "并发双写窗口；迟到通知；写库失败可重试。",
        "七、关键功能与疑难点/亮点设计": (
            "KD-001 回调幂等：DB 唯一键 + 事务内读改写；mustFollow=notificationId 幂等键。"
        ),
        "八、技术评估（NFR）": "稳定优先；无常驻轮询；功耗可忽略。",
        "九、接口设计": "POST /payments/callback；成功 ack / 5xx 可重试。",
        "十、数据库设计": "t_payment_notification(notificationId PK, orderId)。",
        "十一、埋点技术方案": "pay_callback_success；callback_idempotent_hit。",
        "十二、Feature 与 Story 拆解索引": f"| {feature_id} | 主交付切片 | 无 Story |",
        "十三、Story 详细设计索引": "未启用 Story。",
        "附录：与 Feature tech / Story / tasks 的对应关系": (
            f"Epic 总册 → `{feature_id}/tech.md` 薄增量 → tasks.yaml → evidence。"
        ),
    }
    lines = [
        f"# 需求级技术方案（Epic Design）：{req_id}",
        "",
        "> 烟测生成的 Epic Design，供人工打开核对 check-req 产物。",
        "",
        f"**Requirement**：{req_id}",
        "**设计 Version**：v0.1.0",
        "**日期**：2026-11-18",
        "",
    ]
    for title in REQ_ARCH_H2:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(sections[title])
        lines.append("")
    (arch / "architecture.md").write_text("\n".join(lines), encoding="utf-8")

    doc = {
        "requirementId": req_id,
        "summary": "支付回调幂等整需求上下文与模块归属（插件烟测）",
        "features": [feature_id],
        "contracts": [],
        "contractsNoneReason": "单 Feature，无跨切片契约",
        "keyDesigns": [
            {
                "id": "KD-001",
                "title": "回调幂等",
                "summary": "notificationId 唯一键 + 事务",
            }
        ],
        "keyDesignsNoneReason": "",
        "risks": [
            {
                "id": "R1",
                "description": "并发双写",
                "impact": "状态抖动",
                "mitigation": "DB 唯一键",
            }
        ],
        "risksNoneReason": "",
        "openTechQuestions": [],
        "diagrams": [
            {
                "id": "D-L0",
                "type": "architecture",
                "layer": 0,
                "title": "L0",
                "scope": "外部边界",
                "tool": "archify",
                "html": "diagrams/req.L0.architecture.html",
                "png": "diagrams/req.L0.architecture.png",
            },
            {
                "id": "D-L1",
                "type": "architecture",
                "layer": 1,
                "title": "L1",
                "scope": "模块归属",
                "tool": "archify",
                "html": "diagrams/req.L1.architecture.html",
                "png": "diagrams/req.L1.architecture.png",
            },
        ],
        "diagramsNoneReason": "",
    }
    (arch / "architecture.yaml").write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def write_split(req_dir: Path, *, req_id: str, feature_id: str, path_name: str) -> None:
    split = {
        "requirementId": req_id,
        "decision": "single",
        "rationale": "验收同窗上线，单一切片即可 G4（插件烟测）",
        "confirmedByHuman": False,
        "features": [
            {
                "id": feature_id,
                "title": "支付回调幂等主切片",
                "scope": "无 UI 回调幂等，覆盖 A1–A2",
                "path": path_name,
                "dependsOn": [],
            }
        ],
    }
    (req_dir / "split.yaml").write_text(
        yaml.safe_dump(split, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _prepare_feature(
    root: Path,
    feature_id: str,
    *,
    path_name: str,
    requirement_id: str | None = None,
) -> Path:
    feature = init_feature(root, feature_id, requirement_id=requirement_id)
    set_path(feature, path_name)
    adopt_role(feature, "product")
    write_yaml(feature / "spec.yaml", valid_spec().replace("id: CH-014", f"id: {feature_id}"))
    write_feature_prd(
        feature / "prd.md",
        feature_id=feature_id,
        requirement_id=requirement_id,
        path_name=path_name,
    )
    return feature


def _advance_feature_to_gd(feature: Path, *, path_name: str, requirement_id: str | None) -> None:
    accept_gate(feature, "G0")
    accept_gate(feature, "G1")
    adopt_role(feature, "architect")
    accept_gate(feature, "G2")
    write_feature_tech_docs(
        feature,
        feature_id=feature.name,
        requirement_id=requirement_id,
        path_name=path_name,
    )
    accept_gate(feature, "G2T")
    # 主控不在 adopt 菜单；tasks scaffold 由测试代跑
    scaffold_tasks(feature, mode="single", force=True)
    accept_gate(feature, "G3")
    adopt_role(feature, "reviewer")
    write_yaml(feature / "review.yaml", valid_review())
    accept_gate(feature, "GR")
    adopt_role(feature, "tester")
    write_yaml(feature / "evidence.yaml", valid_evidence())
    accept_gate(feature, "G4")
    adopt_role(feature, "deployer")
    write_yaml(feature / "deploy.yaml", valid_deploy())
    accept_gate(feature, "GD")


def write_scenario_readme(scenario_dir: Path, title: str, bullets: list[str]) -> None:
    lines = [f"# {title}", "", "本目录由 `tests.test_plugin_smoke` 每次运行重新生成。", "", "## 请打开核对", ""]
    for item in bullets:
        lines.append(f"- {item}")
    lines.append("")
    (scenario_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def run_small_light() -> Path:
    from tests.smoke_small_vocab import run_small_light as _run

    root = reset_scenario(SCENARIO_SMALL_LIGHT)
    return _run(root, FEATURE_SMALL_LIGHT)


def run_small_light_auto() -> Path:
    from tests.smoke_small_vocab import run_small_light_auto as _run

    root = reset_scenario(SCENARIO_SMALL_LIGHT_AUTO)
    return _run(root, FEATURE_SMALL_LIGHT_AUTO)


def run_large_requirement() -> tuple[Path, list[Path]]:
    """大需求：无痛学环 3 Feature，全程自动、产物不省略。"""
    from tests.smoke_english_app import run_english_learning_large_requirement

    root = reset_scenario(SCENARIO_LARGE_REQ)
    return run_english_learning_large_requirement(root)


def write_smoke_index() -> Path:
    root = smoke_root()
    index = root / "README.md"
    index.write_text(
        """# 插件烟测产物（自动生成）

每次运行：

```bash
python -m unittest tests.test_plugin_smoke -v
```

会**清空并重建**下列场景目录，写出可打开核对的阶段产物（不是临时目录占位）。

| 目录 | 场景 |
| --- | --- |
| `01-small-light/` | 小需求 light：语境卡收藏生词本（真图） |
| `02-small-light-auto/` | 小需求 light-auto：同上连跑 |
| `03-large-req/` | 大需求：无痛学环 3 Feature（收藏+复习+进度，全产物） |

说明：

- 全部场景对标无痛单词真实需求文案；**禁止空壳图 /「测试占位」正文**。
- 图来自 `tests/fixtures/smoke-diagrams/out/`（Archify finalize + export PNG）。
- 全程自动，无需人选角色/路径/视觉。
- 本目录默认 gitignore；夹具真图在 tests/fixtures 可入库。
""",
        encoding="utf-8",
    )
    return index


def feature_stage_files(feature_dir: Path) -> dict[str, list[Path]]:
    """各阶段期望存在的关键产物。"""
    return {
        "G1": [feature_dir / "prd.md", feature_dir / "spec.yaml"],
        "G2T": [
            feature_dir / "tech.md",
            feature_dir / "tech-spec.md",
            feature_dir / "tech.yaml",
            feature_dir / "diagrams" / "vocab.L1.architecture.html",
            feature_dir / "diagrams" / "vocab.L1.architecture.png",
        ],
        "G3": [feature_dir / "tasks.yaml"],
        "GR": [feature_dir / "review.yaml"],
        "G4": [feature_dir / "evidence.yaml"],
        "GD": [feature_dir / "deploy.yaml"],
        "board": [feature_dir / "BOARD.md", feature_dir / "state.json"],
    }


def assert_files_exist(paths: list[Path]) -> None:
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise AssertionError("缺少产物:\n" + "\n".join(missing))


def assert_markdown_has_substance(path: Path, *, min_chars: int = 400) -> None:
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < min_chars:
        raise AssertionError(f"{path} 内容过短（{len(text)}），疑似未真正落盘")
    for banned in ("（测试占位", "Smoke Archify stub", "待填写", "[……]", "[谁、痛点"):
        if banned in text:
            raise AssertionError(f"{path} 仍含未填充模板痕迹: {banned}")


def assert_real_diagram_pair(html: Path, png: Path) -> None:
    if not html.is_file() or html.stat().st_size < 100_000:
        raise AssertionError(f"假图或不完整 HTML: {html}")
    if not png.is_file() or png.stat().st_size < 50_000:
        raise AssertionError(f"假图或不完整 PNG: {png}")
    body = html.read_text(encoding="utf-8", errors="ignore")
    if "Smoke Archify stub" in body:
        raise AssertionError(f"{html} 仍是空壳桩")
    if "archify" not in body.lower():
        raise AssertionError(f"{html} 缺少 Archify 溯源")
