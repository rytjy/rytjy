# MCP 审计回归包

版本一变就跑同一套用例，输出一张差异表。三个案例：server-filesystem、mcp-server-fetch、mcp-server-git。

## 用法

```bash
cd audit/mcp/regress
python3 regress.py            # 跑全部
python3 regress.py --case git-003
```

退出码：`0` 全部命中且版本未变；`1` 有失败或版本变了；环境错误看 traceback。

## 输出

`results/<YYYYmmdd-HHMMSS>/`：

- `<case>-<run>.txt`：那一轮的原样输出（stdout+stderr）；
- `SUMMARY.md`：每案一行（版本 本次/基线 · 通过数 · 状态）+ 逐条 PASS/FAIL。

## 判定规则

- 每个断言是输出里的**行级正则**（`re.M` 多行模式），命中即 PASS。断言写在 `cases.json` 的 `runs[].checks`。
- 每案记录一个 `version.baseline`。实测版本与基线不同 → `VERSION CHANGED`，退出码 1，**先人工看差异再改基线**。
- 断言里保留「基线也执行」的对照项（如 `T3a ... marker: True`）：如果哪天基线不再执行，说明测试床坏了，而不是被审计对象变安全了。

## 加一个案例

在 `cases.json` 加一项：

```json
{
  "id": "pkg-004",
  "title": "...",
  "cwd": "audit/mcp/xxx",
  "version": {"kind": "pip", "dist": "pkg-name", "python": ".venv/bin/python", "baseline": "1.2.3"},
  "runs": [{"name": "base", "cmd": [".venv/bin/python", "runtime_test.py"], "timeout": 180,
            "checks": [["说明", "^正则"]]}]
}
```

## 现状（2026-11-26 首跑）

| 案例 | 版本 | 通过 |
|---|---|---|
| fs-001 | 2.4.0 | 7/7 |
| fetch-002 | 2026.11.18 | 15/15 |
| git-003 | 2026.11.18 | 16/16 |


## 复现前提（公开版说明）

这份包是在审计机上跑的，`cases.json` 里的 `cwd` 对应当时的目录布局：

```
audit/mcp/fs/      解包后的 server-filesystem + sandbox/
audit/mcp/fetch/   venv + 已安装的 mcp-server-fetch + runtime_test*.py
audit/mcp/git/     venv + 已安装的 mcp-server-git + runtime_test*.py
```

`scripts/` 里是原样复制的 harness（fs 的 `t2.mjs`、fetch 的两支、git 的三支），方便照着重搭。
换机器时只需要改两处：把三个包按 `cases.json` 里的版本装进各自的 venv，以及把 `cwd` 指到你自己的目录。
`scripts/` 里的脚本写死了 `/tmp/case003*` 这类临时目录（git 那几支），跑之前确认可写。
