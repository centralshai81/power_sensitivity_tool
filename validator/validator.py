from __future__ import annotations

from typing import Dict, List, Any
import pandas as pd


Issue = Dict[str, Any]


def _issue(level: str, sheet: str, row: int, msg: str) -> Issue:
    return {"level": level, "sheet": sheet, "row": row, "msg": msg}


def validate_bus(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    df = data.get("bus", pd.DataFrame())
    if df.empty:
        issues.append(_issue("ERROR", "bus", 0, "bus 工作表为空"))
        return issues

    if df["bus_id"].isna().any():
        rows = df.index[df["bus_id"].isna()].tolist()
        for r in rows:
            issues.append(_issue("ERROR", "bus", r + 2, "节点编号为空"))

    duplicated = df["bus_id"][df["bus_id"].duplicated()]
    for _, value in duplicated.items():
        issues.append(_issue("ERROR", "bus", 0, f"节点编号重复: {value}"))

    for i, row in df.iterrows():
        try:
            vn = float(row["vn_kv"])
            if vn <= 0:
                issues.append(_issue("ERROR", "bus", i + 2, "额定电压必须大于0"))
        except Exception:
            issues.append(_issue("ERROR", "bus", i + 2, "额定电压不是有效数值"))

    return issues


def validate_line(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    bus_ids = set(data["bus"]["bus_id"].astype(str).tolist()) if not data["bus"].empty else set()
    df = data.get("line", pd.DataFrame())
    if df.empty:
        issues.append(_issue("ERROR", "line", 0, "line 工作表为空"))
        return issues

    duplicated = df["line_id"][df["line_id"].duplicated()]
    for _, value in duplicated.items():
        issues.append(_issue("ERROR", "line", 0, f"线路编号重复: {value}"))

    for i, row in df.iterrows():
        from_bus = str(row["from_bus"]) if not pd.isna(row["from_bus"]) else ""
        to_bus = str(row["to_bus"]) if not pd.isna(row["to_bus"]) else ""

        if from_bus not in bus_ids:
            issues.append(_issue("ERROR", "line", i + 2, f"起始节点不存在: {from_bus}"))
        if to_bus not in bus_ids:
            issues.append(_issue("ERROR", "line", i + 2, f"终止节点不存在: {to_bus}"))
        if from_bus == to_bus and from_bus != "":
            issues.append(_issue("ERROR", "line", i + 2, "起始节点与终止节点不能相同"))

        try:
            length = float(row["length_km"])
            if length <= 0:
                issues.append(_issue("ERROR", "line", i + 2, "线路长度必须大于0"))
        except Exception:
            issues.append(_issue("ERROR", "line", i + 2, "线路长度不是有效数值"))

        try:
            r = float(row["r_ohm_per_km"])
            x = float(row["x_ohm_per_km"])
            if r == 0 and x == 0:
                issues.append(_issue("ERROR", "line", i + 2, "单位电阻和单位电抗不能同时为0"))
        except Exception:
            issues.append(_issue("ERROR", "line", i + 2, "线路阻抗参数不是有效数值"))

    return issues


def validate_load(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    bus_ids = set(data["bus"]["bus_id"].astype(str).tolist()) if not data["bus"].empty else set()
    df = data.get("load", pd.DataFrame())
    if df.empty:
        issues.append(_issue("WARNING", "load", 0, "load 工作表为空"))
        return issues

    duplicated = df["load_id"][df["load_id"].duplicated()]
    for _, value in duplicated.items():
        issues.append(_issue("ERROR", "load", 0, f"负荷编号重复: {value}"))

    for i, row in df.iterrows():
        bus_id = str(row["bus_id"]) if not pd.isna(row["bus_id"]) else ""
        if bus_id not in bus_ids:
            issues.append(_issue("ERROR", "load", i + 2, f"接入节点不存在: {bus_id}"))

        try:
            float(row["p_mw"])
            float(row["q_mvar"])
        except Exception:
            issues.append(_issue("ERROR", "load", i + 2, "有功/无功负荷不是有效数值"))

    return issues


def validate_ext_grid(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    bus_ids = set(data["bus"]["bus_id"].astype(str).tolist()) if not data["bus"].empty else set()
    df = data.get("ext_grid", pd.DataFrame())
    if df.empty:
        issues.append(_issue("ERROR", "ext_grid", 0, "ext_grid 工作表为空"))
        return issues

    valid_count = 0
    for i, row in df.iterrows():
        bus_id = str(row["bus_id"]) if not pd.isna(row["bus_id"]) else ""
        if bus_id not in bus_ids:
            issues.append(_issue("ERROR", "ext_grid", i + 2, f"接入节点不存在: {bus_id}"))
        else:
            valid_count += 1

    if valid_count == 0:
        issues.append(_issue("ERROR", "ext_grid", 0, "没有有效的外部电源/平衡节点"))

    return issues


def validate_trafo(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    df = data.get("trafo", pd.DataFrame())
    if df.empty:
        return issues

    bus_ids = set(data["bus"]["bus_id"].astype(str).tolist()) if not data["bus"].empty else set()

    for i, row in df.iterrows():
        hv_bus = str(row["hv_bus"]) if not pd.isna(row["hv_bus"]) else ""
        lv_bus = str(row["lv_bus"]) if not pd.isna(row["lv_bus"]) else ""
        if hv_bus not in bus_ids:
            issues.append(_issue("ERROR", "trafo", i + 2, f"高压侧节点不存在: {hv_bus}"))
        if lv_bus not in bus_ids:
            issues.append(_issue("ERROR", "trafo", i + 2, f"低压侧节点不存在: {lv_bus}"))

        numeric_fields = ["sn_mva", "vn_hv_kv", "vn_lv_kv", "vk_percent", "vkr_percent"]
        for field in numeric_fields:
            try:
                float(row[field])
            except Exception:
                issues.append(_issue("ERROR", "trafo", i + 2, f"{field} 不是有效数值"))

    return issues


def validate_dg(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    df = data.get("dg", pd.DataFrame())
    if df.empty:
        return issues

    bus_ids = set(data["bus"]["bus_id"].astype(str).tolist()) if not data["bus"].empty else set()

    for i, row in df.iterrows():
        bus_id = str(row["bus_id"]) if not pd.isna(row["bus_id"]) else ""
        if bus_id not in bus_ids:
            issues.append(_issue("ERROR", "dg", i + 2, f"接入节点不存在: {bus_id}"))
        try:
            float(row["p_mw"])
        except Exception:
            issues.append(_issue("ERROR", "dg", i + 2, "有功功率不是有效数值"))

    return issues


def validate_switch(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    df = data.get("switch", pd.DataFrame())
    if df.empty:
        return issues

    bus_ids = set(data["bus"]["bus_id"].astype(str).tolist()) if not data["bus"].empty else set()
    line_ids = set(data["line"]["line_id"].astype(str).tolist()) if not data["line"].empty else set()
    trafo_ids = set(data["trafo"]["trafo_id"].astype(str).tolist()) if not data["trafo"].empty else set()

    for i, row in df.iterrows():
        bus = str(row["bus"]) if not pd.isna(row["bus"]) else ""
        element_type = str(row["element_type"]).strip().lower() if not pd.isna(row["element_type"]) else ""
        element_id = str(row["element_id"]) if not pd.isna(row["element_id"]) else ""

        if bus not in bus_ids:
            issues.append(_issue("ERROR", "switch", i + 2, f"所在节点不存在: {bus}"))

        if element_type not in {"line", "trafo", "bus"}:
            issues.append(_issue("ERROR", "switch", i + 2, f"连接设备类型非法: {element_type}"))
        else:
            if element_type == "line" and element_id not in line_ids:
                issues.append(_issue("ERROR", "switch", i + 2, f"线路编号不存在: {element_id}"))
            if element_type == "trafo" and element_id not in trafo_ids:
                issues.append(_issue("ERROR", "switch", i + 2, f"变压器编号不存在: {element_id}"))
            if element_type == "bus" and element_id not in bus_ids:
                issues.append(_issue("ERROR", "switch", i + 2, f"节点编号不存在: {element_id}"))

    return issues


def validate_all(data: Dict[str, pd.DataFrame]) -> List[Issue]:
    issues: List[Issue] = []
    issues.extend(validate_bus(data))
    issues.extend(validate_line(data))
    issues.extend(validate_load(data))
    issues.extend(validate_ext_grid(data))
    issues.extend(validate_trafo(data))
    issues.extend(validate_dg(data))
    issues.extend(validate_switch(data))
    return issues


def summarize_issues(issues: List[Issue]) -> str:
    if not issues:
        return "[INFO] 数据校验通过，无异常。"

    err_cnt = sum(1 for x in issues if x["level"] == "ERROR")
    warn_cnt = sum(1 for x in issues if x["level"] == "WARNING")

    lines = [
        f"[INFO] 数据校验完成: ERROR={err_cnt}, WARNING={warn_cnt}"
    ]
    for item in issues[:20]:
        lines.append(
            f'[{item["level"]}] sheet={item["sheet"]} row={item["row"]} msg={item["msg"]}'
        )
    if len(issues) > 20:
        lines.append(f"... 共 {len(issues)} 条问题，仅显示前 20 条")
    return "\n".join(lines)
