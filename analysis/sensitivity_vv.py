from __future__ import annotations

from typing import Any, Dict
import copy
import pandas as pd

from analysis.power_flow import run_base_powerflow


def _read_config_table(config_df: pd.DataFrame) -> Dict[str, str]:
    if config_df is None or config_df.empty or "param" not in config_df.columns:
        return {}
    return {str(k): str(v) for k, v in zip(config_df["param"], config_df["value"])}


def calc_vv_sensitivity(net: Any, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    工程可运行版 VV 近似矩阵：
    当前版本采用 dV_i / dP_j (pu / MW) 近似表征节点间电压耦合。

    说明：
    - 这是第二批用于跑通主链的近似实现；
    - 你后续可直接用已有研究版 VV 算法替换本文件。
    """
    config = _read_config_table(data.get("config", pd.DataFrame()))
    delta_p = float(config.get("delta_p_mw", 0.01))

    base_net = copy.deepcopy(net)
    run_base_powerflow(base_net, config)
    base_vm = base_net.res_bus["vm_pu"].copy()

    if net.load.empty:
        return pd.DataFrame()

    matrix = pd.DataFrame(index=base_net.bus.index)

    for load_idx in net.load.index:
        test_net = copy.deepcopy(net)
        test_net.load.at[load_idx, "p_mw"] = float(test_net.load.at[load_idx, "p_mw"]) + delta_p
        run_base_powerflow(test_net, config)
        dv = (test_net.res_bus["vm_pu"] - base_vm) / delta_p
        load_bus = int(net.load.loc[load_idx, "bus"])
        matrix[f"load_bus_{load_bus}"] = dv.values

    matrix.index.name = "bus_pp_idx"
    return matrix
