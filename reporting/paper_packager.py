# reporting/paper_packager.py

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import shutil
import pandas as pd


def copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def package_paper_figures(output_dir: str | Path) -> pd.DataFrame:
    """
    从 results/figures 中整理出更适合论文插图的文件到 results/paper_figures。
    返回图表索引表。
    """
    output_dir = Path(output_dir)
    fig_dir = output_dir / "figures"
    paper_dir = output_dir / "paper_figures"
    paper_dir.mkdir(parents=True, exist_ok=True)

    records = []

    # 1. 全局热力图
    global_figure_items = [
        ("Fig1_vv_heatmap", fig_dir / "vv_sensitivity_heatmap.png", "全局电压-电压灵敏度热力图"),
        ("Fig2_qv_heatmap", fig_dir / "qv_sensitivity_heatmap.png", "全局无功-电压灵敏度热力图"),
    ]

    for fig_id, src, desc in global_figure_items:
        dst = paper_dir / f"{fig_id}.png"
        if copy_if_exists(src, dst):
            records.append({"figure_id": fig_id, "file": str(dst), "description": desc})

    # 2. 分组热力图
    group_heatmap_dir = fig_dir / "group_heatmaps"
    group_figure_items = [
        ("Fig3_PQ_voltage_sag_heatmap", group_heatmap_dir / "PQ_voltage_sag_heatmap.png", "PQ节点电压暂降灵敏度热力图"),
        ("Fig4_PQ_reactive_variation_heatmap", group_heatmap_dir / "PQ_reactive_variation_heatmap.png", "PQ节点无功扰动灵敏度热力图"),
        ("Fig5_PV_voltage_sag_heatmap", group_heatmap_dir / "PV_voltage_sag_heatmap.png", "PV节点电压设定值扰动灵敏度热力图"),
        ("Fig6_PV_reactive_variation_heatmap", group_heatmap_dir / "PV_reactive_variation_heatmap.png", "PV节点无功扰动灵敏度热力图"),
    ]

    for fig_id, src, desc in group_figure_items:
        dst = paper_dir / f"{fig_id}.png"
        if copy_if_exists(src, dst):
            records.append({"figure_id": fig_id, "file": str(dst), "description": desc})

    # 3. 报告层图
    report_fig_dir = fig_dir / "report_summary"
    report_figure_items = [
        ("Fig7_group_mean_max_delta_v", report_fig_dir / "group_mean_max_delta_v.png", "各场景组平均最大电压偏移对比"),
        ("Fig8_group_mean_affected_bus_count", report_fig_dir / "group_mean_affected_bus_count.png", "各场景组平均受影响节点数对比"),
        ("Fig9_group_dual_metric", report_fig_dir / "group_dual_metric.png", "各场景组电压影响与受影响节点双指标图"),
        ("Fig10_overall_vv_bus_rank", report_fig_dir / "overall_vv_bus_rank.png", "全局电压-电压灵敏度节点排名"),
        ("Fig11_overall_qv_bus_rank", report_fig_dir / "overall_qv_bus_rank.png", "全局无功-电压灵敏度节点排名"),
        ("Fig12_overall_line_rank", report_fig_dir / "overall_line_rank.png", "全局关键线路排名"),
    ]

    for fig_id, src, desc in report_figure_items:
        dst = paper_dir / f"{fig_id}.png"
        if copy_if_exists(src, dst):
            records.append({"figure_id": fig_id, "file": str(dst), "description": desc})

    index_df = pd.DataFrame(records)
    if not index_df.empty:
        index_df.to_csv(paper_dir / "论文图表索引.csv", index=False, encoding="utf-8-sig")

    return index_df
