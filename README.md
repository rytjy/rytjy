# rytjy

Read-only code review — evidence first.

I read code closely and write up what I find: **Solidity/DeFi contracts**, and (since 2026-10)
**backtest & strategy code**. Every item carries a `file:line` I re-read, an honest coverage
label, and an explicit "unverified" tag where I could not prove it.

## Standards

1. Every claim carries a `file:line` that I re-read. No "somewhere around here".
2. "The fix is present" ≠ "the fix is correct" — kept separate, always.
3. Reports state what I did **not** read (`coverage: X/Y SLOC`). Below 30% I say it does not
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

**Null results — kept on purpose**
[no-findings](https://github.com/rytjy/no-findings) — two reviews where I read **all** the in-scope
code (100% SLOC) and nothing was committable. Published because the honest output of a review is
not always a bug list.

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
| microsoft/qlib | [#2297 — `Rsquare(N=0)`: is the std≈0 mask missing in the expanding branch?](https://github.com/microsoft/qlib/issues/2297) |
| microsoft/qlib | [#2352 — `IdxMax`/`IdxMin` do not skip NaN, while `Mad`/`Rank` do — intended?](https://github.com/microsoft/qlib/issues/2352) |
| microsoft/qlib | [#2354 — `pkg_resources` at `collect_info.py:5` — `importlib.metadata` instead?](https://github.com/microsoft/qlib/issues/2354) |
| microsoft/qlib | [#2163 — is `metric_fn` compared to a tuple with `==`, so the default metric always raises?](https://github.com/microsoft/qlib/issues/2163) |
| microsoft/qlib | [#2167 — `evals_result=dict()` as a default argument at 28 sites — `None` instead?](https://github.com/microsoft/qlib/issues/2167) |
| microsoft/qlib | [#2276 — `TopkDropoutStrategy` sizes buys from the raw `risk_degree`, bypassing the getter?](https://github.com/microsoft/qlib/issues/2276) |
| polakowo/vectorbt | [#876 — `ewm_std` ignores `ddof` in both engines — which indicators are affected?](https://github.com/polakowo/vectorbt/issues/876) |
| polakowo/vectorbt | [#737 — extreme percentages: `SizeType.amount` against the default `init_cash`?](https://github.com/polakowo/vectorbt/issues/737) |
| kernc/backtesting.py | [#1339 — does NaN-bar handling push the whole start line back, or skip per bar?](https://github.com/kernc/backtesting.py/issues/1339) |
| kernc/backtesting.py | [#1415 — `MultiBacktest` docstring imports a name its module does not export?](https://github.com/kernc/backtesting.py/issues/1415) |
| ranaroussi/quantstats | [#571 — a sub-$1 price series is read as returns; is price input in scope?](https://github.com/ranaroussi/quantstats/issues/571) |
| AI4Finance-Foundation/FinRL | [#1434 — `auto_adjust=False`: are OHLC prices rescaled by adjcp/close?](https://github.com/AI4Finance-Foundation/FinRL/issues/1434) |
| uty101/Cross-Sectional-Factor-Backtester | [#4 — DSR: all-trials or candidates only? survivors-only universe?](https://github.com/uty101/Cross-Sectional-Factor-Backtester/issues/4) |
| july-backtester | [#421 — does rename resolution stay as-of, or can `universe(d)` admit future names?](https://github.com/zachisit/july-backtester/issues/421) |
| mr-scrooge-v6 | [#9 — is the promote/demote bar measuring the *search* rather than the edge?](https://github.com/BrockStar3540/mr-scrooge-v6/issues/9) |

**Follow-up — one of these was picked up upstream.** A third-party contributor opened
[quantstats#574](https://github.com/ranaroussi/quantstats/pull/574) implementing the warning
shape discussed in [#571](https://github.com/ranaroussi/quantstats/issues/571) (with a regression
test), and a second contributor reviewed it on the branch. Not merged as of 2026-10-12; the
maintainer has not weighed in.

**Findings** — separated from the questions above: these come with a repro that runs against the
project’s own code path, and they still state what I did not read.

| Project | Finding |
|---|---|
| tradedesk | [#179 — weekend financing books 5 days for a 3-day Fri→Mon span (Friday ×3 + Sat/Sun counted again) — repro included](https://github.com/radiusred/tradedesk/issues/179) |

## Contact

Open an issue on any of the above, or **`@`-mention me in a thread** — GitHub has no direct
messages, so a mention or an issue is the only way to reach me.

<details>
<summary>中文</summary>

### 独立代码复核 · 证据优先

我读代码，把读到的东西写出来 —— **每条都带 `文件:行号`（我逐行回读过）**、
**覆盖率标签**，以及**明确的「未验证」标记**：证明不了的我不装。
范围：**Solidity / DeFi 合约**，以及（2026-10 起）**回测与策略代码**。

**三条底线**

1. 每条结论都带 `文件:行号`，而且我回读过那一行 —— 不是"某处大概有"
2. `修复在不在` ≠ `修复对不对` —— 两件事，永远分开说
3. 报告里写明**我没读的部分**（`覆盖率 X/Y SLOC`）；低于 30% 我直接说"不足以支撑结论"

**公开可查**

- 方法（可复现）：[`ov-harness`](https://github.com/rytjy/ov-harness) —— "修复报告里声称的 fix commit，真的在受审代码里吗？"（中英双语 + 可运行脚本）
- 工具包（可跑）：[`backtest-audit-kit`](https://github.com/rytjy/backtest-audit-kit) —— 四个零依赖检查器，抓回测最常骗人的四种方式（前视泄漏 / 账本不变量 / 费用·资金费重复计 / 变异盲区）。服务一页说明：[`PORTFOLIO.md`](https://github.com/rytjy/backtest-audit-kit/blob/main/PORTFOLIO.md)。
- **阴性结果（故意公开）**：[no-findings](https://github.com/rytjy/no-findings) —— 两次**读完全部**在范围代码（100% SLOC）、没有可交发现的复核。公开它，是因为「复核的诚实产出不一定是一张 bug 清单」。
- **有一条提问被上游接走了**：第三方贡献者按 #571 讨论的形状开了 [quantstats#574](https://github.com/ranaroussi/quantstats/pull/574)（带回归测试），另一位贡献者在分支上做了审查。截至 2026-10-12 未合并，维护者未表态。
- 在开源代码库上提的**具体提问**（只读、无赏金、无金钱往来）：上表 21 条，每条都是针对某一行的提问，不是"漏洞"断言
- 在开源代码库上提的**发现**（可复现）：[`radiusred/tradedesk#179`](https://github.com/radiusred/tradedesk/issues/179) —— 周末融资在 Fri→Mon（3 个日历日）按 5 天计息（周五 ×3 + 周六/周日各 +1），高估 66.7%；附可跑复现

**联系**：开 issue，或在任意一条线程里 **@ 我** —— GitHub 没有私信，@ 或 issue 是唯一能联系到我的方式。

</details>
