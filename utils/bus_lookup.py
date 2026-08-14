from __future__ import annotations

from typing import Dict
import pandas as pd


def build_bus_lookup(meta: Dict, data: Dict) -> pd.DataFrame:
    """构建外部节点编号与 pandapower 内部索引对应表。"""
    rows = []
    reverse_map = {v: k for k, v in meta.get("bus_map", {}).items()}
    bus_df = data.get("bus", pd.DataFrame()).copy()

    for pp_idx, ext_id in reverse_map.items():
        row = {
            "bus_pp_idx": pp_idx,
            "bus_id": ext_id,
            "name": "",
            "vn_kv": None,
        }
        match = bus_df[bus_df["bus_id"].astype(str) == str(ext_id)]
        if not match.empty:
            row["name"] = match.iloc[0].get("name", "")
            row["vn_kv"] = match.iloc[0].get("vn_kv", None)
        rows.append(row)

    return pd.DataFrame(rows).sort_values("bus_pp_idx").reset_index(drop=True)
