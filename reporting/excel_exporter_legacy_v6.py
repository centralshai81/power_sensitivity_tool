from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import pandas as pd
import openpyxl

from utils.legacy_output_formatter import (
    format_base_bus_voltage,
    format_base_line_flow,
    format_system_loss,
    format_summary_df,
    format_bus_matrix,
    format_flow_matrix,
    format_impact_summary,
    format_group_statistics,
    format_bus_rank,
    format_line_rank,
)

OLD_SHEET_ORDER = [
    "基准节点电压",
    "基准线路潮流",
    "基准系统损耗",
    "PV基准节点电压",
    "PV基准线路潮流",
    "PV基准系统损耗",
    "全部场景汇总",
    "电压-电压灵敏度矩阵",
    "无功-电压灵敏度矩阵",
    "潮流灵敏度矩阵",
    "影响指标汇总",
    "分组统计",
    "PQ_voltage_sag_节点排名",
    "PQ_reactive_variation_节点排名",
    "PV_voltage_sag_节点排名",
    "PV_reactive_variation_节点排名",
    "PQ_voltage_sag_线路排名",
    "PQ_reactive_variation_线路排名",
    "PV_voltage_sag_线路排名",
    "PV_reactive_variation_线路排名",
    "全局电压-电压节点排名",
    "全局无功-电压节点排名",
    "全局线路排名",
]

def _safe_sheet_name(name: str, max_len: int = 31) -> str:
    invalid = ['\\', '/', '*', '?', ':', '[', ']']
    for ch in invalid:
        name = name.replace(ch, "_")
    return name[:max_len]

def export_all_results_to_excel_legacy(
    output_path: str | Path,
    base_result: Dict[str, Any],
    pv_base_result: Dict[str, Any],
    summary_df: pd.DataFrame,
    sensitivity_results: Dict[str, pd.DataFrame],
    impact_results: Dict[str, Any],
    group_tables: Dict[str, Any],
    overall_tables: Dict[str, pd.DataFrame]
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        format_base_bus_voltage(base_result["bus_voltage"]).to_excel(writer, sheet_name="基准节点电压", index=False)
        format_base_line_flow(base_result["line_flow"]).to_excel(writer, sheet_name="基准线路潮流", index=False)
        format_system_loss(base_result["system_loss"]).to_excel(writer, sheet_name="基准系统损耗", index=False)

        format_base_bus_voltage(pv_base_result["bus_voltage"]).to_excel(writer, sheet_name="PV基准节点电压", index=False)
        format_base_line_flow(pv_base_result["line_flow"]).to_excel(writer, sheet_name="PV基准线路潮流", index=False)
        format_system_loss(pv_base_result["system_loss"]).to_excel(writer, sheet_name="PV基准系统损耗", index=False)

        format_summary_df(summary_df).to_excel(writer, sheet_name="全部场景汇总", index=False)
        format_bus_matrix(sensitivity_results["vv_matrix"]).to_excel(writer, sheet_name="电压-电压灵敏度矩阵", index=False)
        format_bus_matrix(sensitivity_results["qv_matrix"]).to_excel(writer, sheet_name="无功-电压灵敏度矩阵", index=False)
        format_flow_matrix(sensitivity_results["flow_matrix"]).to_excel(writer, sheet_name="潮流灵敏度矩阵", index=False)
        format_impact_summary(impact_results["impact_summary"]).to_excel(writer, sheet_name="影响指标汇总", index=False)

        format_group_statistics(group_tables.get("group_statistics", pd.DataFrame())).to_excel(writer, sheet_name="分组统计", index=False)

        for group_name, df in group_tables.get("group_bus_rank_tables", {}).items():
            format_bus_rank(df).to_excel(writer, sheet_name=_safe_sheet_name(f"{group_name}_节点排名"), index=False)

        for group_name, df in group_tables.get("group_line_rank_tables", {}).items():
            format_line_rank(df).to_excel(writer, sheet_name=_safe_sheet_name(f"{group_name}_线路排名"), index=False)

        format_bus_rank(overall_tables["overall_vv_bus_rank"]).to_excel(writer, sheet_name="全局电压-电压节点排名", index=False)
        format_bus_rank(overall_tables["overall_qv_bus_rank"]).to_excel(writer, sheet_name="全局无功-电压节点排名", index=False)
        format_line_rank(overall_tables["overall_line_rank"]).to_excel(writer, sheet_name="全局线路排名", index=False)

    wb = openpyxl.load_workbook(output_path)
    name_to_sheet = {ws.title: ws for ws in wb.worksheets}
    ordered = [name_to_sheet[name] for name in OLD_SHEET_ORDER if name in name_to_sheet]
    wb._sheets = ordered
    wb.save(output_path)
