# analysis/topology_analysis.py

from __future__ import annotations

from typing import Dict, Any
import networkx as nx
import pandas as pd
import numpy as np


def build_graph_from_net(net) -> nx.Graph:
    """
    将 pandapower 网络转为 networkx 图。
    节点使用 mp_bus 作为标签。
    """
    g = nx.Graph()

    bus_lookup = {}
    for pp_bus, row in net.bus.iterrows():
        mp_bus = int(row["mp_bus"]) if "mp_bus" in net.bus.columns else int(pp_bus + 1)
        bus_lookup[int(pp_bus)] = mp_bus
        g.add_node(mp_bus)

    for line_id, row in net.line.iterrows():
        from_pp = int(row["from_bus"])
        to_pp = int(row["to_bus"])
        from_mp = bus_lookup[from_pp]
        to_mp = bus_lookup[to_pp]

        r_ohm = float(row["r_ohm_per_km"] * row["length_km"])
        x_ohm = float(row["x_ohm_per_km"] * row["length_km"])
        z_mag = float(np.sqrt(r_ohm ** 2 + x_ohm ** 2))

        g.add_edge(
            from_mp,
            to_mp,
            line_id=int(line_id),
            r_ohm=r_ohm,
            x_ohm=x_ohm,
            z_ohm=z_mag
        )

    return g


def calc_topological_distance(graph: nx.Graph, source_bus: int) -> pd.DataFrame:
    """
    计算从 source_bus 到各节点的拓扑距离（边数）。
    """
    distances = nx.single_source_shortest_path_length(graph, source_bus)

    rows = [{"mp_bus": int(bus), "topo_distance": int(dist)} for bus, dist in distances.items()]
    return pd.DataFrame(rows).sort_values("mp_bus").reset_index(drop=True)


def calc_electrical_distance(graph: nx.Graph, source_bus: int) -> pd.DataFrame:
    """
    使用边权 z_ohm 计算从 source_bus 到各节点的累计电气距离。
    """
    distances = nx.single_source_dijkstra_path_length(graph, source_bus, weight="z_ohm")

    rows = [{"mp_bus": int(bus), "electrical_distance": float(dist)} for bus, dist in distances.items()]
    return pd.DataFrame(rows).sort_values("mp_bus").reset_index(drop=True)


def build_distance_dataframe(net, source_bus: int) -> pd.DataFrame:
    """
    生成 source_bus 到各节点的拓扑距离与电气距离表。
    """
    graph = build_graph_from_net(net)
    topo_df = calc_topological_distance(graph, source_bus)
    elec_df = calc_electrical_distance(graph, source_bus)

    return topo_df.merge(elec_df, on="mp_bus", how="outer").sort_values("mp_bus").reset_index(drop=True)


def merge_distance_with_delta(distance_df: pd.DataFrame, delta_bus_df: pd.DataFrame) -> pd.DataFrame:
    """
    将距离信息与电压变化结果合并。
    """
    df = distance_df.merge(
        delta_bus_df[["mp_bus", "delta_vm_pu"]],
        on="mp_bus",
        how="left"
    )
    df["abs_delta_vm_pu"] = df["delta_vm_pu"].abs()
    return df.sort_values("mp_bus").reset_index(drop=True)