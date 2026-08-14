# visualization/network_graph_plots.py

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np


def build_radial_layout(graph: nx.Graph, root: int = 1) -> Dict[int, Tuple[float, float]]:
    """
    为辐射型配电网构造一个较稳定的层次布局。
    """
    # BFS 层级
    levels = nx.single_source_shortest_path_length(graph, root)

    by_level = {}
    for node, lv in levels.items():
        by_level.setdefault(lv, []).append(node)

    pos = {}
    max_width = max(len(v) for v in by_level.values()) if by_level else 1

    for lv, nodes in sorted(by_level.items()):
        nodes = sorted(nodes)
        width = len(nodes)
        for i, node in enumerate(nodes):
            x = i - (width - 1) / 2
            y = -lv
            pos[node] = (x, y)

    return pos


def build_graph_from_net_for_plot(net) -> nx.Graph:
    """
    从 pandapower 网络构造绘图用 graph，节点标签为 mp_bus。
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
        g.add_edge(
            bus_lookup[from_pp],
            bus_lookup[to_pp],
            line_id=int(line_id)
        )

    return g


def plot_voltage_colored_network(
    net,
    delta_bus_df: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path,
    root_bus: int = 1
) -> None:
    """
    绘制节点按电压变化着色的网络拓扑图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    graph = build_graph_from_net_for_plot(net)
    pos = build_radial_layout(graph, root=root_bus)

    value_map = dict(zip(delta_bus_df["mp_bus"].astype(int), delta_bus_df["delta_vm_pu"]))
    node_values = [value_map.get(node, 0.0) for node in graph.nodes()]

    plt.figure(figsize=(12, 7))
    edges = nx.draw_networkx_edges(graph, pos, width=1.5)
    nodes = nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_values,
        cmap="coolwarm",
        node_size=550
    )
    nx.draw_networkx_labels(graph, pos, font_size=8)

    plt.colorbar(nodes, label="Delta Voltage (p.u.)")
    plt.title(f"Voltage Impact Network Map - {scenario_id}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()


def plot_line_colored_network(
    net,
    delta_line_df: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path,
    root_bus: int = 1,
    value_col: str = "delta_p_from_mw"
) -> None:
    """
    绘制线路按潮流变化着色的网络拓扑图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    graph = build_graph_from_net_for_plot(net)
    pos = build_radial_layout(graph, root=root_bus)

    line_value_map = dict(zip(delta_line_df["line_id"].astype(int), delta_line_df[value_col]))

    edge_values = []
    for u, v, data in graph.edges(data=True):
        lid = data.get("line_id")
        edge_values.append(line_value_map.get(lid, 0.0))

    plt.figure(figsize=(12, 7))
    ec = nx.draw_networkx_edges(
        graph,
        pos,
        edge_color=edge_values,
        edge_cmap=plt.cm.viridis,
        width=3
    )
    nx.draw_networkx_nodes(graph, pos, node_color="lightgray", node_size=500)
    nx.draw_networkx_labels(graph, pos, font_size=8)

    plt.colorbar(ec, label=value_col)
    plt.title(f"线路潮流影响网络拓扑图 - {scenario_id}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()