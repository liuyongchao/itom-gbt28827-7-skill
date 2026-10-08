# 运维成本计算器：输入合同与执行说明

版本 `1.0.0-restricted`，Python 3.9 或更高版本，仅使用标准库，无网络访问和第三方依赖。来源为所提供的 GB/T 28827.7—2022，适用范围以本技能的能力卡为准。程序负责输入格式、已声明单位和算术控制，无法验证合同、取参证据和分摊政策是否真实或适用，也无法自动识别被改名或删去来源信息的重复成本。

## 运行

在技能根目录运行：

```text
python resources/itom_calc.py input.json --out output.json
```

省略 `--out` 将 JSON 输出到标准输出。UTF-8 输入兼容 BOM；结果为 UTF-8。`example-inputs.json` 是按模式索引的合成样例集合，须复制某一个模式对应的对象为 `input.json`，不能把整个集合直接交给计算器。样例中的年份、单价和系数仅为演练参数。

数值必须是十进制**字符串**，例如 `"1.05"`、`"0"`。输入最多28位数字，指数绝对值不超过100；内部以 Decimal 80位有效数字运算，不执行金额取整。循环小数除法受80位精度约束。业务交付的元/万元和舍入位数应在报告中另行声明，并保留未舍入结果。布尔值用 JSON `true/false`；未知费用用 `null` 或省略，显式 `"0"` 仅可用于已确认零额。

返回状态：`calculated` 表示所声明范围输入齐全并完成算术；`partial` 表示只能给出已知小计；`needs_review` 表示来源或上游问题待核查；`needs_input` 表示输入合同未满足。`needs_input` 退出码为2，其余为0；**退出码0不等于完整成本**。程序不把未知费用当成0。输入格式错误返回首个问题，修正后重跑。`calculated` 不表示全标准认证或报价合理性认定。

所有模式必填 `mode` 和非空文本 `period`（例如 `2027全年`）。涉金额模式还必填 `currency`（如 `CNY`）和唯一 `scope_id`。输入应先按能力卡核对来源、范围、费用层级和重复归集。

## 模式输入

### unit_workload：一个对象在一个周期的单位工作量

- `workload_unit`：`person_hour`、`person_day` 或 `person_month`。
- `activities`：数组；每项 `id, category, effort, frequency`，`frequency` 为非负整数。
- `category` 的四类代码为 `routine` 例行操作、`response` 响应支持、`improvement` 优化改善、`assessment` 调研评估。
- 不适用活动在 `excluded_categories` 中按代码写非空依据。四类须全部纳入或有依据裁剪，同一类可以有多条不同活动。

计算 Σ(单次工作量×周期次数)。输出 `result.workload`，量纲为所声明的单对象周期工作量。此处不得再乘对象数量。工具使用天数不是人员人日。

### allocation：已确认同口径分摊或兼职折算

必填 `pool, numerator, denominator, basis_unit, basis_source`。分母须大于0，分子不得大于分母；结果为成本池×分子/分母。`basis_unit` 必须表示已经核对一致的分摊口径，程序不能识别用同一标签包装的混合量纲。输出 `summary.level=cost_component`；不同间接费用的适用分摊基准应由第2张卡先核对。

### environment / hardware / security：分类工作量与费用

必填 `workload_unit="person_day"`、`rate_unit="<currency>/person_day"`、`classes`。

每类字段：`id, quantity, unit_workload, workload_factor, rate, price_factor`。`quantity` 为非负整数。按数量×周期单位工作量×已定最终工作量因子得到工作量，再乘该类费率和最终价格因子得到直接人力。

`other_costs` 含 `direct_nonhuman`、`indirect_labor`、`indirect_nonhuman` 三项金额，任何项未知都输出 `partial` 已知小计。不得将工作量或直接人力成本标作完整总额。

`security` 另外必填 `scope_size`，表示**整个待测安全范围的类别数**，不是这次提交的行数。仅 `scope_size="1"` 且恰好一行时计算成本；否则仅输出已有类别工作量和三类其他费用的已知小计，`amount=null`，标记 `S01/N01`。`workload_complete=false` 表示尚有未提供类别；数量虽多但实际同一类别可以计算。多类别即使同价，本版仍不计成本。汇总时不得拆成多个单类别绕过此限制。

### management：四类管理活动费用

与上述货币和单位字段相同，`classes` 每项为 `id, category, occurrences, unit_workload, rate, price_factor`。类别为 `planning` 规划设计、`delivery` 交付管理、`quality` 质量管控、`review` 总结改进；全四类应纳入或写入 `excluded_categories` 说明裁剪依据。`occurrences` 为次数整数。直接人力=Σ(次数×每次人日×对应人日价格×最终价格因子)。`other_costs` 同上。

没有管理百分比输入。标准10%—15%仅保留为通常工作量参考，不能作为必加金额百分比。

### software_size：接收外部规模并作已定调整

- FP：`size_unit="FP"`，必填 `size,count_source,count_method,delivered,special_requirements`。有 `creep_factor` 时须填 `factor_source`；只有 `delivered=true` 且 `special_requirements=false` 时，可在未提供因子的情况下依本条注取1。结果为 `adjusted_size`（FP）。
- 套数：`size_unit="set"`，必填整数 `size,count_source,level_factor,type_factor,factor_source`；结果为套数×级别因子×类型因子，单位 `adjusted_set`。

程序不执行外部五种功能点计数法，不把按钮、菜单、页面数量当FP，不把套数与FP合并。

### software_workload：规模和生产率得到软件工作量

必填 `size,size_unit,productivity,productivity_unit,mlf,mcf,msf,workload_unit,parameter_source`。规模单位为 `FP` 或 `adjusted_set`；工作量单位为三种人员时间单位之一。生产率单位必须精确为 `<workload_unit>/<size_unit>`，例如 `person_hour/FP`。

结果=规模×生产率×三组最终因子。程序不对任意子因子自动加权或组合，不默认附录0.92，也不根据特征自动查资料性附录选档。

### software_cost：仅8.2.1工作量×综合费率

必填 `method="8.2.1"`、`composite_rate_confirmed=true`、`classes`。每项 `id,workload,workload_unit,rate,rate_unit`；`rate_unit` 为 `<currency>/<人员时间单位>`。费率已含间接成本和毛利润；只额外加 `direct_nonhuman`。提供额外 `other_costs/indirect_labor/indirect_nonhuman/profit` 字段会拒绝执行，避免重复。

若工作量单位与费率单位不同，该行必须提供 `conversion`：`from_unit,to_unit,source`，另提供 `multiplier` 或 `divisor` **恰好一个**。前者用工作量×倍率，后者用工作量÷除数。例如项目明确约定176小时/人月时，可填从 `person_hour` 到 `person_month` 的 `divisor="176"`；176绝不是全局默认。相同单位不得再传换算。

`direct_nonhuman` 未知时只给已知小计。其他方法返回 `S02/N02` 待核查并保留空总额，本版不执行8.2.2的功能点单价路径。

### migration：第11章人工工作分解与成本

必填 `workload_unit="person_day"`、`rate_unit="<currency>/person_day"`、`rate,rate_source,common_rate_applicable=true`。`classes` 每项为 `id,quantity,quantity_unit,unit_workload,personnel_factor,factors`。

`factors` 必须含 `service,location,batch`，每个为 `{ "applicable": true, "value": "1.1", "source": "取参依据" }`。本版支持三因子均提供适用值；或明确恰好一个因子适用、其余两个 `applicable=false,value="1"` 且有非适用依据。不能将漏填当作不适用；其他组合应先回到能力卡核对原文或明确三组适用值后再运行，程序保守判停。

每行工作量=数量×三因子之积×单位人工工作量×人员能力因子；合计后乘明确适用于全部人工要素的共同费率。不同数量单位不强行相加。`other_costs` 同其他分章；工具天数、材料数量先取得计价依据，折成对应费用，不进入人员人日。表1数据与应用迁移行的功能变化升级边界须由能力卡判断。

### nonhuman：已归属项目的直接非人力及工具金额

必填 `coverage_complete`、`non_overlap_confirmed=true`、`items`（可为空但零项须有范围依据）。每项为 `id,amount,period,currency,basis`。金额未知填 `null`。按合同周期逐项已给金额求和；例如软件工具折旧、管理、二次开发、其他费用，硬件工具折旧、管理、使用、维护、其他费用应分别列项。

覆盖不全或任一金额未知时只给已知小计。此模式输出 `cost_component` 层级，不自动建立折旧制度，不把全额采购和折旧同时计入，也不据数量猜测价格。是否共享和已含须先核对。

### total：在保持口径和上游状态的前提下汇总

必填 `expected_level`（`service_total`或`cost_component`）、`coverage_complete`、`non_overlap_confirmed=true`、`entries`。每个 `entries` 项直接使用前述金额输出的 **完整 `summary` 对象**，保留全部字段，尤其 `issues`、`domain`、安全范围信息及 `security_scope_count`。

支持外部已核验结果时同样填写：`id,scope_id,domain,period,currency,level,status,amount,known_subtotal,issues`。`status` 非 `calculated` 时 `amount` 必须为 `null`；待核查问题用 `{code,message}` 保留。`calculated` 要求无问题且 `amount` 等于已知小计。安全条目还须 `security_scope_size`；嵌套总额条目 `domain="total"` 还须 `security_scope_count`。禁止人为删改这些溯源字段。

期间/币种不一致、不同费用层级、重复范围ID拒绝汇总；未完整覆盖只给小计。两个安全单类条目或含多个安全分类的嵌套总额会触发 `S01/N01` 并从已知金额中排除相关安全条目/子汇总。上游 `S02/N02` 等问题向下游传递。程序无法判断不同ID背后实际是否重叠，`non_overlap_confirmed` 应有人工核对依据。

## 共同来源状态与能力边界

金额输入可带 `unresolved_issues:[{"code":"N04","message":"参数适用性待核查"}]`，执行算术后仍输出 `needs_review` 而不冒充完整结论。参数为已知数不等于该参数已经适用于实际项目。

程序没有六类自动归属、外部FP计数、经验系数校准、当前市场价格、自动折旧、法定鉴定、技术迁移执行等功能；这些分别由能力卡作范围判断、证据登记或判停。错误消息、单位核对、去重、精度与状态传播属于本技能实施控制，不冒充标准原文。
