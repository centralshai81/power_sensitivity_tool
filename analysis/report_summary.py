# analysis/report_summary.py

from __future__ import annotations

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np


def filter_summary_by_group(
    summary_df: pd.DataFrame,
    node_type: str | None = None,
    disturbance_type: str | None = None,
    network_type: str | None = None
) -> pd.DataFrame:
    """
    对场景汇总表按组筛选。
    """
    df = summary_df.copy()

    if node_type is not None:
        df = df[df["node_type"] == node_type]

    if disturbance_type is not None:
        df = df[df["disturbance_type"] == disturbance_type]

    if network_type is not None:
        df = df[df["network_type"] == network_type]

    return df.reset_index(drop=True)


def filter_matrix_by_group(
    matrix_df: pd.DataFrame,
    node_type: str | None = None,
    disturbance_type: str | None = None,
    network_type: str | None = None
) -> pd.DataFrame:
    """
    对灵敏度矩阵表按组筛选。
    """
    if matrix_df.empty:
        return matrix_df.copy()

    df = matrix_df.copy()

    if node_type is not None and "node_type" in df.columns:
        df = df[df["node_type"] == node_type]

    if disturbance_type is not None and "disturbance_type" in df.columns:
        df = df[df["disturbance_type"] == disturbance_type]

    if network_type is not None and "network_type" in df.columns:
        df = df[df["network_type"] == network_type]

    return df.reset_index(drop=True)


def summarize_group_statistics(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    对某一组场景进行统计汇总。
    """
    if summary_df.empty:
        return pd.DataFrame(columns=[
            "scenario_count",
            "mean_max_abs_delta_vm_pu",
            "max_max_abs_delta_vm_pu",
            "mean_affected_bus_count",
            "max_affected_bus_count",
            "mean_delta_p_loss_mw",
            "mean_delta_q_loss_mvar"
        ])

    row = {
        "scenario_count": int(len(summary_df)),
        "mean_max_abs_delta_vm_pu": float(summary_df["max_abs_delta_vm_pu"].dropna().mean()),
        "max_max_abs_delta_vm_pu": float(summary_df["max_abs_delta_vm_pu"].dropna().max()),
        "mean_affected_bus_count": float(summary_df["affected_bus_count"].dropna().mean()),
        "max_affected_bus_count": float(summary_df["affected_bus_count"].dropna().max()),
        "mean_delta_p_loss_mw": float(summary_df["delta_p_loss_mw"].dropna().mean()),
        "mean_delta_q_loss_mvar": float(summary_df["delta_q_loss_mvar"].dropna().mean())
    }
    return pd.DataFrame([row])


def aggregate_bus_sensitivity_importance(
    matrix_df: pd.DataFrame
) -> pd.DataFrame:
    """
    根据灵敏度矩阵统计各观测节点的总体敏感程度。
    对每个 bus_k 统计：
    - mean_abs_sensitivity
    - max_abs_sensitivity
    - std_sensitivity
    """
    if matrix_df.empty:
        return pd.DataFrame(columns=["obs_bus", "mean_abs_sensitivity", "max_abs_sensitivity", "std_sensitivity"])

    bus_cols = [c for c in matrix_df.columns if c.startswith("bus_")]
    rows = []

    for col in bus_cols:
        values = pd.to_numeric(matrix_df[col], errors="coerce").dropna()
        if len(values) == 0:
            continue

        obs_bus = int(col.replace("bus_", ""))
        rows.append({
            "obs_bus": obs_bus,
            "mean_abs_sensitivity": float(values.abs().mean()),
            "max_abs_sensitivity": float(values.abs().max()),
            "std_sensitivity": float(values.std(ddof=0))
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    return df.sort_values(["mean_abs_sensitivity", "max_abs_sensitivity"], ascending=False).reset_index(drop=True)


def aggregate_line_sensitivity_importance(
    flow_matrix_df: pd.DataFrame
) -> pd.DataFrame:
    """
    根据线路灵敏度矩阵统计各线路总体敏感程度。
    分别对 _p 和 _q 做聚合，再形成综合指标。
    """
    if flow_matrix_df.empty:
        return pd.DataFrame(columns=[
            "line_id",
            "mean_abs_p_sens",
            "max_abs_p_sens",
            "mean_abs_q_sens",
            "max_abs_q_sens",
            "combined_score"
        ])

    p_cols = [c for c in flow_matrix_df.columns if c.startswith("line_") and c.endswith("_p")]
    q_cols = [c for c in flow_matrix_df.columns if c.startswith("line_") and c.endswith("_q")]

    line_ids = sorted(set(
        int(c.split("_")[1]) for c in p_cols + q_cols
    ))

    rows = []
    for lid in line_ids:
        p_col = f"line_{lid}_p"
        q_col = f"line_{lid}_q"

        p_vals = pd.to_numeric(flow_matrix_df[p_col], errors="coerce").dropna() if p_col in flow_matrix_df.columns else pd.Series(dtype=float)
        q_vals = pd.to_numeric(flow_matrix_df[q_col], errors="coerce").dropna() if q_col in flow_matrix_df.columns else pd.Series(dtype=float)

        mean_abs_p = float(p_vals.abs().mean()) if len(p_vals) else 0.0
        max_abs_p = float(p_vals.abs().max()) if len(p_vals) else 0.0
        mean_abs_q = float(q_vals.abs().mean()) if len(q_vals) else 0.0
        max_abs_q = float(q_vals.abs().max()) if len(q_vals) else 0.0

        rows.append({
            "line_id": lid,
            "mean_abs_p_sens": mean_abs_p,
            "max_abs_p_sens": max_abs_p,
            "mean_abs_q_sens": mean_abs_q,
            "max_abs_q_sens": max_abs_q,
            "combined_score": mean_abs_p + mean_abs_q + 0.5 * max_abs_p + 0.5 * max_abs_q
        })

    df = pd.DataFrame(rows)
    return df.sort_values("combined_score", ascending=False).reset_index(drop=True)


def build_group_report_tables(
    summary_df: pd.DataFrame,
    sensitivity_results: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    构造论文风格的分组汇总表。
    """
    groups = [
        ("PQ_voltage_sag", {"node_type": "PQ", "disturbance_type": "voltage_sag", "network_type": "base"}),
        ("PQ_reactive_variation", {"node_type": "PQ", "disturbance_type": "reactive_variation", "network_type": "base"}),
        ("PV_voltage_sag", {"node_type": "PV", "disturbance_type": "voltage_sag", "network_type": "pv_extended"}),
        ("PV_reactive_variation", {"node_type": "PV", "disturbance_type": "reactive_variation", "network_type": "pv_extended"}),
    ]

    group_stats_rows = []
    group_bus_rank_tables = {}
    group_line_rank_tables = {}

    for group_name, cond in groups:
        sub_summary = filter_summary_by_group(summary_df, **cond)
        stat_df = summarize_group_statistics(sub_summary)

        if not stat_df.empty:
            stat_df.insert(0, "group_name", group_name)
            group_stats_rows.append(stat_df)

        if cond["disturbance_type"] == "voltage_sag":
            matrix_df = filter_matrix_by_group(sensitivity_results["vv_matrix"], **cond)
        else:
            matrix_df = filter_matrix_by_group(sensitivity_results["qv_matrix"], **cond)

        flow_df = filter_matrix_by_group(sensitivity_results["flow_matrix"], **cond)

        bus_rank_df = aggregate_bus_sensitivity_importance(matrix_df)
        line_rank_df = aggregate_line_sensitivity_importance(flow_df)

        group_bus_rank_tables[group_name] = bus_rank_df
        group_line_rank_tables[group_name] = line_rank_df

    group_stats_df = pd.concat(group_stats_rows, ignore_index=True) if group_stats_rows else pd.DataFrame()

    return {
        "group_statistics": group_stats_df,
        "group_bus_rank_tables": group_bus_rank_tables,
        "group_line_rank_tables": group_line_rank_tables
    }


def build_overall_top_tables(
    sensitivity_results: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    生成全局总排名表。
    """
    vv_rank = aggregate_bus_sensitivity_importance(sensitivity_results["vv_matrix"])
    qv_rank = aggregate_bus_sensitivity_importance(sensitivity_results["qv_matrix"])
    line_rank = aggregate_line_sensitivity_importance(sensitivity_results["flow_matrix"])

    return {
        "overall_vv_bus_rank": vv_rank,
        "overall_qv_bus_rank": qv_rank,
        "overall_line_rank": line_rank
    }


def generate_text_summary(
    summary_df: pd.DataFrame,
    group_tables: Dict[str, pd.DataFrame],
    overall_tables: Dict[str, pd.DataFrame]
) -> str:
    """
    自动生成简洁的文字结论摘要。
    """
    lines = []
    lines.append("IEEE33节点灵敏度分析结果摘要")
    lines.append("=" * 36)

    if not summary_df.empty:
        total_cases = len(summary_df)
        success_cases = int(summary_df["success"].fillna(False).sum()) if "success" in summary_df.columns else total_cases
        lines.append(f"1. 本次共完成 {total_cases} 个场景计算，其中成功场景 {success_cases} 个。")

        if "max_abs_delta_vm_pu" in summary_df.columns:
            max_row = summary_df.sort_values("max_abs_delta_vm_pu", ascending=False).iloc[0]
            lines.append(
                f"2. 最大节点电压变化出现在场景 {max_row['scenario_id']}，"
                f"其最大电压偏移为 {max_row['max_abs_delta_vm_pu']:.6f} p.u.。"
            )

    group_stats = group_tables.get("group_statistics", pd.DataFrame())
    if not group_stats.empty:
        lines.append("3. 分组统计结果如下：")
        GROUP_NAME_DISPLAY_MAP = {
            "PQ_voltage_sag": "PQ节点电压暂降",
            "PQ_reactive_variation": "PQ节点无功扰动",
            "PV_voltage_sag": "PV节点电压暂降",
            "PV_reactive_variation": "PV节点无功扰动",
        }
        for _, r in group_stats.iterrows():
            group_display = GROUP_NAME_DISPLAY_MAP.get(r['group_name'], r['group_name'])
            lines.append(
                f"   - {group_display}: 平均最大电压变化 {r['mean_max_abs_delta_vm_pu']:.6f} p.u.，"
                f"平均受影响节点数 {r['mean_affected_bus_count']:.2f} 个。"
            )

    vv_rank = overall_tables.get("overall_vv_bus_rank", pd.DataFrame())
    qv_rank = overall_tables.get("overall_qv_bus_rank", pd.DataFrame())
    line_rank = overall_tables.get("overall_line_rank", pd.DataFrame())

    if not vv_rank.empty:
        top_bus = vv_rank.iloc[0]
        lines.append(
            f"4. 从电压-电压灵敏度角度看，观测节点 {int(top_bus['obs_bus'])} 的平均绝对灵敏度最高，"
            f"均值为 {top_bus['mean_abs_sensitivity']:.6f}。"
        )

    if not qv_rank.empty:
        top_bus = qv_rank.iloc[0]
        lines.append(
            f"5. 从无功-电压灵敏度角度看，观测节点 {int(top_bus['obs_bus'])} 最敏感，"
            f"平均绝对灵敏度为 {top_bus['mean_abs_sensitivity']:.6f}。"
        )

    if not line_rank.empty:
        top_line = line_rank.iloc[0]
        lines.append(
            f"6. 从潮流灵敏度角度看，线路 {int(top_line['line_id'])} 的综合敏感度最高，"
            f"综合评分为 {top_line['combined_score']:.6f}。"
        )

    lines.append("7. 结果表明，不同位置节点对电压暂降与无功扰动的响应具有明显空间差异，末端薄弱节点与关键主干线路通常具有更高的敏感度。")

    return "\n".join(lines)