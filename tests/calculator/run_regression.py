"""Generate portable synthetic examples, then exercise arithmetic and boundaries."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "skills/itom-cost-gbt28827-7/resources"
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("itom_calc", RES / "itom_calc.py")
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)


def common(mode):
    return {"mode": mode, "period": "2027全年（合成演练）", "currency": "CNY", "scope_id": "demo-" + mode}


zero_other = {"direct_nonhuman": "0", "indirect_labor": "0", "indirect_nonhuman": "0"}
examples = {}
examples["unit_workload"] = {"mode": "unit_workload", "period": "2027全年（合成演练）", "workload_unit": "person_day",
    "activities": [{"id": "u1", "category": "routine", "effort": "0.2", "frequency": "12"},
                   {"id": "u2", "category": "response", "effort": "0.4", "frequency": "3"},
                   {"id": "u3", "category": "improvement", "effort": "1.5", "frequency": "2"},
                   {"id": "u4", "category": "assessment", "effort": "0.8", "frequency": "1"}]}
examples["allocation"] = dict(common("allocation"), pool="24000", numerator="45", denominator="180", basis_unit="person_hour", basis_source="合成演练：同月全部项目工作时数")
for mode in ("environment", "hardware", "security"):
    examples[mode] = dict(common(mode), workload_unit="person_day", rate_unit="CNY/person_day",
        classes=[{"id": "c1", "quantity": "8", "unit_workload": "1.5", "workload_factor": "1.1", "rate": "800", "price_factor": "1.05"}],
        other_costs={"direct_nonhuman": "600", "indirect_labor": "300", "indirect_nonhuman": "100"})
examples["security"]["scope_size"] = "1"
examples["management"] = dict(common("management"), workload_unit="person_day", rate_unit="CNY/person_day",
    classes=[{"id": "m1", "category": "planning", "occurrences": "2", "unit_workload": "1.5", "rate": "900", "price_factor": "1.1"},
             {"id": "m2", "category": "delivery", "occurrences": "4", "unit_workload": "0.5", "rate": "800", "price_factor": "1"},
             {"id": "m3", "category": "quality", "occurrences": "2", "unit_workload": "0.8", "rate": "800", "price_factor": "1"},
             {"id": "m4", "category": "review", "occurrences": "1", "unit_workload": "1", "rate": "900", "price_factor": "1"}],
    other_costs=copy.deepcopy(zero_other))
examples["software_size"] = {"mode": "software_size", "period": "2027全年（合成演练）", "size_unit": "FP", "size": "800", "count_source": "合成演练：外部计数报告D1", "count_method": "已声明外部方法和版本", "delivered": False, "special_requirements": True, "creep_factor": "1.1", "factor_source": "合成演练：已定需求蔓延参数"}
examples["software_workload"] = {"mode": "software_workload", "period": "2027全年（合成演练）", "size": "880", "size_unit": "FP", "productivity": "0.75", "productivity_unit": "person_hour/FP", "mlf": "1.1", "mcf": "0.95", "msf": "1.02", "workload_unit": "person_hour", "parameter_source": "合成演练：三组最终因子及生产率"}
examples["software_cost"] = dict(common("software_cost"), method="8.2.1", composite_rate_confirmed=True,
    classes=[{"id": "s1", "workload": "703.494", "workload_unit": "person_hour", "rate": "160", "rate_unit": "CNY/person_hour"}], direct_nonhuman="1200")
examples["migration"] = dict(common("migration"), workload_unit="person_day", rate_unit="CNY/person_day", rate="1100", rate_source="合成演练：共同费率", common_rate_applicable=True,
    classes=[{"id": "g1", "quantity": "4", "quantity_unit": "台", "unit_workload": "0.75", "personnel_factor": "1.05",
              "factors": {"service": {"applicable": True, "value": "1.1", "source": "合成参数"},
                          "location": {"applicable": True, "value": "1.2", "source": "合成参数"},
                          "batch": {"applicable": True, "value": "0.9", "source": "合成参数"}}}], other_costs=copy.deepcopy(zero_other))
examples["nonhuman"] = dict(common("nonhuman"), coverage_complete=True, non_overlap_confirmed=True, items=[
    {"id": "tool-depreciation", "amount": "1300", "period": "2027全年（合成演练）", "currency": "CNY", "basis": "合成：合同周期软件工具折旧"},
    {"id": "tool-secondary-dev", "amount": "600", "period": "2027全年（合成演练）", "currency": "CNY", "basis": "合成：专用工具二次开发"}])
examples["total"] = dict(common("total"), expected_level="service_total", coverage_complete=True, non_overlap_confirmed=True,
    entries=[calc.calculate(examples["environment"])["summary"], calc.calculate(examples["software_cost"])["summary"]])
(HERE / "generated-examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

cases = []


def case(name, mode, checks, change=None):
    obj = copy.deepcopy(examples[mode])
    if change:
        change(obj)
    out = calc.calculate(obj)
    errors = []
    for path, expected in checks.items():
        actual = out
        try:
            for field in path.split("."):
                actual = actual[int(field)] if isinstance(actual, list) else actual[field]
        except (KeyError, IndexError, TypeError):
            actual = "<absent>"
        if actual != expected:
            errors.append({"path": path, "expected": expected, "actual": actual})
    cases.append({"id": name, "passed": not errors, "input": obj, "output": out, "checks": checks, "errors": errors})


def delete(*keys):
    return lambda obj: [obj.pop(key, None) for key in keys]


def setrow(field, value):
    return lambda obj: obj["classes"][0].__setitem__(field, value)


case("unit-four-activities", "unit_workload", {"status": "calculated", "result.workload": "7.4"})
case("unit-frequency-unknown", "unit_workload", {"status": "needs_input"}, lambda o: o["activities"][0].pop("frequency"))
case("unit-incomplete-coverage", "unit_workload", {"status": "needs_input"}, lambda o: o["activities"].pop())
case("unit-explicit-exclusion", "unit_workload", {"status": "calculated", "result.workload": "6.6"}, lambda o: (o["activities"].pop(), o.update(excluded_categories={"assessment": "合成服务目录明确不包含"})))
case("allocation-quarter", "allocation", {"status": "calculated", "result.amount": "6000", "summary.level": "cost_component"})
case("allocation-zero-denominator", "allocation", {"status": "needs_input"}, lambda o: o.update(denominator="0"))
case("allocation-share-over-one", "allocation", {"status": "needs_input"}, lambda o: o.update(numerator="181"))
case("allocation-missing-basis", "allocation", {"status": "needs_input"}, delete("basis_source"))
case("environment-cost", "environment", {"status": "calculated", "result.workload": "13.2", "result.direct_labor": "11088", "result.amount": "12088"})
case("environment-unknown-cost", "environment", {"status": "partial", "result.amount": None, "result.known_subtotal": "11988"}, lambda o: o["other_costs"].pop("indirect_nonhuman"))
case("environment-missing-factor", "environment", {"status": "needs_input"}, lambda o: o["classes"][0].pop("workload_factor"))
case("environment-unit-conflict", "environment", {"status": "needs_input"}, lambda o: o.update(rate_unit="CNY/person_month"))
case("hardware-multiple-rates", "hardware", {"status": "calculated", "result.amount": "13888"}, lambda o: o["classes"].append({"id": "c2", "quantity": "2", "unit_workload": "1", "workload_factor": "1", "rate": "900", "price_factor": "1"}))
case("hardware-negative", "hardware", {"status": "needs_input"}, setrow("quantity", "-1"))
case("hardware-nan", "hardware", {"status": "needs_input"}, setrow("rate", "NaN"))
case("hardware-number-not-string", "hardware", {"status": "needs_input"}, setrow("rate", 800))
case("hardware-decimal-count", "hardware", {"status": "needs_input"}, setrow("quantity", "1.5"))
case("hardware-factor-not-one-default", "hardware", {"status": "needs_input"}, setrow("price_factor", None))
case("security-single", "security", {"status": "calculated", "result.amount": "12088", "summary.security_scope_size": "1"})
case("security-two-classes", "security", {"status": "needs_review", "result.amount": None, "result.workload": "26.4", "result.direct_labor": None}, lambda o: (o.update(scope_size="2"), o["classes"].append(dict(o["classes"][0], id="c2"))))
case("security-one-row-of-two", "security", {"status": "needs_review", "result.workload_complete": False, "result.amount": None}, lambda o: o.update(scope_size="2"))
case("security-lied-scope-size", "security", {"status": "needs_input"}, lambda o: o["classes"].append(dict(o["classes"][0], id="c2")))
case("management-four-activities", "management", {"status": "calculated", "result.workload": "7.6", "result.amount": "6750"})
case("management-unknown-extra", "management", {"status": "partial", "result.amount": None}, delete("other_costs"))
case("management-incomplete-coverage", "management", {"status": "needs_input"}, lambda o: o["classes"].pop())
case("software-fp-adjustment", "software_size", {"status": "calculated", "result.adjusted_size": "880", "result.size_unit": "FP"})
case("software-fp-no-creep-default", "software_size", {"status": "needs_input"}, delete("creep_factor"))
case("software-fp-local-one", "software_size", {"status": "calculated", "result.adjusted_size": "800", "result.creep_factor": "1"}, lambda o: (o.pop("creep_factor"), o.update(delivered=True, special_requirements=False)))
case("software-sets-separate", "software_size", {"status": "calculated", "result.adjusted_size": "5.94", "result.size_unit": "adjusted_set"}, lambda o: o.update(size_unit="set", size="6", level_factor="1.1", type_factor="0.9"))
case("software-workload-product", "software_workload", {"status": "calculated", "result.workload": "703.494"})
case("software-unit-mismatch", "software_workload", {"status": "needs_input"}, lambda o: o.update(productivity_unit="FP/person_hour"))
case("software-missing-group-factor", "software_workload", {"status": "needs_input"}, delete("msf"))
case("software-composite-cost", "software_cost", {"status": "calculated", "result.amount": "113759.04"})
case("software-double-indirect", "software_cost", {"status": "needs_input", "issues.0.code": "DOUBLE_COUNT"}, lambda o: o.update(indirect_labor="1000"))
case("software-blocked-fp-method", "software_cost", {"status": "needs_review", "result.amount": None, "issues.0.code": "S02/N02"}, lambda o: o.update(method="8.2.2"))
case("software-missing-conversion", "software_cost", {"status": "needs_input"}, setrow("rate_unit", "CNY/person_month"))
case("software-explicit-conversion", "software_cost", {"status": "calculated", "result.amount": "6200"}, lambda o: o["classes"][0].update(workload="40", rate="20000", rate_unit="CNY/person_month", conversion={"from_unit": "person_hour", "to_unit": "person_month", "divisor": "160", "source": "合成合同明确160小时/人月"}))
case("software-unknown-direct-nonhuman", "software_cost", {"status": "partial", "result.amount": None, "result.known_subtotal": "112559.04"}, delete("direct_nonhuman"))
case("migration-workload-and-cost", "migration", {"status": "calculated", "result.workload": "3.7422", "result.amount": "4116.42"})
case("migration-missing-factor", "migration", {"status": "needs_input"}, lambda o: o["classes"][0]["factors"].pop("batch"))
case("migration-one-factor-local-rule", "migration", {"status": "calculated", "result.workload": "3.465", "result.amount": "3811.5"}, lambda o: [o["classes"][0]["factors"][k].update(applicable=False, value="1", source="已确认本项目仅服务级别因子适用") for k in ("location", "batch")])
case("migration-nonapplicable-not-one", "migration", {"status": "needs_input"}, lambda o: o["classes"][0]["factors"]["location"].update(applicable=False))
case("migration-common-rate-not-confirmed", "migration", {"status": "needs_input"}, lambda o: o.update(common_rate_applicable=False))
case("nonhuman-tool-sum", "nonhuman", {"status": "calculated", "result.amount": "1900", "summary.level": "cost_component"})
case("nonhuman-unknown-item", "nonhuman", {"status": "partial", "result.amount": None, "result.known_subtotal": "1300"}, lambda o: o["items"][1].update(amount=None))
case("nonhuman-unpriced-quantity", "nonhuman", {"status": "partial", "result.amount": None}, lambda o: (o["items"][1].pop("amount"), o["items"][1].update(tool_days="2")))
case("nonhuman-period-conflict", "nonhuman", {"status": "needs_input"}, lambda o: o["items"][0].update(period="2026全年"))
case("nonhuman-coverage-incomplete", "nonhuman", {"status": "partial", "result.amount": None}, lambda o: o.update(coverage_complete=False))
case("total-disjoint-complete", "total", {"status": "calculated", "result.amount": "125847.04"})
case("total-period-conflict", "total", {"status": "needs_input"}, lambda o: o["entries"][0].update(period="2026全年"))
case("total-currency-conflict", "total", {"status": "needs_input"}, lambda o: o["entries"][0].update(currency="USD"))
case("total-level-conflict", "total", {"status": "needs_input"}, lambda o: o["entries"].append(calc.calculate(examples["nonhuman"])["summary"]))
case("total-duplicate-scope", "total", {"status": "needs_input"}, lambda o: o["entries"][1].update(scope_id=o["entries"][0]["scope_id"]))
case("total-coverage-incomplete", "total", {"status": "partial", "result.amount": None, "result.known_subtotal": "125847.04"}, lambda o: o.update(coverage_complete=False))
case("total-unknown-upstream", "total", {"status": "partial", "result.amount": None, "result.known_subtotal": "125747.04"}, lambda o: o["entries"].__setitem__(0, calc.calculate(dict(examples["environment"], other_costs={"direct_nonhuman": "600", "indirect_labor": "300"}))["summary"]))
case("total-propagate-n02", "total", {"status": "needs_review", "result.amount": None, "result.known_subtotal": "12088"}, lambda o: o["entries"].__setitem__(1, calc.calculate(dict(examples["software_cost"], method="8.2.2"))["summary"]))
case("total-preserve-n04", "total", {"status": "needs_review", "result.amount": None}, lambda o: o.update(unresolved_issues=[{"code": "N04", "message": "参数适用性待核查"}]))


def split_security(obj):
    obj["entries"] = [calc.calculate(dict(examples["security"], scope_id="sec-a"))["summary"],
                      calc.calculate(dict(examples["security"], scope_id="sec-b"))["summary"]]


case("total-block-security-split", "total", {"status": "needs_review", "result.amount": None, "result.known_subtotal": "0"}, split_security)


def nested_security(obj):
    first = dict(common("total"), scope_id="nested-a", expected_level="service_total", coverage_complete=True,
                 non_overlap_confirmed=True, entries=[calc.calculate(dict(examples["security"], scope_id="sec-a"))["summary"]])
    obj["entries"] = [calc.calculate(first)["summary"], calc.calculate(dict(examples["security"], scope_id="sec-b"))["summary"]]


case("total-block-nested-security-split", "total", {"status": "needs_review", "result.amount": None, "result.known_subtotal": "0"}, nested_security)
case("total-no-overlap-attestation", "total", {"status": "needs_input"}, lambda o: o.update(non_overlap_confirmed=False))
case("total-forged-complete-with-issues", "total", {"status": "needs_input"}, lambda o: o["entries"][0].update(issues=[{"code": "N04", "message": "证据待核查"}]))
case("total-inconsistent-complete-subtotal", "total", {"status": "needs_input"}, lambda o: o["entries"][0].update(known_subtotal="1"))
case("total-review-without-message-stays-review", "total", {"status": "needs_review", "result.amount": None}, lambda o: o["entries"][0].update(status="needs_review", amount=None))
case("software-two-conversion-forms-rejected", "software_cost", {"status": "needs_input"}, lambda o: o["classes"][0].update(rate_unit="CNY/person_month", conversion={"from_unit": "person_hour", "to_unit": "person_month", "divisor": "160", "multiplier": "0.00625", "source": "合成"}))
case("software-zero-conversion-rejected", "software_cost", {"status": "needs_input"}, lambda o: o["classes"][0].update(rate_unit="CNY/person_month", conversion={"from_unit": "person_hour", "to_unit": "person_month", "divisor": "0", "source": "合成"}))
case("hardware-infinite-rejected", "hardware", {"status": "needs_input"}, setrow("rate", "Infinity"))
case("hardware-unknown-zero-not-imputed", "hardware", {"status": "partial", "result.amount": None, "result.known_subtotal": "11088"}, delete("other_costs"))
case("nonhuman-duplicate-line", "nonhuman", {"status": "needs_input", "issues.0.code": "DUPLICATE"}, lambda o: o["items"].append(copy.deepcopy(o["items"][0])))

# P2 regression: transfer the producer's unrounded summary unchanged.
third_expected = "33." + "3" * 78
third_summary = calc.calculate(dict(examples["allocation"], pool="100", numerator="1", denominator="3"))["summary"]
case("precision-allocation-third-roundtrip", "total", {"status": "calculated", "result.amount": third_expected},
     lambda o: o.update(expected_level="cost_component", entries=[third_summary]))
conversion_expected = "56.818181818181818181818181818181818181818181818181818181818181818181818181818182"
conversion_input = dict(examples["software_cost"], classes=[dict(examples["software_cost"]["classes"][0], workload="1", rate="10000", rate_unit="CNY/person_month", conversion={"from_unit": "person_hour", "to_unit": "person_month", "divisor": "176", "source": "合成合同明确176小时/人月"})], direct_nonhuman="0")
conversion_summary = calc.calculate(conversion_input)["summary"]
case("precision-software-conversion-roundtrip", "total", {"status": "calculated", "result.amount": conversion_expected},
     lambda o: o.update(entries=[conversion_summary]))
partial_nested_input = dict(examples["total"], scope_id="third-partial", expected_level="cost_component", entries=[third_summary], coverage_complete=False)
partial_nested_summary = calc.calculate(partial_nested_input)["summary"]
case("precision-nested-partial-subtotal", "total", {"status": "partial", "result.amount": None, "result.known_subtotal": third_expected},
     lambda o: o.update(expected_level="cost_component", entries=[partial_nested_summary]))
huge_input = copy.deepcopy(examples["hardware"])
huge_input["classes"][0].update(quantity="1", unit_workload="1e100", workload_factor="1e100", rate="1e100", price_factor="1e100")
huge_input["other_costs"] = copy.deepcopy(zero_other)
huge_summary = calc.calculate(huge_input)["summary"]
case("precision-multiplication-expanded-integer-zeroes", "total", {"status": "calculated", "result.amount": "1" + "0" * 400},
     lambda o: o.update(entries=[huge_summary]))
tiny_input = copy.deepcopy(huge_input)
tiny_input["classes"][0].update(unit_workload="1e-100", workload_factor="1e-100", rate="1e-100", price_factor="1e-100")
tiny_summary = calc.calculate(tiny_input)["summary"]
case("precision-multiplication-expanded-small-value", "total", {"status": "calculated", "result.amount": "0." + "0" * 399 + "1"},
     lambda o: o.update(entries=[tiny_summary]))


def summary_amount(value):
    def update(obj):
        obj["entries"] = [dict(examples["total"]["entries"][0], amount=value, known_subtotal=value)]
    return update


case("precision-summary-long-representational-tail", "total", {"status": "calculated", "result.amount": "1.25"}, summary_amount("1.25" + "0" * 200))
case("precision-summary-81-significant-digits-rejected", "total", {"status": "needs_input"}, summary_amount("0." + "1" * 81))
case("precision-summary-excessive-magnitude-rejected", "total", {"status": "needs_input"}, summary_amount("1e1025"))
case("precision-summary-excessively-small-rejected", "total", {"status": "needs_input"}, summary_amount("1e-1025"))
case("precision-summary-overlong-text-rejected", "total", {"status": "needs_input"}, summary_amount("1." + "0" * 2048))
case("precision-summary-negative-rejected", "total", {"status": "needs_input"}, summary_amount("-0.1"))
case("precision-summary-nonfinite-rejected", "total", {"status": "needs_input"}, summary_amount("NaN"))
case("precision-human-input-still-limited", "allocation", {"status": "needs_input"}, lambda o: o.update(pool=third_expected))

# Exercise actual CLI I/O, Unicode paths and exit status rather than import alone.
cli_input = HERE / "样例输入.json"
cli_output = HERE / "样例结果.json"
cli_input.write_text(json.dumps(examples["software_cost"], ensure_ascii=False), encoding="utf-8-sig")
run = subprocess.run([sys.executable, str(RES / "itom_calc.py"), str(cli_input), "--out", str(cli_output)], capture_output=True, text=True)
cli_value = json.loads(cli_output.read_text(encoding="utf-8")) if cli_output.exists() else {}
cases.append({"id": "cli-bom-unicode-output", "passed": run.returncode == 0 and cli_value.get("result", {}).get("amount") == "113759.04", "returncode": run.returncode, "stderr": run.stderr})
cli_input.write_text('{"mode":"hardware","period":"demo"}', encoding="utf-8")
run = subprocess.run([sys.executable, str(RES / "itom_calc.py"), str(cli_input)], capture_output=True)
cli_value = json.loads(run.stdout.decode("utf-8")) if run.stdout else {}
cases.append({"id": "cli-needs-input-exit-code", "passed": run.returncode == 2 and cli_value.get("status") == "needs_input", "returncode": run.returncode})
cli_input.write_text('{"mode":', encoding="utf-8")
run = subprocess.run([sys.executable, str(RES / "itom_calc.py"), str(cli_input)], capture_output=True)
cli_value = json.loads(run.stdout.decode("utf-8")) if run.stdout else {}
cases.append({"id": "cli-invalid-json", "passed": run.returncode == 2 and cli_value.get("issues", [{}])[0].get("code") == "INVALID_INPUT_FILE", "returncode": run.returncode})
portable = HERE / "portable-probe"
portable.mkdir(exist_ok=True)
shutil.copyfile(RES / "itom_calc.py", portable / "itom_calc.py")
(portable / "input.json").write_text(json.dumps(examples["migration"], ensure_ascii=False), encoding="utf-8")
run = subprocess.run([sys.executable, "itom_calc.py", "input.json", "--out", "output.json"], cwd=portable, capture_output=True)
portable_value = json.loads((portable / "output.json").read_text(encoding="utf-8")) if (portable / "output.json").exists() else {}
cases.append({"id": "cli-portable-standalone", "passed": run.returncode == 0 and portable_value.get("result", {}).get("amount") == "4116.42", "returncode": run.returncode})
report = {"suite": "itom-calculator-regression", "scope": "Deterministic implementation tests; not host-model or full-standard certification", "python": sys.version, "cases": len(cases), "passed": sum(c["passed"] for c in cases), "failed": sum(not c["passed"] for c in cases), "results": cases}
(HERE / "test-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("suite", "cases", "passed", "failed")}, ensure_ascii=False))
for failed in [c for c in cases if not c["passed"]]:
    print(json.dumps(failed, ensure_ascii=False))
sys.exit(1 if report["failed"] else 0)
