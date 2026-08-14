from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

import pandas as pd

from dataio.excel_reader import read_excel_project
from dataio.normalizer import normalize_all_tables


DEFAULT_PV_VM_PU = 1.0
DEFAULT_PV_Q_MVAR_MIN = -999.0
DEFAULT_PV_Q_MVAR_MAX = 999.0


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _resolve_path(project_root: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return project_root / path


def _to_int_bus_id(value: Any) -> int:
    return int(float(str(value).strip()))


def _float_or_default(value: Any, default: float) -> float:
    if pd.isna(value):
        return default
    return float(value)


def extract_pv_node_settings_from_excel(excel_path: str | Path) -> Dict[str, Dict[str, float]]:
    raw_data = read_excel_project(str(excel_path))
    data = normalize_all_tables(raw_data)
    dg_df = data.get("dg", pd.DataFrame())

    if dg_df.empty or "mode" not in dg_df.columns:
        return {}

    pv_rows = dg_df[dg_df["mode"].astype(str).str.strip().str.upper() == "PV"]
    settings: Dict[str, Dict[str, float]] = {}

    for _, row in pv_rows.iterrows():
        bus_id = str(_to_int_bus_id(row["bus_id"]))
        settings[bus_id] = {
            "p_mw": float(row["p_mw"]),
            "vm_pu": _float_or_default(row.get("vm_pu", DEFAULT_PV_VM_PU), DEFAULT_PV_VM_PU),
            "q_mvar_min": _float_or_default(row.get("q_mvar_min", DEFAULT_PV_Q_MVAR_MIN), DEFAULT_PV_Q_MVAR_MIN),
            "q_mvar_max": _float_or_default(row.get("q_mvar_max", DEFAULT_PV_Q_MVAR_MAX), DEFAULT_PV_Q_MVAR_MAX),
        }

    return dict(sorted(settings.items(), key=lambda item: int(item[0])))


def _sync_pv_quick_scenarios(analysis_cfg: Dict[str, Any], pv_nodes: List[int]) -> None:
    scenarios = analysis_cfg.get("quick_test_scenarios")
    if not isinstance(scenarios, list):
        return

    synced = []
    seen = set()

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue

        if str(scenario.get("node_type", "")).upper() != "PV":
            synced.append(scenario)
            continue

        for bus in pv_nodes:
            new_scenario = dict(scenario)
            new_scenario["target_bus"] = bus
            key = (
                new_scenario.get("network_type"),
                new_scenario.get("node_type"),
                new_scenario.get("target_bus"),
                new_scenario.get("disturbance_type"),
                new_scenario.get("disturbance_value"),
            )
            if key not in seen:
                synced.append(new_scenario)
                seen.add(key)

    analysis_cfg["quick_test_scenarios"] = synced


def sync_pv_config_from_excel(
    project_root: str | Path,
    network_config_path: str | Path,
    analysis_config_path: str | Path,
) -> Dict[str, Any]:
    """
    以 Excel dg 工作表中 控制模式(PQ/PV)=PV 的行同步 PV 配置。
    同步范围：
    - network_config_v7.json: pv_node_settings
    - analysis_config_v7.json: pv_test_nodes
    - analysis_config_v7.json: quick_test_scenarios 中的 PV 场景目标节点
    """
    root = Path(project_root)
    network_path = Path(network_config_path)
    analysis_path = Path(analysis_config_path)

    network_cfg = _load_json(network_path)
    if str(network_cfg.get("network_source", "")).strip().lower() != "excel":
        return {"synced": False, "reason": "network_source 不是 excel"}

    excel_input_file = network_cfg.get("excel_input_file", "")
    if not excel_input_file:
        return {"synced": False, "reason": "excel_input_file 为空"}

    excel_path = _resolve_path(root, str(excel_input_file))
    if not excel_path.exists():
        return {"synced": False, "reason": f"Excel 输入文件不存在: {excel_path}"}

    pv_node_settings = extract_pv_node_settings_from_excel(excel_path)
    pv_nodes = [int(k) for k in pv_node_settings.keys()]

    network_cfg["pv_node_settings"] = pv_node_settings
    _save_json(network_path, network_cfg)

    analysis_cfg = _load_json(analysis_path)
    analysis_cfg["pv_test_nodes"] = pv_nodes
    _sync_pv_quick_scenarios(analysis_cfg, pv_nodes)
    _save_json(analysis_path, analysis_cfg)

    return {
        "synced": True,
        "excel_input_file": str(excel_path),
        "pv_nodes": pv_nodes,
        "pv_node_count": len(pv_nodes),
    }
