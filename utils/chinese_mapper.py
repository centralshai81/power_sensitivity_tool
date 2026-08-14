from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import pandas as pd

COLUMN_MAP = {
    "scenario_id": "场景编号",
    "success": "是否成功",
    "network_type": "网络类型",
    "node_type": "节点类型",
    "target_bus": "目标节点",
    "disturbance_type": "扰动类型",
    "disturbance_value": "扰动值",
    "max_abs_delta_vm_pu": "最大电压偏移绝对值(pu)",
    "affected_bus_count": "受影响节点数",
    "max_abs_delta_p_from_mw": "最大线路有功变化(MW)",
    "max_abs_delta_q_from_mvar": "最大线路无功变化(Mvar)",
    "delta_p_loss_mw": "有功网损变化(MW)",
    "delta_q_loss_mvar": "无功网损变化(Mvar)",
    "pp_bus": "内部节点号",
    "mp_bus": "外部节点号",
    "vm_pu": "电压幅值(pu)",
    "va_degree": "电压相角(度)",
    "line_id": "线路编号",
    "from_pp_bus": "起始内部节点",
    "to_pp_bus": "终止内部节点",
    "p_from_mw": "首端有功(MW)",
    "q_from_mvar": "首端无功(Mvar)",
    "p_to_mw": "末端有功(MW)",
    "q_to_mvar": "末端无功(Mvar)",
    "loading_percent": "负载率(%)",
    "delta_vm_pu": "电压变化量(pu)",
    "delta_va_degree": "相角变化(度)",
    "delta_p_from_mw": "首端有功变化(MW)",
    "delta_q_from_mvar": "首端无功变化(Mvar)",
    "delta_p_to_mw": "末端有功变化(MW)",
    "delta_q_to_mvar": "末端无功变化(Mvar)",
    "delta_loading_percent": "负载率变化(%)",
    "sensitivity_vv": "VV灵敏度",
    "sensitivity_qv": "QV灵敏度",
    "sens_pflow": "有功潮流灵敏度",
    "sens_qflow": "无功潮流灵敏度",
    "input_change": "输入扰动量",
    "group_name": "分组名称",
    "scenario_count": "场景数",
    "mean_max_abs_delta_vm_pu": "平均最大电压偏移(pu)",
    "max_max_abs_delta_vm_pu": "最大电压偏移峰值(pu)",
    "mean_affected_bus_count": "平均受影响节点数",
    "max_affected_bus_count": "最大受影响节点数",
    "mean_delta_p_loss_mw": "平均有功网损变化(MW)",
    "mean_delta_q_loss_mvar": "平均无功网损变化(Mvar)",
    "obs_bus": "观测节点",
    "mean_abs_sensitivity": "平均绝对灵敏度",
    "max_abs_sensitivity": "最大绝对灵敏度",
    "std_sensitivity": "灵敏度标准差",
    "mean_abs_p_sens": "平均绝对有功灵敏度",
    "max_abs_p_sens": "最大绝对有功灵敏度",
    "mean_abs_q_sens": "平均绝对无功灵敏度",
    "max_abs_q_sens": "最大绝对无功灵敏度",
    "combined_score": "综合评分",
    "figure_id": "图编号",
    "file": "文件路径",
    "description": "说明",
}

VALUE_MAP = {
    "base": "基础网络",
    "pv_extended": "PV扩展网络",
    "PQ": "PQ节点",
    "PV": "PV节点",
    "voltage_sag": "电压暂降",
    "reactive_variation": "无功扰动",
}


def translate_dataframe(df: pd.DataFrame, translate_values: bool = True) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()

    out = df.copy()
    out = out.rename(columns={c: COLUMN_MAP.get(c, c) for c in out.columns})

    if translate_values:
        for col in out.columns:
            if out[col].dtype == object:
                out[col] = out[col].map(lambda x: VALUE_MAP.get(x, x))
    return out


def save_dataframe_chinese(df: pd.DataFrame, path, translate_values: bool = True) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    translate_dataframe(df, translate_values=translate_values).to_csv(p, index=False, encoding="utf-8-sig")


def save_json_chinese(obj: Any, path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
