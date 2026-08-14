# reporting/excel_exporter.py

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import pandas as pd

from utils.chinese_mapper import translate_dataframe


def _safe_sheet_name(name: str, max_len: int = 31) -> str:
    invalid = ['\\', '/', '*', '?', ':', '[', ']']
    for ch in invalid:
        name = name.replace(ch, "_")
    return name[:max_len]


def _translate_and_write(df: pd.DataFrame, writer: pd.ExcelWriter, sheet_name: str, translate_values: bool = True) -> None:
    translated_df = translate_dataframe(df, translate_values=translate_values)
    translated_df.to_excel(writer, sheet_name=_safe_sheet_name(sheet_name), index=False)


def export_all_results_to_excel(
    output_path: str | Path,
    base_result: Dict[str, Any],
    pv_base_result: Dict[str, Any],
    summary_df: pd.DataFrame,
    sensitivity_results: Dict[str, pd.DataFrame],
    impact_results: Dict[str, Any],
    group_tables: Dict[str, Any],
    overall_tables: Dict[str, pd.DataFrame]
) -> None:
    """
    将核心结果导出到一个 Excel 工作簿。
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        _translate_and_write(base_result["bus_voltage"], writer, "基准节点电压", translate_values=False)
        _translate_and_write(base_result["line_flow"], writer, "基准线路潮流", translate_values=False)
        _translate_and_write(pd.DataFrame([base_result["system_loss"]]), writer, "基准系统损耗", translate_values=False)

        _translate_and_write(pv_base_result["bus_voltage"], writer, "PV基准节点电压", translate_values=False)
        _translate_and_write(pv_base_result["line_flow"], writer, "PV基准线路潮流", translate_values=False)
        _translate_and_write(pd.DataFrame([pv_base_result["system_loss"]]), writer, "PV基准系统损耗", translate_values=False)

        _translate_and_write(summary_df, writer, "全部场景汇总", translate_values=True)

        _translate_and_write(sensitivity_results["vv_matrix"], writer, "电压-电压灵敏度矩阵", translate_values=True)
        _translate_and_write(sensitivity_results["qv_matrix"], writer, "无功-电压灵敏度矩阵", translate_values=True)
        _translate_and_write(sensitivity_results["flow_matrix"], writer, "潮流灵敏度矩阵", translate_values=True)

        _translate_and_write(impact_results["impact_summary"], writer, "影响指标汇总", translate_values=True)

        group_stats = group_tables.get("group_statistics", pd.DataFrame())
        _translate_and_write(group_stats, writer, "分组统计", translate_values=True)

        for group_name, df in group_tables.get("group_bus_rank_tables", {}).items():
            _translate_and_write(df, writer, f"{group_name}_节点排名", translate_values=True)

        for group_name, df in group_tables.get("group_line_rank_tables", {}).items():
            _translate_and_write(df, writer, f"{group_name}_线路排名", translate_values=True)

        _translate_and_write(overall_tables["overall_vv_bus_rank"], writer, "全局电压-电压节点排名", translate_values=True)
        _translate_and_write(overall_tables["overall_qv_bus_rank"], writer, "全局无功-电压节点排名", translate_values=True)
        _translate_and_write(overall_tables["overall_line_rank"], writer, "全局线路排名", translate_values=True)
