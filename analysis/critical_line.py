from __future__ import annotations

from typing import Any
import pandas as pd


def identify_critical_lines(net: Any, vv_matrix: pd.DataFrame, qv_matrix: pd.DataFrame) -> pd.DataFrame:
    """关键线路识别：利用线路两端节点综合得分均值构建线路敏感度评分。"""
    if net.line.empty:
        return pd.DataFrame()

    vv_score = vv_matrix.abs().sum(axis=1) if vv_matrix is not None and not vv_matrix.empty else pd.Series(dtype=float)
    qv_score = qv_matrix.abs().sum(axis=1) if qv_matrix is not None and not qv_matrix.empty else pd.Series(dtype=float)
    node_score = vv_score.reindex(net.bus.index).fillna(0.0) + qv_score.reindex(net.bus.index).fillna(0.0)

    rows = []
    for line_idx, row in net.line.iterrows():
        from_bus = int(row["from_bus"])
        to_bus = int(row["to_bus"])
        score = (float(node_score.loc[from_bus]) + float(node_score.loc[to_bus])) / 2.0
        rows.append({
            "line_pp_idx": line_idx,
            "from_bus_pp_idx": from_bus,
            "to_bus_pp_idx": to_bus,
            "line_score": score,
        })

    result = pd.DataFrame(rows).sort_values("line_score", ascending=False).reset_index(drop=True)
    result["rank"] = range(1, len(result) + 1)
    return result[["rank", "line_pp_idx", "from_bus_pp_idx", "to_bus_pp_idx", "line_score"]]
