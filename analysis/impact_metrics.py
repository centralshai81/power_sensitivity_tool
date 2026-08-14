# analysis/impact_metrics.py

from __future__ import annotations

from typing import Dict, Any, List
import pandas as pd


def calc_voltage_impact_radius(delta_bus_df: pd.DataFrame, threshold: float = 0.005) -> Dict[str, Any]:
    """
    根据电压变化阈值统计影响范围。
    """
    if delta_bus_df.empty:
        return {
            "affected_bus_count": 0,
            "affected_buses": [],
            "max_abs_delta_v": 0.0,
            "mean_abs_delta_v": 0.0
        }

    affected = delta_bus_df.loc[delta_bus_df["delta_vm_pu"].abs() >= threshold].copy()

    return {
        "affected_bus_count": int(len(affected)),
        "affected_buses": affected["mp_bus"].astype(int).tolist(),
        "max_abs_delta_v": float(delta_bus_df["delta_vm_pu"].abs().max()),
        "mean_abs_delta_v": float(delta_bus_df["delta_vm_pu"].abs().mean())
    }


def identify_key_lines(delta_line_df: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    """
    按线路有功潮流变化绝对值排序，识别关键线路。
    """
    if delta_line_df.empty:
        return pd.DataFrame(columns=["line_id", "delta_p_from_mw", "delta_q_from_mvar", "score"])

    df = delta_line_df.copy()
    df["score"] = df["delta_p_from_mw"].abs() + df["delta_q_from_mvar"].abs()

    cols = ["line_id", "delta_p_from_mw", "delta_q_from_mvar", "score"]
    return df.sort_values("score", ascending=False)[cols].head(top_k).reset_index(drop=True)


def rank_sensitive_buses(sens_df: pd.DataFrame, value_col: str, top_k: int = 10) -> pd.DataFrame:
    """
    对单场景节点灵敏度进行排序。
    """
    if sens_df.empty or value_col not in sens_df.columns:
        return pd.DataFrame(columns=["mp_bus", value_col, "abs_value"])

    df = sens_df.copy()
    df["abs_value"] = df[value_col].abs()

    return df.sort_values("abs_value", ascending=False)[["mp_bus", value_col, "abs_value"]].head(top_k).reset_index(drop=True)


def evaluate_impacts(
    sim_results: List[Dict[str, Any]],
    sensitivity_results: Dict[str, pd.DataFrame],
    cfg: Dict[str, Any]
) -> Dict[str, Any]:
    """
    汇总所有场景的影响指标。
    """
    threshold = float(cfg.get("voltage_impact_threshold", 0.005))
    scenario_rows = []
    key_lines_map = {}
    sensitive_buses_map = {}

    for item in sim_results:
        scenario_id = item.get("scenario_id")
        if not item.get("success", False):
            scenario_rows.append({
                "scenario_id": scenario_id,
                "success": False,
                "affected_bus_count": None,
                "max_abs_delta_v": None,
                "mean_abs_delta_v": None
            })
            continue

        delta_bus = item["delta_result"]["delta_bus"]
        delta_line = item["delta_result"]["delta_line"]
        scenario = item["scenario_meta"]

        radius_info = calc_voltage_impact_radius(delta_bus, threshold=threshold)
        key_lines_df = identify_key_lines(delta_line, top_k=5)

        if scenario["disturbance_type"] == "voltage_sag":
            # VV 灵敏度
            from analysis.sensitivity_calc import calc_voltage_to_voltage_sensitivity
            sens_df = calc_voltage_to_voltage_sensitivity(item)
            sensitive_df = rank_sensitive_buses(sens_df, "sensitivity_vv", top_k=10)
        else:
            from analysis.sensitivity_calc import calc_qv_sensitivity
            sens_df = calc_qv_sensitivity(item)
            sensitive_df = rank_sensitive_buses(sens_df, "sensitivity_qv", top_k=10)

        key_lines_map[scenario_id] = key_lines_df
        sensitive_buses_map[scenario_id] = sensitive_df

        row = {
            "scenario_id": scenario_id,
            "success": True,
            "network_type": scenario["network_type"],
            "node_type": scenario["node_type"],
            "target_bus": scenario["target_bus"],
            "disturbance_type": scenario["disturbance_type"],
            "disturbance_value": scenario["disturbance_value"],
            "affected_bus_count": radius_info["affected_bus_count"],
            "max_abs_delta_v": radius_info["max_abs_delta_v"],
            "mean_abs_delta_v": radius_info["mean_abs_delta_v"]
        }
        scenario_rows.append(row)

    impact_summary = pd.DataFrame(scenario_rows)

    return {
        "impact_summary": impact_summary,
        "key_lines_map": key_lines_map,
        "sensitive_buses_map": sensitive_buses_map
    }