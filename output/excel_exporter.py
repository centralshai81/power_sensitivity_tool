from __future__ import annotations

from typing import Dict
import pandas as pd


def export_all_results(
    output_excel: str,
    perturb_result: Dict[str, pd.DataFrame],
    vv_matrix: pd.DataFrame,
    qv_matrix: pd.DataFrame,
    critical_nodes: pd.DataFrame,
    critical_lines: pd.DataFrame,
    bus_lookup: pd.DataFrame | None = None,
) -> None:
    """导出分析结果到 Excel。"""
    with pd.ExcelWriter(output_excel) as writer:
        if bus_lookup is not None and not bus_lookup.empty:
            bus_lookup.to_excel(writer, sheet_name="bus_lookup", index=False)

        if perturb_result:
            for key, df in perturb_result.items():
                if df is not None and not df.empty:
                    df.to_excel(writer, sheet_name=key[:31], index=False)

        if vv_matrix is not None and not vv_matrix.empty:
            vv_matrix.to_excel(writer, sheet_name="vv_matrix")

        if qv_matrix is not None and not qv_matrix.empty:
            qv_matrix.to_excel(writer, sheet_name="qv_matrix")

        if critical_nodes is not None and not critical_nodes.empty:
            critical_nodes.to_excel(writer, sheet_name="critical_nodes", index=False)

        if critical_lines is not None and not critical_lines.empty:
            critical_lines.to_excel(writer, sheet_name="critical_lines", index=False)
