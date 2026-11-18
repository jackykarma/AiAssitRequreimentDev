# UI Kit 动效 / 特效标准合同

所有可人选 kit（`ui-kit` / `painless` / `midoo` / 后续注册项）须对齐本文件。  
令牌用各自前缀（`uk` / `pk` / `md`），**语义同名**。

## 1. 必有令牌

| 语义 | 令牌后缀 | 推荐值 | 用途 |
| --- | --- | --- | --- |
| 标准缓动 | `--{p}-ease` | `cubic-bezier(0.22, 1, 0.36, 1)` | 通用过渡 |
| 标准时长 | `--{p}-duration` | `240–280ms` | 颜色/透明度/位移 |
| 快速 | `--{p}-duration-fast` | `160–180ms` | 按压缩放 |
| 慢速 | `--{p}-duration-slow` | `320–400ms` | sheet / 入场 |
| 按压缩放 | `--{p}-press-scale` | `0.96` | 可点控件 active |
| 玻璃模糊 | `--{p}-blur-glass` | `16–24px` | 底栏/毛玻璃 |
| 防剧透模糊 | `--{p}-blur-spoiler` | `4 / 7 / 10px`（soft/base/strong） | 有则必须可揭晓 |

## 2. 必有行为类（或等价实现）

| 行为 | 约定 | 备注 |
| --- | --- | --- |
| 按压反馈 | `.{p}-pressable:active { transform: scale(var(--{p}-press-scale)) }` | CTA / FAB / 卡片 |
| 模糊揭晓 | `.{p}-blur-text` → `.is-revealed`；过渡 `filter` + `--{p}-duration` | 无防剧透可省略类，但勿另造马赛克 |
| Sheet 入场 | 自下而上 + scrim 淡入，用 `--{p}-duration-slow` | 词气泡 / 半屏 |
| Toast | 上浮淡入，`--{p}-duration` | 可选 |
| 入场 | `.{p}-fade-up` opacity+translateY | 列表卡可选 |

## 3. 无障碍

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

各 kit 的 `components.css`（或 `motion.css`）须包含上述规则。

## 4. 写入 ux.yaml

复杂/产品相关动效另记 `visual.motion`（`M*`：`trigger` / `effect`）。  
kit 级通用按压/揭晓不必逐条写进 `M*`，但 THEME.md 须有「动效」节指向本合同。

## 5. 禁止

- 各 kit 自造互不兼容的时长语义（如把 `duration` 当 80ms 微交互）
- 用 `visibility:hidden` / 纯色块冒充防剧透模糊
- 忽略 `prefers-reduced-motion`
