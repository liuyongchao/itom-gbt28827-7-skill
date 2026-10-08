{
  "case_id": "O14",
  "status": "needs_input",
  "route": "software-workload（软件工作量计算）；parameter-evidence",
  "numeric_results": {
    "normalized_productivity": "0.25",
    "base_workload": "80"
  },
  "notes": [
    "依据用户提供的GB/T 28827.7—2022限定版技能，未核验标准现行状态。周期为2026年度合同期间，金额单位为CNY元；除明确缺失项外，按题给双方核定的参数、基线、单位和范围执行，不作外部真实性验证。",
    "不能使用320×4×1.1×1×1.2。4FP/人时表示每人时完成4FP，方向与本式要求相反；按题给明确单位，转换为R＝1÷4＝0.25人时/FP。原式320FP×4FP/人时不能得到人时。",
    "已知未调整基数S×R＝320×0.25＝80人时；normalized_productivity单位为人时/FP，base_workload单位为人时，后者不是完整调整后工作量。转换使用80位Decimal辅助人工复算，保留精度。",
    "必须补最终运维能力调整因子MCF及其基线、适用范围和来源；若仅有团队经验/自动化子因子，还需核定组合依据。不得把缺失MCF填1。完整表达式为W＝320×0.25×1.1×MCF×1.2人时，待MCF补齐后才计算完整W；人日或人月换算未被请求，不自行转换。"
  ]
}
