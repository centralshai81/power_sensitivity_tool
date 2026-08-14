from __future__ import annotations

from typing import Dict, Any
import pandas as pd


def _rename_if_exists(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()
    out = df.copy()
    valid = {k: v for k, v in rename_map.items() if k in out.columns}
    return out.rename(columns=valid)


def _reindex_columns(df: pd.DataFrame, ordered_cols: list[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()
    cols = [c for c in ordered_cols if c in df.columns] + [c for c in df.columns if c not in ordered_cols]
    return df[cols]


def format_base_bus_voltage(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "pp_bus": "Pandapower节点编号",
        "mp_bus": "MATPOWER节点编号",
        "vm_pu": "电压幅值(p.u.)",
        "va_degree": "电压相角(度)",
    })
    return _reindex_columns(out, ["Pandapower节点编号", "MATPOWER节点编号", "电压幅值(p.u.)", "电压相角(度)"])


def format_base_line_flow(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "line_id": "线路编号",
        "from_pp_bus": "起始Pandapower节点",
        "to_pp_bus": "终止Pandapower节点",
        "p_from_mw": "首端有功(MW)",
        "q_from_mvar": "首端无功(Mvar)",
        "p_to_mw": "末端有功(MW)",
        "q_to_mvar": "末端无功(Mvar)",
        "loading_percent": "负载率(%)",
    })
    return _reindex_columns(
        out,
        ["线路编号", "起始Pandapower节点", "终止Pandapower节点", "首端有功(MW)", "首端无功(Mvar)", "末端有功(MW)", "末端无功(Mvar)", "负载率(%)"]
    )


def format_system_loss(loss_obj: Dict[str, Any] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(loss_obj, pd.DataFrame):
        df = loss_obj.copy()
    else:
        df = pd.DataFrame([loss_obj])
    out = _rename_if_exists(df, {
        "p_loss_mw": "有功损耗(MW)",
        "q_loss_mvar": "无功损耗(Mvar)",
    })
    return _reindex_columns(out, ["有功损耗(MW)", "无功损耗(Mvar)"])


def format_summary_df(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "scenario_id": "场景编号",
        "success": "计算成功",
        "network_type": "网络类型",
        "node_type": "节点类型",
        "target_bus": "目标节点",
        "disturbance_type": "扰动类型",
        "disturbance_value": "扰动值",
        "max_abs_delta_vm_pu": "最大电压偏移(p.u.)",
        "affected_bus_count": "受影响节点数",
        "max_abs_delta_p_from_mw": "最大有功变化(MW)",
        "max_abs_delta_q_from_mvar": "最大无功变化(Mvar)",
        "delta_p_loss_mw": "有功损耗变化(MW)",
        "delta_q_loss_mvar": "无功损耗变化(Mvar)",
        "error": "错误信息",
    })
    return _reindex_columns(
        out,
        ["场景编号", "计算成功", "网络类型", "节点类型", "目标节点", "扰动类型", "扰动值",
         "最大电压偏移(p.u.)", "受影响节点数", "最大有功变化(MW)", "最大无功变化(Mvar)",
         "有功损耗变化(MW)", "无功损耗变化(Mvar)", "错误信息"]
    )


def format_impact_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "scenario_id": "场景编号",
        "success": "计算成功",
        "network_type": "网络类型",
        "node_type": "节点类型",
        "target_bus": "目标节点",
        "disturbance_type": "扰动类型",
        "disturbance_value": "扰动值",
        "affected_bus_count": "受影响节点数",
        "max_abs_delta_v": "最大电压偏移(p.u.)",
        "mean_abs_delta_v": "平均电压偏移(p.u.)",
    })
    return _reindex_columns(
        out,
        ["场景编号", "计算成功", "网络类型", "节点类型", "目标节点", "扰动类型", "扰动值",
         "受影响节点数", "最大电压偏移(p.u.)", "平均电压偏移(p.u.)"]
    )


def _convert_bus_cols_to_legacy(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df.copy()
    return df.copy()


def format_bus_matrix(df: pd.DataFrame) -> pd.DataFrame:
    out = _convert_bus_cols_to_legacy(df)
    out = _rename_if_exists(out, {
        "scenario_id": "场景编号",
        "network_type": "网络类型",
        "node_type": "节点类型",
        "target_bus": "目标节点",
        "disturbance_type": "扰动类型",
        "disturbance_value": "扰动值",
    })
    fixed = ["场景编号", "网络类型", "节点类型", "目标节点", "扰动类型", "扰动值"]
    bus_cols = sorted([c for c in out.columns if str(c).startswith("bus_")], key=lambda x: int(str(x).split("_")[1]))
    return out[fixed + bus_cols] if all(c in out.columns for c in fixed) else _reindex_columns(out, fixed + bus_cols)


def format_flow_matrix(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "scenario_id": "场景编号",
        "network_type": "网络类型",
        "node_type": "节点类型",
        "target_bus": "目标节点",
        "disturbance_type": "扰动类型",
        "disturbance_value": "扰动值",
    })
    fixed = ["场景编号", "网络类型", "节点类型", "目标节点", "扰动类型", "扰动值"]
    line_cols = [c for c in out.columns if str(c).startswith("line_")]
    def sort_key(x: str):
        try:
            parts = x.split("_")
            return (int(parts[1]), parts[2] if len(parts) > 2 else "")
        except Exception:
            return (10**9, x)
    line_cols = sorted(line_cols, key=sort_key)
    return out[fixed + line_cols] if all(c in out.columns for c in fixed) else _reindex_columns(out, fixed + line_cols)


def format_group_statistics(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "group_name": "分组名称",
        "scenario_count": "场景数量",
        "mean_max_abs_delta_vm_pu": "平均最大电压偏移(p.u.)",
        "max_max_abs_delta_vm_pu": "最大电压偏移峰值(p.u.)",
        "mean_affected_bus_count": "平均受影响节点数",
        "max_affected_bus_count": "最大受影响节点数",
        "mean_delta_p_loss_mw": "平均有功损耗变化(MW)",
        "mean_delta_q_loss_mvar": "平均无功损耗变化(Mvar)",
    })
    return _reindex_columns(
        out,
        ["分组名称", "场景数量", "平均最大电压偏移(p.u.)", "最大电压偏移峰值(p.u.)",
         "平均受影响节点数", "最大受影响节点数", "平均有功损耗变化(MW)", "平均无功损耗变化(Mvar)"]
    )


def format_bus_rank(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "obs_bus": "观测节点",
        "mean_abs_sensitivity": "平均绝对灵敏度",
        "max_abs_sensitivity": "最大绝对灵敏度",
        "std_sensitivity": "灵敏度标准差",
    })
    return _reindex_columns(out, ["观测节点", "平均绝对灵敏度", "最大绝对灵敏度", "灵敏度标准差"])


def format_line_rank(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_if_exists(df, {
        "line_id": "线路编号",
        "mean_abs_p_sens": "平均绝对有功灵敏度",
        "max_abs_p_sens": "最大绝对有功灵敏度",
        "mean_abs_q_sens": "平均绝对无功灵敏度",
        "max_abs_q_sens": "最大绝对无功灵敏度",
        "combined_score": "综合评分",
    })
    return _reindex_columns(
        out,
        ["线路编号", "平均绝对有功灵敏度", "最大绝对有功灵敏度", "平均绝对无功灵敏度", "最大绝对无功灵敏度", "综合评分"]
    )
