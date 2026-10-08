#!/usr/bin/env python3
"""Restricted GB/T 28827.7-2022 arithmetic helper. Python 3.9+, standard library.

This validates declared inputs, not the truth/applicability of supporting evidence.
No market defaults, no external FP counting, no 8.2.2 pricing, no multi-class
security pricing. See CALCULATOR.md for contracts and source restrictions.
"""
import argparse
from decimal import Decimal, InvalidOperation, localcontext
import json
from pathlib import Path
import re
import sys

VERSION = "1.0.0-restricted"
ZERO = Decimal("0")
ONE = Decimal("1")
ACTIVITIES = {"routine", "response", "improvement", "assessment"}
MANAGEMENT = {"planning", "delivery", "quality", "review"}
LABOR_UNITS = {"person_hour", "person_day", "person_month"}
OTHER = ("direct_nonhuman", "indirect_labor", "indirect_nonhuman")
NOTICE = "只校验声明输入与算术；不验证证据真实性、参数适用性或全标准符合性。"


class InputError(ValueError):
    def __init__(self, message, code="INPUT_REQUIRED"):
        super().__init__(message)
        self.code = code


def need(obj, key):
    if key not in obj or obj[key] is None:
        raise InputError("缺少 " + key)
    return obj[key]


def txt(obj, key):
    value = need(obj, key)
    if not isinstance(value, str) or not value.strip():
        raise InputError(key + " 必须是非空文本")
    return value.strip()


def number(value, name, positive=False):
    if not isinstance(value, str) or not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", value):
        raise InputError(name + " 必须是有限十进制字符串")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise InputError(name + " 不是有效十进制数") from None
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise InputError(name + (" 必须大于0" if positive else " 必须非负"))
    if len(result.as_tuple().digits) > 28 or abs(result.as_tuple().exponent) > 100:
        raise InputError(name + " 超出实现精度限制（28位输入数字、指数绝对值≤100）")
    return result


def num(obj, key, positive=False):
    return number(need(obj, key), key, positive)


def integer(obj, key, positive=False):
    result = num(obj, key, positive)
    if result != result.to_integral_value():
        raise InputError(key + " 必须为整数")
    return int(result)


def flag(obj, key):
    value = need(obj, key)
    if type(value) is not bool:
        raise InputError(key + " 必须为布尔值")
    return value


def yes(obj, key):
    if not flag(obj, key):
        raise InputError(key + " 尚未确认")


def array(obj, key, empty=False):
    values = need(obj, key)
    if not isinstance(values, list) or (not empty and not values):
        raise InputError(key + " 必须为" + ("" if empty else "非空") + "数组")
    if any(not isinstance(value, dict) for value in values):
        raise InputError(key + " 每项必须为对象")
    ids = [txt(value, "id") for value in values]
    if len(set(ids)) != len(ids):
        raise InputError(key + " 存在重复id", "DUPLICATE")
    return values


def exact(obj, key, allowed):
    value = txt(obj, key)
    if value not in allowed:
        raise InputError(key + " 不支持: " + value)
    return value


def s(value):
    value = format(value, "f")
    return value.rstrip("0").rstrip(".") if "." in value else value


def issue(code, message):
    return {"code": code, "message": message}


def result(mode, data, status="calculated", issues=None):
    return {"calculator_version": VERSION, "mode": mode, "status": status,
            "result": data, "issues": issues or [], "notice": NOTICE,
            "precision": "Decimal 80 significant digits; no currency rounding"}


def inherited(obj):
    items = obj.get("unresolved_issues", [])
    if not isinstance(items, list) or any(not isinstance(i, dict) for i in items):
        raise InputError("unresolved_issues 必须为问题对象数组")
    return [issue(txt(i, "code"), txt(i, "message")) for i in items]


def monetary(obj, data, subtotal, missing, issues=None, domain=None, level="service_total"):
    issues = list(issues or []) + inherited(obj)
    for key in missing:
        issues.append(issue("UNKNOWN_COST", key + " 未确定；不得视为0"))
    status = "needs_review" if any(i["code"] != "UNKNOWN_COST" for i in issues) else ("partial" if issues else "calculated")
    summary = {"id": txt(obj, "scope_id"), "scope_id": txt(obj, "scope_id"),
               "domain": domain or obj["mode"], "period": txt(obj, "period"),
               "currency": txt(obj, "currency"), "level": level, "status": status,
               "amount": s(subtotal) if status == "calculated" else None,
               "known_subtotal": s(subtotal), "issues": issues,
               "security_scope_count": "1" if obj["mode"] == "security" else "0"}
    if obj["mode"] == "security":
        summary["security_scope_size"] = str(integer(obj, "scope_size", positive=True))
    data.update({"amount": summary["amount"], "known_subtotal": summary["known_subtotal"],
                 "currency": summary["currency"], "missing_costs": missing})
    output = result(obj["mode"], data, status, issues)
    output["summary"] = summary
    return output


def optional_costs(obj, keys=OTHER):
    costs = obj.get("other_costs", {})
    if not isinstance(costs, dict):
        raise InputError("other_costs 必须为对象")
    if set(costs) - set(keys):
        raise InputError("other_costs 含不支持的费用类型")
    data, missing, total = {}, [], ZERO
    for key in keys:
        value = costs.get(key)
        if value is None:
            missing.append(key)
            data[key] = None
        else:
            value = number(value, key)
            data[key] = s(value)
            total += value
    return data, missing, total


def coverage(obj, rows, allowed):
    excluded = obj.get("excluded_categories", {})
    if not isinstance(excluded, dict) or set(excluded) - allowed:
        raise InputError("excluded_categories 仅可列支持的活动类别")
    if any(not isinstance(v, str) or not v.strip() for v in excluded.values()):
        raise InputError("裁剪活动必须说明依据")
    present = {exact(row, "category", allowed) for row in rows}
    if present & set(excluded):
        raise InputError("活动不能同时纳入与裁剪")
    if present | set(excluded) != allowed:
        raise InputError("四类活动尚未完整盘点（纳入或有依据裁剪）")


def unit_workload(obj):
    unit = exact(obj, "workload_unit", LABOR_UNITS)
    rows = array(obj, "activities")
    coverage(obj, rows, ACTIVITIES)
    out, total = [], ZERO
    for row in rows:
        effort, frequency = num(row, "effort"), integer(row, "frequency")
        amount = effort * frequency
        out.append({"id": row["id"], "category": row["category"], "workload": s(amount)})
        total += amount
    return result(obj["mode"], {"period": obj["period"], "workload_unit": unit,
                  "basis": "one_object_per_period", "workload": s(total), "activities": out})


def allocation(obj):
    basis_unit = txt(obj, "basis_unit")
    txt(obj, "basis_source")
    pool, part, whole = num(obj, "pool"), num(obj, "numerator"), num(obj, "denominator", True)
    if part > whole:
        raise InputError("分子不能大于分母")
    out = pool * part / whole
    return monetary(obj, {"basis_unit": basis_unit, "share": s(part / whole),
                         "allocated_amount": s(out)}, out, [], level="cost_component")


def class_cost(obj):
    mode = obj["mode"]
    exact(obj, "workload_unit", {"person_day"})
    currency = txt(obj, "currency")
    exact(obj, "rate_unit", {currency + "/person_day"})
    rows = array(obj, "classes")
    if mode == "management":
        coverage(obj, rows, MANAGEMENT)
    scope_size = integer(obj, "scope_size", True) if mode == "security" else len(rows)
    if mode == "security" and scope_size < len(rows):
        raise InputError("scope_size 不得小于已提供安全类别数")
    multi_security = mode == "security" and scope_size != 1
    records, total_work, direct = [], ZERO, ZERO
    for row in rows:
        q = integer(row, "occurrences" if mode == "management" else "quantity")
        unit = num(row, "unit_workload")
        factor = ONE if mode == "management" else num(row, "workload_factor")
        work = q * unit * factor
        rec = {"id": row["id"], "workload": s(work), "direct_labor": None}
        if not multi_security:
            cost = work * num(row, "rate") * num(row, "price_factor")
            direct += cost
            rec["direct_labor"] = s(cost)
        total_work += work
        records.append(rec)
    other, missing, extra = optional_costs(obj)
    data = {"classes": records, "workload": s(total_work), "workload_unit": "person_day",
            "workload_complete": scope_size == len(rows),
            "direct_labor": None if multi_security else s(direct), "other_costs": other}
    issues = [issue("S01/N01", "整个待测安全范围不是单类别；仅计算已给工作量，禁止多类别成本及拆分绕过")] if multi_security else []
    if multi_security:
        missing.append("direct_labor")
    return monetary(obj, data, direct + extra, missing, issues)


def software_size(obj):
    kind = exact(obj, "size_unit", {"FP", "set"})
    raw = num(obj, "size")
    txt(obj, "count_source")
    if kind == "FP":
        txt(obj, "count_method")
        delivered, special = flag(obj, "delivered"), flag(obj, "special_requirements")
        if obj.get("creep_factor") is None:
            if delivered and not special:
                factor, basis = ONE, "8.3.1已交付且无特殊要求之注"
            else:
                raise InputError("需求蔓延因子未知，不能默认1")
        else:
            factor, basis = num(obj, "creep_factor"), txt(obj, "factor_source")
        adjusted = raw * factor
        data = {"original_size": s(raw), "adjusted_size": s(adjusted), "size_unit": "FP",
                "creep_factor": s(factor), "factor_source": basis}
    else:
        integer(obj, "size")
        txt(obj, "factor_source")
        adjusted = raw * num(obj, "level_factor") * num(obj, "type_factor")
        data = {"original_size": s(raw), "adjusted_size": s(adjusted), "size_unit": "adjusted_set"}
    return result(obj["mode"], data)


def software_workload(obj):
    unit = exact(obj, "workload_unit", LABOR_UNITS)
    size_unit = exact(obj, "size_unit", {"FP", "adjusted_set"})
    exact(obj, "productivity_unit", {unit + "/" + size_unit})
    txt(obj, "parameter_source")
    amount = num(obj, "size") * num(obj, "productivity") * num(obj, "mlf") * num(obj, "mcf") * num(obj, "msf")
    return result(obj["mode"], {"workload": s(amount), "workload_unit": unit, "size_unit": size_unit})


def software_cost(obj):
    if txt(obj, "method") != "8.2.1":
        return monetary(obj, {}, ZERO, ["software_cost"],
                        [issue("S02/N02", "本版不执行8.2.2功能点单价成本路径")], domain="software")
    yes(obj, "composite_rate_confirmed")
    if any(k in obj for k in ("other_costs", "indirect_labor", "indirect_nonhuman", "profit")):
        raise InputError("综合费率已含间接成本和毛利润；本模式只额外归集direct_nonhuman", "DOUBLE_COUNT")
    rows, total, records = array(obj, "classes"), ZERO, []
    currency = txt(obj, "currency")
    for row in rows:
        unit = exact(row, "workload_unit", LABOR_UNITS)
        rate_unit = exact(row, "rate_unit", {currency + "/" + u for u in LABOR_UNITS})
        target = rate_unit.split("/")[1]
        work, rate = num(row, "workload"), num(row, "rate")
        converted = work
        if unit != target:
            conversion = need(row, "conversion")
            if not isinstance(conversion, dict):
                raise InputError("conversion 必须为对象")
            exact(conversion, "from_unit", {unit})
            exact(conversion, "to_unit", {target})
            txt(conversion, "source")
            if ("multiplier" in conversion) == ("divisor" in conversion):
                raise InputError("conversion必须且只能提供multiplier或divisor之一")
            converted = (work * num(conversion, "multiplier", True) if "multiplier" in conversion
                         else work / num(conversion, "divisor", True))
        elif "conversion" in row:
            raise InputError("相同单位不应重复换算")
        amount = converted * rate
        total += amount
        records.append({"id": row["id"], "rated_workload": s(converted), "rated_workload_unit": target,
                        "composite_cost": s(amount)})
    value = obj.get("direct_nonhuman")
    missing = ["direct_nonhuman"] if value is None else []
    extra = ZERO if value is None else number(value, "direct_nonhuman")
    return monetary(obj, {"method": "8.2.1", "classes": records, "composite_cost": s(total),
                         "direct_nonhuman": None if missing else s(extra)}, total + extra, missing, domain="software")


def migration(obj):
    exact(obj, "workload_unit", {"person_day"})
    currency = txt(obj, "currency")
    exact(obj, "rate_unit", {currency + "/person_day"})
    txt(obj, "rate_source")
    yes(obj, "common_rate_applicable")
    rate = num(obj, "rate")
    rows, total_work, out = array(obj, "classes"), ZERO, []
    for row in rows:
        txt(row, "quantity_unit")
        factors = need(row, "factors")
        if not isinstance(factors, dict) or set(factors) != {"service", "location", "batch"}:
            raise InputError("factors须明确service/location/batch三因子")
        values = []
        for key in ("service", "location", "batch"):
            item = factors[key]
            if not isinstance(item, dict):
                raise InputError(key + "因子必须为对象")
            applicable = flag(item, "applicable")
            txt(item, "source")
            value = num(item, "value")
            if not applicable and value != ONE:
                raise InputError("不适用因子只有明确依据取1，不能填其他值")
            values.append((applicable, value))
        count = sum(1 for applicable, _ in values if applicable)
        if count != 3 and count != 1:
            raise InputError("本版仅支持三因子均有适用值，或明确仅一个适用、其余有依据为1")
        work = num(row, "quantity") * num(row, "unit_workload") * num(row, "personnel_factor")
        for _, value in values:
            work *= value
        total_work += work
        out.append({"id": row["id"], "workload": s(work), "direct_labor": s(work * rate)})
    other, missing, extra = optional_costs(obj)
    return monetary(obj, {"classes": out, "workload": s(total_work), "workload_unit": "person_day",
                         "direct_labor": s(total_work * rate), "other_costs": other}, total_work * rate + extra, missing)


def nonhuman(obj):
    rows = array(obj, "items", empty=True)
    complete = flag(obj, "coverage_complete")
    yes(obj, "non_overlap_confirmed")
    total, out, missing = ZERO, [], []
    for row in rows:
        txt(row, "basis")
        if txt(row, "period") != obj["period"]:
            raise InputError("费用期间不一致")
        if txt(row, "currency") != txt(obj, "currency"):
            raise InputError("费用币种不一致")
        value = row.get("amount")
        if value is None:
            missing.append(row["id"])
            out.append({"id": row["id"], "amount": None})
        else:
            amount = number(value, "amount")
            total += amount
            out.append({"id": row["id"], "amount": s(amount)})
    if not complete:
        missing.append("coverage_incomplete")
    return monetary(obj, {"items": out}, total, missing, level="cost_component")


def total_cost(obj):
    rows = array(obj, "entries")
    yes(obj, "non_overlap_confirmed")
    complete = flag(obj, "coverage_complete")
    level = exact(obj, "expected_level", {"service_total", "cost_component"})
    scopes = [txt(row, "scope_id") for row in rows]
    if len(set(scopes)) != len(scopes):
        raise InputError("scope_id 重复；请核对已含费用或重叠范围", "DUPLICATE")
    security_count = sum(1 if row.get("domain") == "security" else
                         integer(row, "security_scope_count") if row.get("domain") == "total" else 0
                         for row in rows)
    issues, missing, known, out = [], [], ZERO, []
    for row in rows:
        if txt(row, "period") != obj["period"] or txt(row, "currency") != txt(obj, "currency"):
            raise InputError("分项期间或币种不一致")
        if txt(row, "level") != level:
            raise InputError("直接人力/构成金额与服务总额层级不能混合")
        status = exact(row, "status", {"calculated", "partial", "needs_review", "needs_input"})
        row_issues = need(row, "issues")
        if not isinstance(row_issues, list) or any(not isinstance(i, dict) for i in row_issues):
            raise InputError("summary.issues必须为问题对象数组")
        issues.extend(issue(txt(i, "code"), txt(i, "message")) for i in row_issues)
        blocked = False
        if txt(row, "domain") == "security":
            size = integer(row, "security_scope_size", True)
            if security_count > 1 or size != 1:
                issues.append(issue("S01/N01", "多安全分类/多单类分项不能合并成本；该项未计入已知小计"))
                blocked = True
        elif row["domain"] == "total" and integer(row, "security_scope_count") and security_count > 1:
            issues.append(issue("S01/N01", "嵌套汇总含多个安全分类；该子汇总未计入已知小计"))
            blocked = True
        if status == "calculated":
            amount = num(row, "amount")
            if num(row, "known_subtotal") != amount:
                raise InputError("完整金额与已知小计不一致")
            if row_issues:
                raise InputError("calculated状态仍含未解决问题，不能伪装完整")
        else:
            if row.get("amount") is not None:
                raise InputError("非完整分项amount必须为null")
            amount = num(row, "known_subtotal")
            missing.append(row["id"])
            if status == "needs_review" and not row_issues:
                issues.append(issue("UPSTREAM_REVIEW", row["id"] + " 上游待核查状态保留"))
        if blocked:
            missing.append(row["id"])
        else:
            known += amount
        out.append({"id": row["id"], "included_known_subtotal": "0" if blocked else s(amount),
                    "status": status, "excluded_pending_review": blocked})
    if not complete:
        missing.append("coverage_incomplete")
    output = monetary(obj, {"entries": out}, known, sorted(set(missing)), issues, domain="total", level=level)
    output["summary"]["security_scope_count"] = str(security_count)
    return output


MODES = {"unit_workload": unit_workload, "allocation": allocation,
         "environment": class_cost, "hardware": class_cost, "security": class_cost,
         "management": class_cost, "software_size": software_size,
         "software_workload": software_workload, "software_cost": software_cost,
         "migration": migration, "nonhuman": nonhuman, "total": total_cost}


def calculate(obj):
    mode = obj.get("mode", "unknown") if isinstance(obj, dict) else "unknown"
    try:
        if not isinstance(obj, dict):
            raise InputError("JSON根节点必须为对象")
        mode = exact(obj, "mode", set(MODES))
        txt(obj, "period")
        with localcontext() as context:
            context.prec = 80
            return MODES[mode](obj)
    except (InputError, InvalidOperation) as error:
        return result(mode, {}, "needs_input", [issue(getattr(error, "code", "INVALID_NUMBER"), str(error))])


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        output = calculate(data)
    except (OSError, json.JSONDecodeError) as error:
        output = result("unknown", {}, "needs_input", [issue("INVALID_INPUT_FILE", str(error))])
    rendered = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 2 if output["status"] == "needs_input" else 0


if __name__ == "__main__":
    sys.exit(main())
