from __future__ import annotations

from typing import Dict, Any, List


def validate_project_config(cfg: Dict[str, Any]) -> List[str]:
    """
    返回错误列表；为空表示通过。
    """
    errors: List[str] = []

    # 必要字段
    required = [
        "network_source",
        "sn_mva",
        "output_dir",
        "pq_test_nodes",
        "pv_test_nodes",
        "voltage_sag_levels",
        "reactive_disturbance_levels",
        "pv_node_settings",
    ]
    for k in required:
        if k not in cfg:
            errors.append(f"缺少必要配置项: {k}")

    source = str(cfg.get("network_source", "")).lower()
    if source not in {"excel", "matpower"}:
        errors.append(f"network_source 只能是 excel 或 matpower，当前为: {source}")

    if source == "excel" and not cfg.get("excel_input_file"):
        errors.append("当 network_source=excel 时，必须提供 excel_input_file")

    try:
        if float(cfg.get("sn_mva", 0)) <= 0:
            errors.append("sn_mva 必须大于0")
    except Exception:
        errors.append("sn_mva 必须是有效数值")

    for key in ["pq_test_nodes", "pv_test_nodes", "voltage_sag_levels", "reactive_disturbance_levels"]:
        val = cfg.get(key, [])
        if not isinstance(val, list):
            errors.append(f"{key} 必须是列表")

    pv_cfg = cfg.get("pv_node_settings", {})
    if not isinstance(pv_cfg, dict):
        errors.append("pv_node_settings 必须是字典")
    else:
        for bus, params in pv_cfg.items():
            if not isinstance(params, dict):
                errors.append(f"pv_node_settings[{bus}] 必须是字典")
                continue
            if "p_mw" not in params or "vm_pu" not in params:
                errors.append(f"pv_node_settings[{bus}] 缺少 p_mw 或 vm_pu")

    qtest = cfg.get("quick_test", None)
    if qtest is not None and not isinstance(qtest, bool):
        errors.append("quick_test 必须是布尔值")

    return errors
