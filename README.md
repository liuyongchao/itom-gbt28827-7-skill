# 运维成本测算与复核技能

依据 **GB/T 28827.7—2022《信息技术服务 运行维护 第7部分：成本度量规范》**，把运维服务清单和参数转成可复核的工作量、费用及缺口清单。一个 `itom-cost-gbt28827-7` 入口，内部14张能力卡，附12模式十进制计算器、输入模板、使用说明、标准精华和测试报告。

**0.1.0 限定范围草稿**：支持范围已测试，N01—N06来源问题仍保留；不宣称完整国标自动化或正式符合性认证。由 [cangjie-skill](https://github.com/kangarooking/cangjie-skill) 提炼，运行不依赖cangjie。仓库不含原标准PDF、扫描图或OCR全文。

## 直接通过链接安装

把下面整段发给支持 `skill-installer` 的 Codex：

```text
请用 skill-installer 安装这个运维成本测算技能：
https://github.com/liuyongchao/itom-gbt28827-7-skill/tree/main/skills/itom-cost-gbt28827-7
```

**已验证**：匿名公开访问、skill-installer远程下载、26文件哈希核对及两个计算器示例均通过，见[发布验证](PUBLICATION.md)。

此链接指向完整技能目录 `skills/itom-cost-gbt28827-7`。应安装整个目录的SKILL.md、references、resources及编译清单。只下载SKILL.md会缺少能力卡和计算器。安装后下一轮对话可使用；如果客户端尚未显示，可重新加载客户端。

也可下载[独立技能ZIP](dist/itom-cost-gbt28827-7-0.1.0.zip)，把其中完整的 `itom-cost-gbt28827-7` 文件夹放到已配置的技能目录。Codex默认位置为 `~/.codex/skills/`，自定义 `CODEX_HOME` 时使用其 `skills/` 子目录。GitHub右上方 Code → Download ZIP 可下载本仓库全部文档和测试材料。

## 使用

```text
用 $itom-cost-gbt28827-7 测算下面的年度运维服务。
先确定六类服务范围和参数缺口，再计算已确定分项，最后复核费用包含关系。
未知费用不要按0，缺失因子不要按1，综合费率已含费用不要重复加。
```

```text
用 $itom-cost-gbt28827-7 复核这份报价：检查工作量、单位换算、
综合费率已含间接费用和利润、管理工作量10%—15%的用法，并给修改清单。
```

完整流程及示例见[使用说明](USAGE.md)。Python3.9+即可运行计算器，无第三方依赖、无联网取价：

```text
python skills/itom-cost-gbt28827-7/resources/itom_calc.py input.json --out output.json
```

输入从[模式样例](skills/itom-cost-gbt28827-7/resources/example-inputs.json)选择一个对象另存，数值使用十进制字符串。接口及状态见[计算器说明](skills/itom-cost-gbt28827-7/resources/CALCULATOR.md)。

## 内容

| 环节 | 能力 |
|---|---|
| 范围和费用口径 | 六类模型选择、四类成本台账及分摊、参数证据登记 |
| 规模及工作量 | 周期单位工作量、基础环境、硬件、软件规模、软件工作量 |
| 分类费用 | 软件综合费率、安全单类、运维管理、迁移搬迁、直接非人力 |
| 结果复核 | 同期间/币种/费用层级、包含关系及不完整状态传递 |

- [标准精华提炼](DIGEST.md)
- [术语词典](GLOSSARY.md)
- [测试报告](TEST_REPORT.md)：28项实际任务、85项脚本检查、入口12项复测，以及基线与修复记录。
- [范围和来源覆盖](coverage-audit.md)
- [待核查事项](needs-review.md)
- [技能入口](skills/itom-cost-gbt28827-7/SKILL.md)
- [项目输入模板](skills/itom-cost-gbt28827-7/resources/project-template.json)和[参数登记表](skills/itom-cost-gbt28827-7/resources/parameter-register.csv)
- `source-bundle/`：可维护的源卡、资源与verified.yaml；不要手改生成目录。

## 适用范围与发布说明

安全可以计算多类别工作量，费用仅限**整个目标确为单类别**；不能拆成多个单类再合并规避N01。软件仅执行8.2.1工作量乘综合费率路径，8.2.2保留N02；外部功能点结果须已核验。管理10%—15%是工作量参考，176工时/人月及附录历史费率均不是项目默认值。

运行目录26个文件与已测试交付版本逐字节一致；独立ZIP也包含相同26个文件。公开测试证据仅作本机路径归一化和去除重复/临时副本，算式、数值、判断及失败记录均保留。详见[发布记录](PUBLICATION.md)。原始提取候选和扫描核查工作稿未发布；引用的候选编号是编制审计标识，运行所需边界已在卡片与资源中给出。
