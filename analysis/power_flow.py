from __future__ import annotations

from typing import Any, Dict

try:
    import pandapower as pp
except ImportError as exc:
    raise ImportError("未检测到 pandapower。请先安装：pip install pandapower") from exc


def run_base_powerflow(net: Any, config: Dict | None = None) -> Any:
    """执行基础潮流计算。"""
    config = config or {}
    algorithm = config.get("pf_algorithm", "nr")

    pp.runpp(
        net,
        algorithm=algorithm,
        calculate_voltage_angles=False,
        init="auto",
    )
    return net
