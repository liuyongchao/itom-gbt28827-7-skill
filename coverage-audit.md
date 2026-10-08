# 原书任务覆盖审计

分母来自阶段0的T01—T16，而不是通过项倒推。所有16项有来源候选与明确去向，未解释遗漏为0；这不等于执行完整覆盖。T06依赖外部计数，T08/T09部分支持，T16为参考及待核查。实际运行时路径已生成，见下方14项单元映射；仍不表示全标准全部执行。

| 任务 | 标题 | 原候选 | 通过单元 | 其他去向 | 状态 |
|---|---|---|---|---|---|
| T01 | 运维服务范围与分类 | f01, f03, p01, p23, c01, g01, g02, g17 | V01 | 无 | supported_conditional |
| T02 | 成本分类与兼职分摊 | f01, f02, f17, p02, p03, p04, p25, p26, g04, g05, g06, g07, g20 | V02 | 无 | supported_conditional |
| T03 | 四类活动单位工作量 | f04, p05, g01, g03, g09, g17, g18 | V03 | 无 | supported_conditional |
| T04 | 基础环境工作量及成本 | f03, f04, f05, f07, f08, p05, p06, p08, p09, g02, g03, g09, g10, g11, g12 | V04, V12 | N04 | supported_conditional |
| T05 | 硬件工作量及成本 | f03, f04, f06, f07, f08, p05, p07, p08, p09, g02, g03, g09, g10, g11, g12 | V05, V12 | N04 | supported_conditional |
| T06 | 软件规模口径与调整 | f03, f09, p10, p11, p28, p29, c01, g02, g08, g16 | V06 | N03 | partial_external_dependency |
| T07 | 软件工作量 | f10, f20, p12, p13, p14, p15, p29, p30, c01, g03, g08, g10, g15, g16, g17, g18 | V07, V12 | N04 | supported_conditional |
| T08 | 软件两条成本路径 | f11, f20, p13, p14, p15, p16, p17, p29, p30, c01, g05, g08, g13, g14, g16, g18 | V08 | N02 | partial_source_gap |
| T09 | 安全工作量及成本 | f03, f04, f12, f13, p05, p18, p19, p20, g02, g03, g09, g10, g11, g12, g17 | V09, V12 | N01, N04 | partial_source_gap |
| T10 | 管理活动工作量及费用 | f03, f14, f15, p21, p22, g02, g03, g05, g09, g11, g12, g18 | V10, V12 | R24, N04 | supported_conditional |
| T11 | 迁移搬迁工作分解与计算 | f03, f16, p23, p24, g02, g03, g17, g18, g19 | V11 | N04 | supported_conditional |
| T12 | 参数基线与依据 | f01, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13, f14, f15, f16, f20, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p29, p30, c01, g09, g10, g11, g12, g13, g14, g15, g16, g17, g19, g20 | V12 | R22, N04, N06 | supported_conditional |
| T13 | 两类间接成本分摊/归集 | f01, f02, f17, p03, p16, p17, p21, p25, p26, g05, g06, g07, g13, g14, g20 | V02 | N04 | supported_conditional |
| T14 | 直接非人力及工具 | f01, f02, f16, f18, f19, p04, p23, p24, p27, g04, g07 | V13 | N04 | supported_conditional |
| T15 | 汇总与口径复核 | f01, f02, f05, f06, f11, f12, f14, f16, f17, f18, f19, p01, p02, p03, p04, p06, p07, p12, p16, p17, p18, p21, p23, p24, p25, p26, p27, p30, c01, g01, g02, g03, g04, g05, g06, g07, g09, g11, g12, g13, g14, g15, g18, g19, g20 | V14 | N01, N02 | supported_conditional |
| T16 | 资料性案例复核 | f20, p14, p28, p29, p30, c01, g08, g10, g13, g15, g16, g18 | 无独立active能力 | R21, R22, N03, N05, N06 | reference_and_needs_review |

## 原始候选的完整去向

审查单元按主题合并及范围分拆，且17条辅助边界归为一组参考；四类数字不可作为71项原始候选的简单互斥计数。

| 原候选 | 审查单元/去重去向 |
|---|---|
| f01 | V14 |
| f02 | V02 |
| f03 | V01 |
| f04 | V03 |
| f05 | V04 |
| f06 | V05 |
| f07 | V12, N04 |
| f08 | V12, N04 |
| f09 | V06, N03 |
| f10 | V07, N04 |
| f11 | V08, N02 |
| f12 | V09, N01 |
| f13 | V12, N04 |
| f14 | V10 |
| f15 | V12, N04 |
| f16 | V11 |
| f17 | V02, N04 |
| f18 | V13 |
| f19 | V13, N04 |
| f20 | N05, N06, D07 |
| p01 | V01, D01 |
| p02 | V14 |
| p03 | V02 |
| p04 | V13 |
| p05 | V03, D02 |
| p06 | V04, D03 |
| p07 | V05, D04 |
| p08 | V12, N04 |
| p09 | V12, N04 |
| p10 | V06, N03 |
| p11 | V06 |
| p12 | V07, D05 |
| p13 | V12, N04 |
| p14 | V12, N02, N04 |
| p15 | V12, N04 |
| p16 | V08 |
| p17 | N02 |
| p18 | V09, N01 |
| p19 | V12, N04 |
| p20 | V12, N04 |
| p21 | V10, R24 |
| p22 | V12, N04 |
| p23 | V11 |
| p24 | V11 |
| p25 | V02, N04 |
| p26 | V02, N04 |
| p27 | V13, N04, D06 |
| p28 | N03, R21 |
| p29 | N02, N06, R22 |
| p30 | N05, R21 |
| c01 | N03, N05, N06, R21 |
| g01 | R01 |
| g02 | R02 |
| g03 | R03 |
| g04 | R04 |
| g05 | R05 |
| g06 | R06 |
| g07 | R07 |
| g08 | R08 |
| g09 | R09 |
| g10 | R10 |
| g11 | R11 |
| g12 | R12 |
| g13 | R13 |
| g14 | R14 |
| g15 | R15 |
| g16 | R16 |
| g17 | R17 |
| g18 | R18 |
| g19 | R19 |
| g20 | R20 |

约定：supported_conditional指在说明的输入及边界内支持，不指无需项目证据。partial_external_dependency/partial_source_gap分别指外部方法依赖/未解决来源问题。


## 实际交付单元映射

| 单元 | 运行时卡片 | 测试正常/边界 |
|---|---|---|
| V01 运维范围及六类模型选择 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/scope-routing.md) | O01 / O02 |
| V02 四类成本归集与有依据的分摊 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/cost-ledger.md) | O03 / O04 |
| V03 四类服务的周期单位工作量 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/unit-workload.md) | O05 / O06 |
| V04 基础环境工作量与成本 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/environment-cost.md) | O07 / O08 |
| V05 硬件工作量与成本 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/hardware-cost.md) | O09 / O10 |
| V06 软件规模口径与已计量规模调整 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/software-size.md) | O11 / O12 |
| V07 软件工作量计算 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/software-workload.md) | O13 / O14 |
| V08 软件工作量乘综合费率的成本路径 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/software-effort-cost.md) | O15 / O16 |
| V09 安全工作量与单类别成本 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/security-cost.md) | O17 / O18 |
| V10 运维管理活动工作量与成本 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/management-cost.md) | O19 / O20 |
| V11 迁移搬迁的工作分解及成本 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/migration-cost.md) | O21 / O22 |
| V12 参数基线与适用证据登记 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/parameter-evidence.md) | O23 / O24 |
| V13 直接非人力及合同周期工具费用 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/nonhuman-cost.md) | O25 / O26 |
| V14 成本汇总与口径复核 | [卡片](skills/itom-cost-gbt28827-7/references/capabilities/total-review.md) | O27 / O28 |

R01—R20实际载于技能references/glossary.md；R21—R24及N01—N06实际载于references/overview.md，N01—N06另随resources/scope-limitations.md交付。原始候选与去重工作稿保存在本地审查记录；本仓库公开能力映射、源Bundle及测试证据。
