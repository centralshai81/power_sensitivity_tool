# simulation/powerflow_runner.py

from __future__ import annotations

from typing import Dict, Any

import pandas as pd
import pandapower as pp


def extract_bus_results(net: pp.pandapowerNet) -> pd.DataFrame:
    df = pd.DataFrame({
        "pp_bus": net.bus.index,
        "mp_bus": net.bus["mp_bus"].values if "mp_bus" in net.bus.columns else (net.bus.index + 1),
        "vm_pu": net.res_bus["vm_pu"].values,
        "va_degree": net.res_bus["va_degree"].values
    })
    return df.sort_values("mp_bus").reset_index(drop=True)


def extract_line_results(net: pp.pandapowerNet) -> pd.DataFrame:
    if net.line.empty:
        return pd.DataFrame(columns=[
            "line_id", "from_pp_bus", "to_pp_bus", "p_from_mw", "q_from_mvar",
            "p_to_mw", "q_to_mvar", "loading_percent"
        ])

    df = pd.DataFrame({
        "line_id": net.line.index,
        "from_pp_bus": net.line["from_bus"].values,
        "to_pp_bus": net.line["to_bus"].values,
        "p_from_mw": net.res_line["p_from_mw"].values,
        "q_from_mvar": net.res_line["q_from_mvar"].values,
        "p_to_mw": net.res_line["p_to_mw"].values,
        "q_to_mvar": net.res_line["q_to_mvar"].values,
        "loading_percent": net.res_line["loading_percent"].values
    })
    return df


def calc_system_loss(net: pp.pandapowerNet) -> Dict[str, float]:
    if net.line.empty:
        return {"p_loss_mw": 0.0, "q_loss_mvar": 0.0}

    p_loss = (net.res_line["p_from_mw"] + net.res_line["p_to_mw"]).sum()
    q_loss = (net.res_line["q_from_mvar"] + net.res_line["q_to_mvar"]).sum()

    return {
        "p_loss_mw": float(p_loss),
        "q_loss_mvar": float(q_loss)
    }


def run_powerflow(net: pp.pandapowerNet) -> Dict[str, Any]:
    """
    执行潮流并提取关键结果。
    """
    try:
        pp.runpp(net, algorithm="nr", init="auto", calculate_voltage_angles=True)

        result = {
            "success": True,
            "bus_voltage": extract_bus_results(net),
            "line_flow": extract_line_results(net),
            "system_loss": calc_system_loss(net)
        }
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "bus_voltage": pd.DataFrame(),
            "line_flow": pd.DataFrame(),
            "system_loss": {"p_loss_mw": None, "q_loss_mvar": None}
        }


def calc_delta_bus(base_bus_df: pd.DataFrame, new_bus_df: pd.DataFrame) -> pd.DataFrame:
    merged = base_bus_df.merge(
        new_bus_df,
        on=["pp_bus", "mp_bus"],
        suffixes=("_base", "_new")
    )
    merged["delta_vm_pu"] = merged["vm_pu_new"] - merged["vm_pu_base"]
    merged["delta_va_degree"] = merged["va_degree_new"] - merged["va_degree_base"]
    return merged[[
        "pp_bus", "mp_bus",
        "vm_pu_base", "vm_pu_new", "delta_vm_pu",
        "va_degree_base", "va_degree_new", "delta_va_degree"
    ]]


def calc_delta_line(base_line_df: pd.DataFrame, new_line_df: pd.DataFrame) -> pd.DataFrame:
    merged = base_line_df.merge(
        new_line_df,
        on=["line_id", "from_pp_bus", "to_pp_bus"],
        suffixes=("_base", "_new")
    )
    merged["delta_p_from_mw"] = merged["p_from_mw_new"] - merged["p_from_mw_base"]
    merged["delta_q_from_mvar"] = merged["q_from_mvar_new"] - merged["q_from_mvar_base"]
    merged["delta_p_to_mw"] = merged["p_to_mw_new"] - merged["p_to_mw_base"]
    merged["delta_q_to_mvar"] = merged["q_to_mvar_new"] - merged["q_to_mvar_base"]
    merged["delta_loading_percent"] = merged["loading_percent_new"] - merged["loading_percent_base"]

    return merged


def calc_delta_loss(base_loss: Dict[str, float], new_loss: Dict[str, float]) -> Dict[str, float]:
    return {
        "p_loss_mw_base": base_loss["p_loss_mw"],
        "p_loss_mw_new": new_loss["p_loss_mw"],
        "delta_p_loss_mw": new_loss["p_loss_mw"] - base_loss["p_loss_mw"],
        "q_loss_mvar_base": base_loss["q_loss_mvar"],
        "q_loss_mvar_new": new_loss["q_loss_mvar"],
        "delta_q_loss_mvar": new_loss["q_loss_mvar"] - base_loss["q_loss_mvar"],
    }