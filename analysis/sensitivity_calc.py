# analysis/sensitivity_calc.py

from __future__ import annotations

from typing import Dict, Any, List
import numpy as np
import pandas as pd


def calc_voltage_to_voltage_sensitivity(sim_result: Dict[str, Any]) -> pd.DataFrame:
    """
    计算单场景下的电压-电压灵敏度：
        S_vv(j) = ΔV_j / ΔV_i
    其中 i 为目标扰动节点，j 为观测节点。
    """
    if not sim_result.get("success", False):
        return pd.DataFrame(columns=["mp_bus", "delta_vm_pu", "sensitivity_vv"])

    scenario = sim_result["scenario_meta"]
    target_bus = int(scenario["target_bus"])

    delta_bus = sim_result["delta_result"]["delta_bus"].copy()
    target_row = delta_bus.loc[delta_bus["mp_bus"] == target_bus]

    if target_row.empty:
        return pd.DataFrame(columns=["mp_bus", "delta_vm_pu", "sensitivity_vv"])

    delta_vi = float(target_row.iloc[0]["delta_vm_pu"])

    if abs(delta_vi) < 1e-12:
        delta_bus["sensitivity_vv"] = np.nan
    else:
        delta_bus["sensitivity_vv"] = delta_bus["delta_vm_pu"] / delta_vi

    return delta_bus[["mp_bus", "delta_vm_pu", "sensitivity_vv"]].sort_values("mp_bus").reset_index(drop=True)


def calc_qv_sensitivity(sim_result: Dict[str, Any]) -> pd.DataFrame:
    """
    计算单场景下的 Q-V 灵敏度：
        S_qv(j) = ΔV_j / ΔQ_i
    """
    if not sim_result.get("success", False):
        return pd.DataFrame(columns=["mp_bus", "delta_vm_pu", "sensitivity_qv"])

    scenario = sim_result["scenario_meta"]
    disturbance_type = scenario["disturbance_type"]

    if disturbance_type != "reactive_variation":
        return pd.DataFrame(columns=["mp_bus", "delta_vm_pu", "sensitivity_qv"])

    delta_q = float(scenario["disturbance_value"])
    delta_bus = sim_result["delta_result"]["delta_bus"].copy()

    if abs(delta_q) < 1e-12:
        delta_bus["sensitivity_qv"] = np.nan
    else:
        delta_bus["sensitivity_qv"] = delta_bus["delta_vm_pu"] / delta_q

    return delta_bus[["mp_bus", "delta_vm_pu", "sensitivity_qv"]].sort_values("mp_bus").reset_index(drop=True)


def calc_flow_sensitivity(sim_result: Dict[str, Any]) -> pd.DataFrame:
    """
    计算线路潮流灵敏度：
      - 电压暂降场景: ΔP_line / ΔV_i, ΔQ_line / ΔV_i
      - 无功扰动场景: ΔP_line / ΔQ_i, ΔQ_line / ΔQ_i
    统一输出为 sens_pflow, sens_qflow
    """
    if not sim_result.get("success", False):
        return pd.DataFrame(columns=["line_id", "sens_pflow", "sens_qflow", "input_change"])

    scenario = sim_result["scenario_meta"]
    delta_line = sim_result["delta_result"]["delta_line"].copy()

    if scenario["disturbance_type"] == "voltage_sag":
        target_bus = int(scenario["target_bus"])
        delta_bus = sim_result["delta_result"]["delta_bus"]
        target_row = delta_bus.loc[delta_bus["mp_bus"] == target_bus]
        if target_row.empty:
            delta_line["sens_pflow"] = np.nan
            delta_line["sens_qflow"] = np.nan
            delta_line["input_change"] = np.nan
            return delta_line[["line_id", "sens_pflow", "sens_qflow", "input_change"]]

        input_change = float(target_row.iloc[0]["delta_vm_pu"])
    else:
        input_change = float(scenario["disturbance_value"])

    if abs(input_change) < 1e-12:
        delta_line["sens_pflow"] = np.nan
        delta_line["sens_qflow"] = np.nan
    else:
        delta_line["sens_pflow"] = delta_line["delta_p_from_mw"] / input_change
        delta_line["sens_qflow"] = delta_line["delta_q_from_mvar"] / input_change

    delta_line["input_change"] = input_change

    return delta_line[["line_id", "sens_pflow", "sens_qflow", "input_change"]].sort_values("line_id").reset_index(drop=True)


def build_bus_sensitivity_matrix(
    sim_results: List[Dict[str, Any]],
    sensitivity_type: str = "vv"
) -> pd.DataFrame:
    """
    将多个场景的节点灵敏度汇总为矩阵：
    行 = source_bus(场景)
    列 = obs_bus
    """
    rows = []

    for item in sim_results:
        if not item.get("success", False):
            continue

        scenario = item["scenario_meta"]

        if sensitivity_type == "vv" and scenario["disturbance_type"] == "voltage_sag":
            sens_df = calc_voltage_to_voltage_sensitivity(item)
            value_col = "sensitivity_vv"
        elif sensitivity_type == "qv" and scenario["disturbance_type"] == "reactive_variation":
            sens_df = calc_qv_sensitivity(item)
            value_col = "sensitivity_qv"
        else:
            continue

        row = {
            "scenario_id": item["scenario_id"],
            "network_type": scenario["network_type"],
            "node_type": scenario["node_type"],
            "target_bus": scenario["target_bus"],
            "disturbance_type": scenario["disturbance_type"],
            "disturbance_value": scenario["disturbance_value"]
        }

        for _, r in sens_df.iterrows():
            row[f"bus_{int(r['mp_bus'])}"] = r[value_col]

        rows.append(row)

    return pd.DataFrame(rows)


def build_line_sensitivity_matrix(sim_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    将多个场景的线路潮流灵敏度汇总为矩阵。
    """
    rows = []

    for item in sim_results:
        if not item.get("success", False):
            continue

        scenario = item["scenario_meta"]
        sens_df = calc_flow_sensitivity(item)

        row = {
            "scenario_id": item["scenario_id"],
            "network_type": scenario["network_type"],
            "node_type": scenario["node_type"],
            "target_bus": scenario["target_bus"],
            "disturbance_type": scenario["disturbance_type"],
            "disturbance_value": scenario["disturbance_value"]
        }

        for _, r in sens_df.iterrows():
            row[f"line_{int(r['line_id'])}_p"] = r["sens_pflow"]
            row[f"line_{int(r['line_id'])}_q"] = r["sens_qflow"]

        rows.append(row)

    return pd.DataFrame(rows)


def calculate_all_sensitivities(sim_results: List[Dict[str, Any]], cfg: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    汇总所有灵敏度结果。
    """
    vv_matrix = build_bus_sensitivity_matrix(sim_results, sensitivity_type="vv")
    qv_matrix = build_bus_sensitivity_matrix(sim_results, sensitivity_type="qv")
    flow_matrix = build_line_sensitivity_matrix(sim_results)

    return {
        "vv_matrix": vv_matrix,
        "qv_matrix": qv_matrix,
        "flow_matrix": flow_matrix
    }