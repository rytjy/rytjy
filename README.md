# rytjy

Read-only Solidity review. Evidence first.

I read small DeFi codebases closely and write up what I find — every item carries a `file:line`
I re-read, an honest coverage label, and an explicit "unverified" tag where I couldn't prove it.

## Standards

1. Every claim carries a `file:line` that I re-read. No "somewhere around here".
2. "The fix is present" ≠ "the fix is correct" — kept separate, always.
3. Reports state what I did **not** read (`coverage: X/Y SLOC`). Below 30% I say it doesn't
   support a conclusion.

## Public work

**Method — reproducible**
[`ov-harness`](https://github.com/rytjy/ov-harness) — *is the claimed fix commit actually in the
reviewed revision?* (EN/ZH, with a runnable script)

**Toolkit — backtest audit · 回测审计**
[`backtest-audit-kit`](https://github.com/rytjy/backtest-audit-kit) — four dependency-free
checkers that find the four ways a backtest lies: look-ahead leaks, ledger-invariant breaks,
fee/funding double-counting, mutation blind spots. Service one-pager:
[`PORTFOLIO.md`](https://github.com/rytjy/backtest-audit-kit/blob/main/PORTFOLIO.md).

**Questions raised on open codebases** — read-only, no bounty, no payment involved, each one a
question about a specific line rather than a claim of a bug:

| Project | Issue |
|---|---|
| Ledgity Yield | [#4 — `mint()` does not guarantee the requested share amount (ERC-4626)](https://github.com/LedgityLabs/ledgity-v2-contracts/issues/4) |
| Monolith | [#59 — does `Lens.previewRedeem` intentionally settle differently from `Lender.redeem`?](https://github.com/MonolithMarket/Monolith/issues/59) |
| Tizi | [#2 — is `nftQueueUSDC` deducted twice after `fulfillNFT`?](https://github.com/tizimoney/Tizi-contract/issues/2) |
| VETRO | [#141 — can a `pegBand` be silently disabled by `priceTolerance` and re-enabled later?](https://github.com/vetro-protocol/vetro-contracts/issues/141) |
| SwingHook | [#1 — `SwingCurve`: 3 of the 98 cumulative entries can never be selected](https://github.com/Hooknomics/swinghook-smartcontract/issues/1) |
| Basalt Vault | [#4 — `GmPriceParams`: two call sites, two Chainlink→E30 conventions](https://github.com/basalt-vault/basalt-vault/issues/4) |
| july-backtester | [#421 — does rename resolution stay as-of, or can `universe(d)` admit future names?](https://github.com/zachisit/july-backtester/issues/421) |
| mr-scrooge-v6 | [#9 — is the promote/demote bar measuring the *search* rather than the edge?](https://github.com/BrockStar3540/mr-scrooge-v6/issues/9) |

## Contact

Open an issue on any of the above, or message me here on GitHub.

<details>
<summary>中文</summary>

### 独立合约复核 · 证据优先

我读小型 DeFi 代码库，把读到的东西写出来 —— **每条都带 `文件:行号`（我逐行回读过）**、
**覆盖率标签**，以及**明确的「未验证」标记**：证明不了的我不装。

**三条底线**

1. 每条结论都带 `文件:行号`，而且我回读过那一行 —— 不是"某处大概有"
2. `修复在不在` ≠ `修复对不对` —— 两件事，永远分开说
3. 报告里写明**我没读的部分**（`覆盖率 X/Y SLOC`）；低于 30% 我直接说"不足以支撑结论"

**公开可查**

- 方法（可复现）：[`ov-harness`](https://github.com/rytjy/ov-harness) —— "修复报告里声称的 fix commit，真的在受审代码里吗？"（中英双语 + 可运行脚本）
- 工具包（可跑）：[`backtest-audit-kit`](https://github.com/rytjy/backtest-audit-kit) —— 四个零依赖检查器，抓回测最常骗人的四种方式（前视泄漏 / 账本不变量 / 费用·资金费重复计 / 变异盲区）。服务一页说明：[`PORTFOLIO.md`](https://github.com/rytjy/backtest-audit-kit/blob/main/PORTFOLIO.md)。
- 在开源代码库上提的**具体提问**（只读、无赏金、无金钱往来）：上表 8 条，每条都是针对某一行的提问，不是"漏洞"断言

**联系**：开 issue，或在 GitHub 上私信我。

</details>
