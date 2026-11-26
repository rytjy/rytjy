# MCP server 审计记录

> 配套文章：[`notes/mcp-audit-2026-11.md`](../../notes/mcp-audit-2026-11.md)
> 三个目标、三份记录：`@modelcontextprotocol/server-filesystem 2.4.0` · `mcp-server-fetch 2026.11.18` · `mcp-server-git 2026.11.18`

每份记录包含四样东西：

1. **产物核验**：下载的 wheel/tarball 的 sha256，与 registry 上登记的摘要是否一致；
2. **源码定位**：防线的 `文件:行`；
3. **运行用例与原始输出**：脚本在 `fetch/`、`git/` 下，输出在同目录的 `runtime_out*.txt`；
4. **未测面**：这份记录**不覆盖**什么。

## 边界

- 三份结论都是**阴性**：在列出的用例上没绕过去；不是「已防住」的背书。
- 不含 0day，不包含可直接复制的利用步骤。
- 环境：Linux，Python 3.12，git 2.43.0；具体版本见各文件。
- 记录按当天实际运行写；跑不通的一律标「未测」，没有补写成成功。

## 文件

| 文件 | 目标 | 要点 |
|---|---|---|
| [`2026-11-25-fs-001.md`](2026-11-25-fs-001.md) | server-filesystem 2.4.0 | 路径越界 7 例全拒（含符号链接、`/proc`） |
| [`2026-11-25-fetch-002.md`](2026-11-25-fetch-002.md) | mcp-server-fetch 2026.11.18 | 12 行 + 4 组补测：分类/连接两层拒私网；重定向逐跳过钩子；rebinding 为**模拟** |
| [`2026-11-26-git-003.md`](2026-11-26-git-003.md) | mcp-server-git 2026.11.18 | 路径限制、flag 守卫、`harden_repo` 挡住真实 hook 与 submodule filter（两者基线均可执行） |
