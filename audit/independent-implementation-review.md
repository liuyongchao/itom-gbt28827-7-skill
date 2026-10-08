# 运维成本技能独立复核

审查日期：2026-10-08。对象：`work/itom-preview`，计算器版本 `1.0.0-restricted`。本轮仅审查，未改动技能或计算器。

结论：发现 **1 项 P2 问题**，会阻断文档承诺的分项结果原样汇总。下述问题已用独立构造的输入实测；没有读取 `work/itom-evals` 的任何内容，也没有复跑既有72项回归。

## P2：计算器生成的80位金额无法通过自身28位汇总输入限制

位置：`resources/itom_calc.py:53` 的数值长度检查，与 `total_cost` 在 `resources/itom_calc.py:400`、`:408` 读取 `amount`、`known_subtotal` 的调用；对应文档 `resources/CALCULATOR.md:15`、`:89`。

`allocation` 和软件单位换算在80位 Decimal 上下文中计算，循环小数结果会保留约80位有效数字。文档要求将完整 `summary` 原样交给 `total.entries`，并要求中间不提前舍入。但 `total` 仍调用只接受28位输入的 `num/number`，因此正常分项结果在下一步被拒绝为 `needs_input`。同一问题也影响 `partial/needs_review` 的长精度 `known_subtotal`。

复现：在技能根目录运行以下 Python，所有原始输入都远小于28位，传递过程中没有修改 `summary`。

```python
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("itom", Path("resources/itom_calc.py"))
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)

base = {"period": "2027", "currency": "CNY"}
part = calc.calculate(dict(
    base, mode="allocation", scope_id="allocation-a",
    pool="100", numerator="1", denominator="3",
    basis_unit="person_day", basis_source="confirmed project basis"))
combined = calc.calculate(dict(
    base, mode="total", scope_id="project-total",
    expected_level="cost_component", coverage_complete=True,
    non_overlap_confirmed=True, entries=[part["summary"]]))
print(part["status"], part["summary"]["amount"])
print(combined["status"], combined["issues"])
```

实测：第一步为 `calculated`，金额为保留80位有效数字的 `33.333…`；第二步为 `needs_input`，问题为 `INPUT_REQUIRED: amount 超出实现精度限制（28位输入数字、指数绝对值≤100）`。另行用已明确约定的 `1 人时 ÷ 176 人时/人月 × 10000 元/人月` 软件8.2.1分项验证，分项算出 `56.81818…`，交给 `service_total` 同样被拒绝。

预期：原样接收本计算器有效输出的金额与已知小计，保留中间精度并完成同口径汇总。建议区分原始参数和计算结果的数值入口，使输出—输入合同闭合；不能要求用户为绕过限制而提前舍入、截断或改写上游结果。修复验证至少应覆盖上述分摊、带换算的软件成本，以及非完整状态下的长精度已知小计。

## 已核对的关键边界

- 公式位置与批准契约一致：软件8.2.1逐类工作量乘综合费率后加直接非人力；综合费率已含间接成本及毛利润。迁移的三影响因子相乘，人员因子只另乘一次；“仅一个因子适用”的局部取1条件没有扩为全局默认。
- 安全费用限制与 N01/V09 一致，未擅自把类别单价搬进多类求和。自造输入验证了单类费用、真实范围两类但仅输入一类、两个单类直接汇总、以及先包装为子汇总再合并；后三者保留 `S01/N01`，`amount=null`，没有输出多类完整总价。
- 缺两类其他费用的安全结果为 `partial`，汇总后仍是小计；携带 `N04` 的上游结果在汇总后仍为 `needs_review`。8.2.2请求及其后续汇总保留 `S02/N02`，没有启用被禁用的路径。
- 已读入口、能力卡与计算说明均区分“声明输入通过校验”和“证据真实/参数适用性已证实”，没有把数值齐全、脚本成功或项目约定升级为来源验证。
- 已读五张能力卡引用的六个配套资源相对路径均解析到实际存在的文件；脚本仅依赖 Python 标准库，未发现机器专属路径依赖。

## 范围与局限

实际读取了 `SKILL.md`、`resources/CALCULATOR.md`、`resources/itom_calc.py`，以及 `total-review`、`security-cost`、`software-effort-cost`、`migration-cost`、`parameter-evidence` 五张能力卡。来源对照仅使用指定的 `verified.md`、`needs-review.md`、`stage15-decisions.json`。

本轮是相对于上述批准契约的独立一致性审查，没有重做PDF原文取证、核验标准现行状态或核验项目证据的真实性。资源可移植性检查仅覆盖相对链接解析、文件存在和脚本静态依赖，没有在其他操作系统/干净Python环境安装整包。自造运行验证使用 Python 3.10 的 `calculate()` 接口，未覆盖全部模式或 CLI 文件异常。没有足够依据将这些未覆盖范围写成“全部通过”。

## 修复复核追加：1.0.1，原 P2 已关闭

复核日期：2026-10-08。本次仅检查修复后的源资源 `work/books/gbt28827-7-2022-itom-cost/.cangjie/capabilities/resources/itom_calc.py`，运行结果版本为 `1.0.1-restricted`；未修改代码，未读取隔离测试目录。

独立复跑原始案例并直接传递完整 `summary`，结果如下：

| 案例 | 上游状态 | 汇总状态 | 精度与缺值结果 |
|---|---|---|---|
| 分摊 `100×1/3` | calculated | calculated | 80位循环小数金额原样保留 |
| 软件 `1÷176×10000`，直接非人力为已确认0 | calculated | calculated | 80位循环小数金额原样保留 |
| 同一软件计算，直接非人力为未知 `null` | partial | partial | `amount=null`，80位已知小计原样保留 |

以上三例均对汇总前后 `amount` 和 `known_subtotal` 作字符串相等断言并通过，没有提前舍入。另以普通参数 `pool="12345678901234567890123456789"`（29位）及 `pool="1e101"` 验证，两者仍返回 `needs_input` 和原始“28位输入数字、指数绝对值≤100”限制错误。

静态复核确认：专用 `summary_num()` 仅用于 `total` 的 `amount`/`known_subtotal`，普通 `num()` 仍走28位检查；汇总读入设80位有效数字、数量级绝对值≤1024与字符串长度≤2048的限制。

结论：**原报告所列唯一 P2 已在本次受检1.0.1源资源中关闭**。本次未扩大为全模式回归，亦未验证预览包、压缩包或最终安装副本是否已同步该版本；原报告其他验证局限仍适用。
