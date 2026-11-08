# 变更 API

由主控代跑；用户不必手敲。

```bash
python -m pip install -e .
python -m aiassitrequreimentdev init <变更编号>
python -m aiassitrequreimentdev check <feature 目录> [--gate G0|G1|G2|G2T|G3|GR|G4|GD]
python -m aiassitrequreimentdev seal <feature 目录>
```

退出码 0 表示所选门禁（或全部）无违反项；非 0 时 stdout 每行：`门禁 错误码 说明`。
