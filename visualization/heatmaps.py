# visualization/heatmaps.py

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def _extract_bus_matrix_for_plot(matrix_df: pd.DataFrame) -> pd.DataFrame:
    """
    从灵敏度矩阵汇总表中提取 bus_* 数值列，构造成可画热力图的表。
    行索引 = scenario_id
    列 = bus_1, bus_2, ...
    """
    if matrix_df.empty:
        return pd.DataFrame()

    value_cols = [c for c in matrix_df.columns if c.startswith("bus_")]
    plot_df = matrix_df[["scenario_id"] + value_cols].copy()
    plot_df = plot_df.set_index("scenario_id")
    return plot_df


def plot_sensitivity_heatmap(
    matrix_df: pd.DataFrame,
    title: str,
    save_path: str | Path
) -> None:
    """
    使用 matplotlib 直接绘制热力图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    plot_df = _extract_bus_matrix_for_plot(matrix_df)
    if plot_df.empty:
        return

    plt.figure(figsize=(12, max(4, 0.35 * len(plot_df))))
    plt.imshow(plot_df.values, aspect="auto")
    plt.colorbar(label="灵敏度")

    plt.xticks(range(len(plot_df.columns)), plot_df.columns, rotation=90)
    plt.yticks(range(len(plot_df.index)), plot_df.index)
    plt.title(title)
    plt.xlabel("观测节点")
    plt.ylabel("场景")
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()


def plot_distance_vs_voltage_impact(
    distance_df: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path,
    x_col: str = "electrical_distance"
) -> None:
    """
    绘制距离与电压影响的关系图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = distance_df.sort_values(x_col)

    plt.figure(figsize=(8, 5))
    plt.scatter(df[x_col], df["abs_delta_vm_pu"])
    plt.xlabel(x_col)
    plt.ylabel("|Delta V| (p.u.)")
    plt.title(f"Distance vs Voltage Impact - {scenario_id}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()