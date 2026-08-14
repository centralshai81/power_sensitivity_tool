from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 支持中文的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def _plot_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str, save_path: str, top_n: int = 10) -> None:
    if df is None or df.empty:
        return
    plot_df = df.head(top_n).copy()
    plt.figure(figsize=(10, 6))
    plt.bar(plot_df[x_col].astype(str), plot_df[y_col].astype(float))
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_critical_bars(critical_nodes: pd.DataFrame, critical_lines: pd.DataFrame, output_dir: str) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _plot_bar(critical_nodes, "bus_pp_idx", "total_score", "关键节点综合得分 Top10", str(output / "critical_nodes_top10.png"))
    _plot_bar(critical_lines, "line_pp_idx", "line_score", "关键线路综合得分 Top10", str(output / "critical_lines_top10.png"))
