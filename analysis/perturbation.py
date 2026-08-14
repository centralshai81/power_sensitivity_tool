from __future__ import annotations

from typing import Any, Dict
import copy
import pandas as pd

from analysis.power_flow import run_base_powerflow


def _read_config_table(config_df: pd.DataFrame) -> Dict[str, str]:
    if config_df is None or config_df.empty or "param" not in config_df.columns:
        return {}
    return {str(k): str(v) for k, v in zip(config_df["param"], config_df["value"])}


def run_perturbation_analysis(net: Any, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    最小扰动分析：
    - 以负荷节点为对象
    - 分别对有功和无功增加小扰动
    - 记录各节点电压变化
    """
    config = _read_config_table(data.get("config", pd.DataFrame()))
    delta_p = float(config.get("delta_p_mw", 0.01))
    delta_q = float(config.get("delta_q_mvar", 0.01))

    base_net = copy.deepcopy(net)
    run_base_powerflow(base_net, config)
    base_vm = base_net.res_bus["vm_pu"].copy()

    load_table = net.load.copy()
    if load_table.empty:
        return {
            "base_bus_voltage": base_vm.reset_index().rename(columns={"index": "bus_pp_idx", "vm_pu": "base_vm_pu"}),
            "active_perturbation_summary": pd.DataFrame(),
            "reactive_perturbation_summary": pd.DataFrame(),
        }

    active_rows = []
    reactive_rows = []

    for load_idx in load_table.index:
        bus_idx = int(load_table.loc[load_idx, "bus"])

        test_net_p = copy.deepcopy(net)
        test_net_p.load.at[load_idx, "p_mw"] = float(test_net_p.load.at[load_idx, "p_mw"]) + delta_p
        run_base_powerflow(test_net_p, config)
        diff_p = test_net_p.res_bus["vm_pu"] - base_vm
        active_rows.append({
            "load_pp_idx": load_idx,
            "bus_pp_idx": bus_idx,
            "delta_p_mw": delta_p,
            "max_abs_dv_pu": float(diff_p.abs().max()),
            "self_bus_dv_pu": float(diff_p.loc[bus_idx]),
        })

        test_net_q = copy.deepcopy(net)
        test_net_q.load.at[load_idx, "q_mvar"] = float(test_net_q.load.at[load_idx, "q_mvar"]) + delta_q
        run_base_powerflow(test_net_q, config)
        diff_q = test_net_q.res_bus["vm_pu"] - base_vm
        reactive_rows.append({
            "load_pp_idx": load_idx,
            "bus_pp_idx": bus_idx,
            "delta_q_mvar": delta_q,
            "max_abs_dv_pu": float(diff_q.abs().max()),
            "self_bus_dv_pu": float(diff_q.loc[bus_idx]),
        })

    return {
        "base_bus_voltage": base_vm.reset_index().rename(columns={"index": "bus_pp_idx", "vm_pu": "base_vm_pu"}),
        "active_perturbation_summary": pd.DataFrame(active_rows),
        "reactive_perturbation_summary": pd.DataFrame(reactive_rows),
    }
