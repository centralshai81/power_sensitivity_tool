from __future__ import annotations

from typing import Any, Dict
import copy
import pandas as pd

from analysis.power_flow import run_base_powerflow


def _read_config_table(config_df: pd.DataFrame) -> Dict[str, str]:
    if config_df is None or config_df.empty or "param" not in config_df.columns:
        return {}
    return {str(k): str(v) for k, v in zip(config_df["param"], config_df["value"])}


def calc_qv_sensitivity(net: Any, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    QV 灵敏度矩阵（有限差分）：
    矩阵元素：dV_i / dQ_j  (pu / Mvar)
    行：响应节点
    列：扰动负荷所在节点
    """
    config = _read_config_table(data.get("config", pd.DataFrame()))
    delta_q = float(config.get("delta_q_mvar", 0.01))

    base_net = copy.deepcopy(net)
    run_base_powerflow(base_net, config)
    base_vm = base_net.res_bus["vm_pu"].copy()

    if net.load.empty:
        return pd.DataFrame()

    matrix = pd.DataFrame(index=base_net.bus.index)

    for load_idx in net.load.index:
        test_net = copy.deepcopy(net)
        test_net.load.at[load_idx, "q_mvar"] = float(test_net.load.at[load_idx, "q_mvar"]) + delta_q
        run_base_powerflow(test_net, config)
        dv = (test_net.res_bus["vm_pu"] - base_vm) / delta_q
        load_bus = int(net.load.loc[load_idx, "bus"])
        matrix[f"load_bus_{load_bus}"] = dv.values

    matrix.index.name = "bus_pp_idx"
    return matrix
