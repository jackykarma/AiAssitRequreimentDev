# 需求级架构草图（可选，非整需求 G2T 合同）

本目录存放**整条需求维度**的架构思考产物：模块边界、跨 feature 契约、依赖方向、同发/先后关系。  
各 feature 的 G2T 仍以 `features/<id>/tech.md` + `tech.yaml` 为准；此处不代替切片技术方案。

## 绘图约定

- 工具：[Archify](https://github.com/tt-a1i/archify)
- 仓库内只保留 `.html`（交互）与 `.svg`（静态）；不提交 PNG/JPG/WebP 等
- 建议文件名：`<REQ-id>.overview.architecture.html` / `.svg`

## 建议内容

1. 端到端主路径与信任边界
2. 各 feature 归属模块与 `dependsOn` 方向
3. 先发 feature 须冻结的接口 / 数据契约

在需求级 `prd.md` 的「整需求架构草图」一节链接到本目录产物。
