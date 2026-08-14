from __future__ import annotations

import pandas as pd


def identify_critical_nodes(vv_matrix: pd.DataFrame, qv_matrix: pd.DataFrame) -> pd.DataFrame:
    """关键节点识别：按 VV/QV 行绝对值求和形成综合得分。"""
    vv_score = vv_matrix.abs().sum(axis=1) if vv_matrix is not None and not vv_matrix.empty else pd.Series(dtype=float)
    qv_score = qv_matrix.abs().sum(axis=1) if qv_matrix is not None and not qv_matrix.empty else pd.Series(dtype=float)

    idx = sorted(set(vv_score.index.tolist()) | set(qv_score.index.tolist()))
    result = pd.DataFrame(index=idx)
    result.index.name = "bus_pp_idx"
    result["vv_score"] = vv_score.reindex(idx).fillna(0.0)
    result["qv_score"] = qv_score.reindex(idx).fillna(0.0)
    result["total_score"] = result["vv_score"] + result["qv_score"]
    result = result.sort_values("total_score", ascending=False).reset_index()
    result["rank"] = range(1, len(result) + 1)
    return result[["rank", "bus_pp_idx", "vv_score", "qv_score", "total_score"]]
